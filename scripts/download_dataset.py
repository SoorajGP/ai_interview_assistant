"""
download_dataset.py
-------------------
Downloads real interview Q&A from Hugging Face and converts them into the
LLM_Interview_Dataset-v2.csv schema used by app.py:

  ID | Domain | Difficulty_Level | Question | Reference_Answer

Sources used:
  1. Aiman1234/Interview-questions  (496 rows – Java/CS Q&A, has difficulty labels)
  2. K-areem/AI-Interview-Questions (4653 rows – AI/ML Q&A, [INST] format parsed)
  3. Shreyash23/interview           (523 rows – ML question-only, filtered where answer is present)
  4. Original LLM_Interview_Dataset-v2.csv kept and merged at the end

Run:
    python scripts/download_dataset.py
"""

import re
import warnings
import pandas as pd
from datasets import load_dataset

warnings.filterwarnings("ignore")

# -- Domain keyword mapping ----------------------------------------------------
# Used to auto-assign domain for datasets that lack one
_DOMAIN_KEYWORDS = {
    "AI/ML": [
        "machine learning", "deep learning", "neural network", "gradient",
        "overfitting", "regularization", "knn", "svm", "random forest",
        "cnn", "rnn", "lstm", "transformer", "backpropagation", "epoch",
        "batch", "loss function", "uml", "nlp", "bert", "gpt", "embedding",
        "clustering", "regression", "classification", "decision tree",
        "reinforcement", "unsupervised", "supervised", "xgboost",
    ],
    "Data Structures & Algorithms": [
        "array", "linked list", "stack", "queue", "tree", "binary",
        "graph", "hash", "sorting", "searching", "dynamic programming",
        "recursion", "big o", "complexity", "bfs", "dfs", "heap",
        "trie", "avl", "red-black", "huffman", "fibonacci", "palindrome",
        "two pointer", "sliding window", "greedy", "backtracking",
    ],
    "Core CS & OS": [
        "operating system", "process", "thread", "deadlock", "memory",
        "virtual", "paging", "segmentation", "cpu", "scheduling",
        "synchronization", "mutex", "semaphore", "network", "tcp", "udp",
        "http", "socket", "compiler", "interpreter", "java", "python",
        "c++", "pointer", "garbage", "oop", "inheritance", "polymorphism",
        "encapsulation", "abstraction", "multithreading", "concurrency",
    ],
    "Behavioral": [
        "teamwork", "conflict", "leadership", "challenge", "weakness",
        "strength", "motivation", "collaborate", "deadline", "feedback",
        "communication", "goal", "ambiguous", "failure", "success",
        "hire", "tell me about", "example of",
    ],
}

DIFFICULTY_MAP = {
    "easy": "Easy", "medium": "Medium", "hard": "Hard",
    "beginner": "Easy", "intermediate": "Medium", "advanced": "Hard",
    "junior": "Easy", "senior": "Hard",
}


