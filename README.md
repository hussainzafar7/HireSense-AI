# HireSense AI

AI-powered virtual recruitment and interview evaluation system built with Flask, Streamlit, scikit-learn, sentence-transformers, and SQLite.

## Setup

```bash
bash setup.sh
```

If Bash is unavailable on Windows, run the commands inside `setup.sh` manually from PowerShell after activating `venv`.

## Run

```bash
bash run.sh
```

Then open Streamlit at http://localhost:8501 and API health at http://localhost:5000/api/health.

## Tests

```bash
python -m pytest tests/ -v
```
