"""
FastAPI wrapper for the Adaptive AI Interview Assistant.
Exposes the core interview state machine over HTTP so the Next.js frontend
can interact with it asynchronously.

Start with:
    uvicorn api:app --reload --host 0.0.0.0 --port 8000
"""

import re
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ── Import core logic from the existing CLI module ──────────────────────────
# app.py is already importable as-is — model/tokenizer/df load once at module
# level, which is exactly what we need for a shared-memory FastAPI process.
from app import evaluate_answer, df, PHASE_LIMITS, PASS_THRESHOLD

# ── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Interview Assistant API",
    description="Adaptive LLM-powered technical interview system.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory session store ───────────────────────────────────────────────────
# Each session is a dict keyed by a UUID string.
# NOTE: This is single-process state — a server restart clears all sessions.
SESSIONS: dict[str, dict] = {}

# ── Shared normalization regex (mirrors app.py) ──────────────────────────────
_PREFIX_RE = re.compile(
    r'^(Candidate prompt|Could you explain this|Define and explain'
    r'|Interview Question|Please answer the following)\s*:\s*',
    re.IGNORECASE,
)

def _normalize(q: str) -> str:
    return _PREFIX_RE.sub('', q.strip()).strip().lower()


# ── Helpers ───────────────────────────────────────────────────────────────────
def _get_next_question(session: dict) -> Optional[dict]:
    """
    Sample the next unseen question matching the current difficulty.
    Returns a dict with question data or None if no questions remain.
    """
    domain_df = df[df['Domain'] == session["domain"]]
    difficulty = session["difficulty"]

    available = domain_df[
        (domain_df['Difficulty_Level'].str.lower() == difficulty.lower())
        & (~domain_df['ID'].isin(session["asked_ids"]))
        & (~domain_df['Question'].apply(_normalize).isin(session["asked_texts"]))
    ]

    if available.empty:
        return None

    row = available.sample(1).iloc[0]
    raw_q = row['Question'].strip()
    question_text = _PREFIX_RE.sub('', raw_q).strip()

    return {
        "id": int(row['ID']),
        "question": question_text,
        "raw_question": raw_q,
        "reference_answer": str(row['Reference_Answer']),
    }


def _compute_verdict(percentage: float) -> str:
    if percentage >= 80:
        return "STRONG HIRE"
    elif percentage >= 60:
        return "LEANING HIRE"
    else:
        return "NO HIRE"


def _advance_phase(session: dict) -> dict:
    """
    Handles phase transitions. Returns a status dict:
      { "advanced": bool, "finished": bool, "reason": str }
    """
    difficulty = session["difficulty"]
    phase_asked = session["phase_asked"]

    if phase_asked < PHASE_LIMITS[difficulty]:
        return {"advanced": False, "finished": False, "reason": ""}

    phase_avg = session["phase_score"] / (phase_asked * 10) if phase_asked else 0

    if difficulty == "Easy":
        session["difficulty"] = "Medium"
        session["phase_asked"] = 0
        session["phase_score"] = 0
        return {"advanced": True, "finished": False, "reason": "Easy round complete. Advancing to Medium."}

    elif difficulty == "Medium":
        if phase_avg >= PASS_THRESHOLD:
            session["difficulty"] = "Hard"
            session["phase_asked"] = 0
            session["phase_score"] = 0
            return {"advanced": True, "finished": False, "reason": f"Medium round complete ({phase_avg*100:.0f}%). Advancing to Hard."}
        else:
            session["is_complete"] = True
            percentage = (session["total_score"] / session["total_possible"] * 100) if session["total_possible"] else 0
            session["verdict"] = _compute_verdict(percentage)
            return {
                "advanced": False,
                "finished": True,
                "reason": f"Medium round complete ({phase_avg*100:.0f}%). Below threshold ({PASS_THRESHOLD*100:.0f}%). Interview concluded.",
            }

    else:  # Hard
        session["is_complete"] = True
        percentage = (session["total_score"] / session["total_possible"] * 100) if session["total_possible"] else 0
        session["verdict"] = _compute_verdict(percentage)
        return {"advanced": False, "finished": True, "reason": "Hard round complete. Interview finished!"}


# ── Pydantic models ───────────────────────────────────────────────────────────
class StartRequest(BaseModel):
    domain: str

class SubmitRequest(BaseModel):
    session_id: str
    user_answer: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/api/domains")
def get_domains():
    """Returns the sorted list of available interview domains."""
    domains = sorted(df['Domain'].dropna().unique().tolist())
    return {"domains": domains}


