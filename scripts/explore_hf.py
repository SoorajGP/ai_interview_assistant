"""
Explore Hugging Face interview datasets to check schema and content.
"""
import sys
from datasets import load_dataset

datasets_to_try = [
    ("Aiman1234/Interview-questions", None),
    ("K-areem/AI-Interview-Questions", None),
    ("Shreyash23/interview", None),
    ("ali-alkhars/interviews", None),
]

for name, split in datasets_to_try:
    try:
        try_split = split or "train"
        ds = load_dataset(name, split=try_split)
        print(f"\n{'='*60}")
        print(f"Dataset : {name}")
        print(f"Rows    : {len(ds)}")
        print(f"Columns : {list(ds.features.keys())}")
        print(f"--- Sample row ---")
        row = dict(ds[0])
        for k, v in row.items():
            print(f"  {k!r}: {str(v)[:150]}")
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"Dataset : {name}  -> FAILED: {type(e).__name__}: {str(e)[:200]}")
