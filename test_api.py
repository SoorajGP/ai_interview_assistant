"""
Smoke test for the AI Interview Assistant FastAPI backend.
Verifies the 3 core endpoints WITHOUT loading the LLM model.

Run with:
    python test_api.py

NOTE: The FastAPI server must be running on localhost:8000.
"""

import sys
import requests

BASE = "http://localhost:8000"

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"

errors = 0

def check(label, cond, detail=""):
    global errors
    if cond:
        print(f"  {PASS} {label}")
    else:
        print(f"  {FAIL} {label}" + (f" — {detail}" if detail else ""))
        errors += 1

print("\n=== AI Interview Assistant — API Smoke Tests ===\n")

# ── 1. Health check ─────────────────────────────────────────────────────────
print("[1] Health endpoint")
try:
    r = requests.get(f"{BASE}/api/health", timeout=5)
    check("Status 200", r.status_code == 200, r.text)
    data = r.json()
    check("status == 'ok'", data.get("status") == "ok")
    print(f"     Model: {data.get('model', 'N/A')}")
except Exception as e:
    check("Server reachable", False, str(e))
    print("\n  → Is the FastAPI server running?  uvicorn api:app --port 8000")
    sys.exit(1)

# ── 2. GET /api/domains ──────────────────────────────────────────────────────
print("\n[2] GET /api/domains")
r = requests.get(f"{BASE}/api/domains", timeout=5)
check("Status 200", r.status_code == 200, r.text)
domains = r.json().get("domains", [])
check("Returns non-empty list", len(domains) > 0, f"Got: {domains}")
check("All domains are strings", all(isinstance(d, str) for d in domains))
print(f"     Domains ({len(domains)}): {', '.join(domains[:4])}{'…' if len(domains) > 4 else ''}")

# ── 3. POST /api/session/start ───────────────────────────────────────────────
print("\n[3] POST /api/session/start")
first_domain = domains[0]
r = requests.post(
    f"{BASE}/api/session/start",
    json={"domain": first_domain},
    timeout=10,
)
check("Status 200", r.status_code == 200, r.text)
session_data = r.json()
sid = session_data.get("session_id", "")
check("Returns session_id", bool(sid))
check("Returns question", bool(session_data.get("question")))
check("difficulty == 'Easy'", session_data.get("difficulty") == "Easy",
      f"Got: {session_data.get('difficulty')}")
check("q_num == 1", session_data.get("q_num") == 1)
check("phase_total == 5", session_data.get("phase_total") == 5)
print(f"     Session: {sid[:18]}…")
print(f"     Q:  {session_data.get('question', '')[:80]}…")

# ── 4. POST /api/session/submit — "I don't know" fast path ──────────────────
print('\n[4] POST /api/session/submit ("I don\'t know" — no model call)')
r = requests.post(
    f"{BASE}/api/session/submit",
    json={"session_id": sid, "user_answer": "I don't know"},
    timeout=10,
)
check("Status 200", r.status_code == 200, r.text)
result = r.json()
check("score == 0", result.get("score") == 0, f"Got: {result.get('score')}")
check("is_complete == False", result.get("is_complete") == False)
check("Returns next_question", bool(result.get("next_question")))
check("Returns feedback text", bool(result.get("feedback")))

# ── 5. Invalid domain ────────────────────────────────────────────────────────
print("\n[5] POST /api/session/start — invalid domain")
r = requests.post(
    f"{BASE}/api/session/start",
    json={"domain": "INVALID_DOMAIN_XYZ"},
    timeout=5,
)
check("Status 400", r.status_code == 400, f"Got: {r.status_code}")

# ── 6. GET /api/session/status ───────────────────────────────────────────────
print("\n[6] GET /api/session/status")
r = requests.get(f"{BASE}/api/session/status/{sid}", timeout=5)
check("Status 200", r.status_code == 200, r.text)
status_data = r.json()
check("domain matches", status_data.get("domain") == first_domain)
check("is_complete == False", status_data.get("is_complete") == False)

# ── Summary ──────────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
if errors == 0:
    print("\033[92m  ALL TESTS PASSED\033[0m")
else:
    print(f"\033[91m  {errors} TEST(S) FAILED\033[0m")
print(f"{'='*50}\n")
sys.exit(errors)