@app.post("/api/session/start")
def start_session(body: StartRequest):
    """
    Starts a new interview session.
    Returns the session ID and the first question.
    """
    domains = df['Domain'].dropna().unique().tolist()
    if body.domain not in domains:
        raise HTTPException(status_code=400, detail=f"Domain '{body.domain}' not found.")

    session_id = str(uuid.uuid4())
    session: dict = {
        "domain": body.domain,
        "difficulty": "Easy",
        "phase_asked": 0,
        "phase_score": 0,
        "total_score": 0,
        "total_possible": 0,
        "asked_ids": set(),
        "asked_texts": set(),
        "lost_marks": [],
        "history": [],
        "is_complete": False,
        "verdict": None,
        # Pending evaluation: the current question awaiting answer
        "_pending": None,
    }

    q = _get_next_question(session)
    if q is None:
        raise HTTPException(status_code=422, detail=f"No questions available for domain '{body.domain}'.")

    # Register this question as pending
    session["_pending"] = q
    session["asked_ids"].add(q["id"])
    session["asked_texts"].add(_normalize(q["raw_question"]))

    SESSIONS[session_id] = session

    return {
        "session_id": session_id,
        "domain": body.domain,
        "difficulty": session["difficulty"],
        "question": q["question"],
        "q_num": session["phase_asked"] + 1,
        "phase_total": PHASE_LIMITS[session["difficulty"]],
        "is_complete": False,
    }


@app.post("/api/session/submit")
def submit_answer(body: SubmitRequest):
    """
    Submits a user answer for the current pending question.
    Returns score, feedback, and the next question (or wrap-up data if done).
    """
    session = SESSIONS.get(body.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found. Please start a new session.")

    if session["is_complete"]:
        raise HTTPException(status_code=409, detail="This interview session is already complete.")

    pending = session.get("_pending")
    if pending is None:
        raise HTTPException(status_code=409, detail="No pending question for this session.")

    # ── Evaluate ─────────────────────────────────────────────────────────────
    score, feedback = evaluate_answer(
        pending["question"],
        pending["reference_answer"],
        body.user_answer,
        max_marks=10,
    )

    marks_lost = 10 - score
    session["total_score"] += score
    session["total_possible"] += 10
    session["phase_score"] += score
    session["phase_asked"] += 1
    session["_pending"] = None

    if marks_lost > 0:
        session["lost_marks"].append({
            "question": pending["question"],
            "score": score,
            "lost": marks_lost,
            "difficulty": session["difficulty"],
        })

    session["history"].append({
        "question": pending["question"],
        "user_answer": body.user_answer,
        "score": score,
        "feedback": feedback,
        "difficulty": session["difficulty"],
    })

    # ── Phase advancement ─────────────────────────────────────────────────────
    phase_result = _advance_phase(session)

    # If interview is over, return wrap-up data
    if session["is_complete"]:
        total = session["total_score"]
        possible = session["total_possible"]
        pct = (total / possible * 100) if possible else 0
        return {
            "score": score,
            "feedback": feedback,
            "is_complete": True,
            "verdict": session["verdict"],
            "total_score": total,
            "total_possible": possible,
            "percentage": round(pct, 1),
            "history": session["history"],
            "lost_marks": session["lost_marks"],
            "phase_message": phase_result["reason"],
            # next_question is None when complete
            "next_question": None,
            "difficulty": session["difficulty"],
            "q_num": None,
            "phase_total": None,
        }

    # ── Get next question ─────────────────────────────────────────────────────
    # Keep polling for next question (handle empty-pool phase skips)
    next_q = None
    max_phase_skips = 3
    for _ in range(max_phase_skips):
        next_q = _get_next_question(session)
        if next_q is not None:
            break
        # No questions left in this phase — force advance
        session["phase_asked"] = PHASE_LIMITS[session["difficulty"]]
        phase_result = _advance_phase(session)
        if session["is_complete"]:
            break

    if session["is_complete"]:
        total = session["total_score"]
        possible = session["total_possible"]
        pct = (total / possible * 100) if possible else 0
        return {
            "score": score,
            "feedback": feedback,
            "is_complete": True,
            "verdict": session["verdict"],
            "total_score": total,
            "total_possible": possible,
            "percentage": round(pct, 1),
            "history": session["history"],
            "lost_marks": session["lost_marks"],
            "phase_message": phase_result["reason"],
            "next_question": None,
            "difficulty": session["difficulty"],
            "q_num": None,
            "phase_total": None,
        }

    # Register new pending question
    session["_pending"] = next_q
    session["asked_ids"].add(next_q["id"])
    session["asked_texts"].add(_normalize(next_q["raw_question"]))

    return {
        "score": score,
        "feedback": feedback,
        "is_complete": False,
        "verdict": None,
        "total_score": session["total_score"],
        "total_possible": session["total_possible"],
        "percentage": None,
        "history": None,
        "lost_marks": None,
        "phase_message": phase_result.get("reason", ""),
        "next_question": next_q["question"],
        "difficulty": session["difficulty"],
        "q_num": session["phase_asked"] + 1,
        "phase_total": PHASE_LIMITS[session["difficulty"]],
    }


@app.get("/api/session/status/{session_id}")
def session_status(session_id: str):
    """Returns a snapshot of the current session state (for reconnection)."""
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    pending = session.get("_pending")
    return {
        "session_id": session_id,
        "domain": session["domain"],
        "difficulty": session["difficulty"],
        "q_num": session["phase_asked"] + 1,
        "phase_total": PHASE_LIMITS[session["difficulty"]],
        "total_score": session["total_score"],
        "total_possible": session["total_possible"],
        "is_complete": session["is_complete"],
        "verdict": session["verdict"],
        "current_question": pending["question"] if pending else None,
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "model": "Qwen1.5-1.8B+PEFT", "sessions_active": len(SESSIONS)}
