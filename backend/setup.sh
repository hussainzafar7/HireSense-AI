#!/bin/bash
set -e
echo "=== HireSense AI Backend Setup ==="
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
mkdir -p data uploads/resumes uploads/audio ml/models_cache
python ml/train_models.py
python -c "from app import create_app; app = create_app()"
echo "Backend setup complete."
