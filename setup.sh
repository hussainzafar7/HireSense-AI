#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "=== HireSense AI Setup ==="
python -m venv venv
if [ -f venv/Scripts/activate ]; then
  source venv/Scripts/activate
else
  source venv/bin/activate
fi
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm || true
python -m nltk.downloader punkt stopwords wordnet || true
python training/download_data.py
python training/preprocess.py
python training/train_evaluator.py
python training/train_resume_scorer.py
python training/evaluate_models.py
echo "=== Setup complete. Run: ./run.sh ==="
