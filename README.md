# IDP3 – Adaptive LLM Interview System

An adaptive technical interview assistant powered by a LoRA fine-tuned **Qwen/Qwen1.5-1.8B** model. It asks questions from a curated dataset, scores your answers using the local LLM, and dynamically adjusts difficulty based on performance.

---

## Project Structure

```
IDP3/
├── data/
│   └── LLM_Interview_Dataset-v2.csv   # Question bank
├── models/
│   └── fine_tuned_interviewer/        # LoRA adapter weights (PEFT 0.20.0)
├── notebooks/
│   └── training_notebook.ipynb        # Colab fine-tuning notebook
├── app.py                             # Main CLI application
├── requirements.txt                   # Python dependencies
├── setup.bat                          # One-click Windows setup script
└── .gitignore
```

---

## Quick Start (Windows)

### Option A – Automated Setup
```bat
setup.bat
```
This creates a virtual environment, installs all dependencies, and prints run instructions.

### Option B – Manual Setup
```powershell
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the interview system
python app.py
```

---

## How It Works

1. **Model** – Loads `Qwen/Qwen1.5-1.8B` (downloaded from HuggingFace on first run) then applies the local LoRA adapter from `models/fine_tuned_interviewer/`.
2. **Dataset** – Reads `data/LLM_Interview_Dataset-v2.csv` which contains questions tagged by Domain and Difficulty (Easy / Hard).
3. **Session Flow**:
   - You pick a domain.
   - The system starts at **Easy** difficulty.
   - Answer 5 Easy questions scoring ≥ 8/10 in a row → difficulty shifts to **Hard**.
   - At the end, you get a full session report with marks lost per question.

---

## Requirements

- Python 3.9+
- ~4 GB disk space (Qwen1.5-1.8B base model downloaded from HuggingFace on first run)
- CPU is sufficient (no GPU required)

---

## Dependencies

See [`requirements.txt`](./requirements.txt). Key packages:

| Package | Purpose |
|---|---|
| `torch` | Model inference |
| `transformers` | Load Qwen1.5-1.8B |
| `peft` | Load LoRA adapter |
| `pandas` | Read question dataset |
| `accelerate` | Device mapping |
