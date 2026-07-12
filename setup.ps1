Write-Host "=== HireSense AI Setup ==="

Write-Host "`n[1/5] Creating Python virtual environment..."
py -m venv backend\venv

Write-Host "[2/5] Installing Python dependencies..."
& "backend\venv\Scripts\python.exe" -m pip install --upgrade pip
& "backend\venv\Scripts\python.exe" -m pip install -r backend\requirements.txt

Write-Host "[3/5] Downloading spaCy model..."
& "backend\venv\Scripts\python.exe" -m spacy download en_core_web_sm

Write-Host "[4/5] Generating question bank and caching models..."
& "backend\venv\Scripts\python.exe" backend\ml\train_models.py

Write-Host "[5/5] Installing frontend dependencies..."
cd frontend
npm install
cd ..

Write-Host "`n=== Setup Complete ==="
Write-Host "Run '.\run.ps1' to start both servers."