def infer_domain(text: str) [+] str:
    t = text.lower()
    scores = {d: sum(1 for kw in kws if kw in t) for d, kws in _DOMAIN_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Core CS & OS"


def infer_difficulty(text: str) [+] str:
    t = text.lower().strip()
    return DIFFICULTY_MAP.get(t, "Medium")


# -- Source 1: Aiman1234/Interview-questions -----------------------------------
print("Loading Aiman1234/Interview-questions …")
ds1 = load_dataset("Aiman1234/Interview-questions", split="train")
rows1 = []
for row in ds1:
    q = str(row.get("Questions", "")).strip()
    a = str(row.get("Answers", "")).strip()
    lvl = str(row.get(" level ", "Medium")).strip()
    lang = str(row.get("language", "")).strip()

    if not q or q.lower() in ("none", "nan") or not a or a.lower() in ("none", "nan"):
        continue

    domain = infer_domain(q + " " + lang)
    difficulty = infer_difficulty(lvl)
    rows1.append({"Question": q, "Reference_Answer": a, "Domain": domain, "Difficulty_Level": difficulty})

print("  [+] {len(rows1)} usable rows")

# -- Source 2: K-areem/AI-Interview-Questions ----------------------------------
# Format: "<s>[INST] Question [/INST] Answer </s>"
print("Loading K-areem/AI-Interview-Questions …")
ds2 = load_dataset("K-areem/AI-Interview-Questions", split="train")
_INST_RE = re.compile(r"\[INST\](.*?)\[/INST\](.*)", re.DOTALL)
rows2 = []
for row in ds2:
    text = str(row.get("text", ""))
    m = _INST_RE.search(text)
    if not m:
        continue
    q = m.group(1).strip().lstrip("<s>").strip()
    a = m.group(2).strip().rstrip("</s>").strip()
    if not q or not a or len(a) < 20:
        continue
    domain = infer_domain(q)
    rows2.append({"Question": q, "Reference_Answer": a, "Domain": domain, "Difficulty_Level": "Medium"})

print(f"  → {len(rows2)} usable rows")

# -- Source 3: Shreyash23/interview ---------------------------------------------
# "output" column is the question — skip if no answer present
print("Loading Shreyash23/interview …")
ds3 = load_dataset("Shreyash23/interview", split="train")
rows3 = []
for row in ds3:
    q = str(row.get("output", "")).strip()
    a = str(row.get("input", "")).strip()   # sometimes has hints
    if not q or q.lower() in ("none", "nan"):
        continue
    # This dataset has questions only; use a placeholder answer for diversity
    # Skip rows with no meaningful answer context
    if not a or a.lower() in ("none", "nan", ""):
        continue
    domain = infer_domain(q)
    rows3.append({"Question": q, "Reference_Answer": a, "Domain": domain, "Difficulty_Level": "Medium"})

print(f"  → {len(rows3)} usable rows (those with answer hints)")

# -- Merge & Deduplicate --------------------------------------------------------
print("\nMerging sources …")
df_new = pd.DataFrame(rows1 + rows2 + rows3)

# Load original dataset and keep it
df_orig = pd.read_csv("./data/LLM_Interview_Dataset-v2.csv")
print(f"  Original dataset: {len(df_orig)} rows")

# Normalise question text for dedup
def norm(q):
    return re.sub(r"\s+", " ", str(q).strip().lower())

df_orig["_norm"] = df_orig["Question"].apply(norm)
df_new["_norm"]  = df_new["Question"].apply(norm)

# Remove new rows whose normalised question already exists in original
existing_norms = set(df_orig["_norm"])
df_new = df_new[~df_new["_norm"].isin(existing_norms)].copy()

# Internal dedup within new rows
df_new = df_new.drop_duplicates(subset="_norm")

print(f"  New unique rows after dedup: {len(df_new)}")

# Assign IDs continuing from the original
start_id = df_orig["ID"].max() + 1
df_new = df_new.reset_index(drop=True)
df_new["ID"] = range(int(start_id), int(start_id) + len(df_new))

# Drop helper column and concat
df_orig = df_orig.drop(columns=["_norm"], errors="ignore")
df_new  = df_new.drop(columns=["_norm"])

df_final = pd.concat(
    [df_orig[["ID", "Domain", "Difficulty_Level", "Question", "Reference_Answer"]],
     df_new[["ID", "Domain", "Difficulty_Level", "Question", "Reference_Answer"]]],
    ignore_index=True
)

# Save
out_path = "./data/LLM_Interview_Dataset-v2.csv"
df_final.to_csv(out_path, index=False)
print(f"\nSaved {len(df_final)} total rows → {out_path}")

# -- Summary -------------------------------------------------------------------
print("\n-- Unique questions per Domain / Difficulty --")
import re as _re
PREFIX_RE = _re.compile(
    r"^(Candidate prompt|Could you explain this|Define and explain"
    r"|Interview Question|Please answer the following)\s*:\s*",
    _re.IGNORECASE
)
df_final["Core"] = df_final["Question"].apply(
    lambda q: PREFIX_RE.sub("", str(q).strip()).strip().lower()
)
g = df_final.groupby(["Domain", "Difficulty_Level"])["Core"].nunique().reset_index()
for _, r in g.iterrows():
    print(f"  {r['Domain']:<38} {r['Difficulty_Level']:<8} {r['Core']:>4} unique questions")
