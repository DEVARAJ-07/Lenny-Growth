# ==============================================================================
# The Lenny Growth Assistant - Turnkey Startup Script
# Starts Ollama (port 11434), FastAPI Backend (port 8000), and Vite (port 5173)
# ==============================================================================

Write-Host "==> [1/3] Checking Local Ollama Daemon on port 11434..." -ForegroundColor Cyan
$ollamaUp = $false
try {
    $res = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($res) { $ollamaUp = $true }
} catch {}

if (-not $ollamaUp) {
    Write-Host "Starting Ollama daemon with models at D:\LLMs\ollama_store..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File scripts\start-ollama.ps1" -WindowStyle Minimized
    Start-Sleep -Seconds 3
} else {
    Write-Host "Ollama is active and running!" -ForegroundColor Green
}

Write-Host "==> [2/3] Checking FastAPI Backend on port 8000..." -ForegroundColor Cyan
$backendUp = $false
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($health) { $backendUp = $true }
} catch {}

if (-not $backendUp) {
    Write-Host "Starting FastAPI Backend Server on http://127.0.0.1:8000..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-Command & '.\.venv\Scripts\python.exe' -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000" -WindowStyle Minimized
    Start-Sleep -Seconds 2
} else {
    Write-Host "FastAPI Backend is active on port 8000!" -ForegroundColor Green
}

Write-Host "==> [3/3] Starting Vite Frontend on http://localhost:5173..." -ForegroundColor Cyan
Set-Location frontend
npm run dev
