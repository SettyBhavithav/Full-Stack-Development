# ============================================================
#  DevVerse AI - One-Click Launcher
# ============================================================
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host ""
Write-Host "  DevVerse AI - One-Click Launcher" -ForegroundColor Cyan
Write-Host ""

# -- 1. Docker (MySQL + Redis) --------------------------------
Write-Host "[1/5] Starting MySQL + Redis (Docker)..." -ForegroundColor Yellow
Set-Location "$Root\docker"
docker compose up -d | Out-Null
Set-Location $Root
Write-Host "      Waiting 10s for database to initialise..." -ForegroundColor DarkGray
Start-Sleep -Seconds 10
Write-Host "      Databases ready!" -ForegroundColor Green

# -- 2. Node.js Backend (port 5000) --------------------------
Write-Host "[2/5] Starting Node.js Backend  -> http://localhost:5000" -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$Root\backend'; if (!(Test-Path node_modules)) { npm install }; node server.js"
)

# -- 3. Background Worker ------------------------------------
Write-Host "[3/5] Starting Background Worker..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$Root\workers'; node queue_worker.js"
)

# -- 4. Python AI Service (port 5001) ------------------------
Write-Host "[4/5] Starting Python AI Service -> http://localhost:5001" -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$Root\python-services'; .\venv\Scripts\activate; python app.py"
)

# -- 5. Frontend HTTP Server (port 8080) ---------------------
Write-Host "[5/5] Starting Frontend Server   -> http://localhost:8080" -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$Root\frontend'; python -m http.server 8080"
)

# -- Open browser after short delay --------------------------
Write-Host ""
Write-Host "  Opening DevVerse AI in your browser in 4 seconds..." -ForegroundColor Cyan
Start-Sleep -Seconds 4
Start-Process "http://localhost:8080/index.html"

Write-Host ""
Write-Host "  ==========================================" -ForegroundColor Green
Write-Host "   DevVerse AI is fully running!" -ForegroundColor Green
Write-Host "   Frontend  : http://localhost:8080" -ForegroundColor White
Write-Host "   Backend   : http://localhost:5000" -ForegroundColor White
Write-Host "   Python AI : http://localhost:5001" -ForegroundColor White
Write-Host "  ==========================================" -ForegroundColor Green
Write-Host ""
