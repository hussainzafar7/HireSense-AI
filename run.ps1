Write-Host "Starting HireSense AI..."
Write-Host ""

$Backend = Start-Process -NoNewWindow -FilePath "$PSScriptRoot\backend\venv\Scripts\python.exe" -ArgumentList "$PSScriptRoot\backend\app.py" -PassThru
Start-Sleep 3

$Frontend = Start-Process -NoNewWindow -FilePath "cmd.exe" -ArgumentList "/c cd /d `"$PSScriptRoot\frontend`" && npx vite --port 3000" -PassThru

Write-Host "==============================="
Write-Host "Frontend: http://localhost:3000"
Write-Host "API:      http://localhost:5000"
Write-Host "==============================="

Read-Host "Press Enter to stop servers"

Stop-Process -Id $Backend.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $Frontend.Id -Force -ErrorAction SilentlyContinue
Write-Host "Servers stopped."
