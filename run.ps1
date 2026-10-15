# LocalPDF Suite — PowerShell Başlatıcı
$Host.UI.RawUI.WindowTitle = "LocalPDF Suite"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       LocalPDF Suite — %100 Yerel & Güvenli" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$pythonExe = Join-Path $scriptDir ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "[BILGI] Sanal ortam olusturuluyor..." -ForegroundColor Green
    python -m venv .venv
    Write-Host "[BILGI] Bagimliliklar kuruluyor..." -ForegroundColor Green
    & (Join-Path $scriptDir ".venv\Scripts\pip.exe") install -r backend\requirements.txt
}

Write-Host "[BILGI] Tarayici aciliyor: http://127.0.0.1:8000" -ForegroundColor Green
Start-Process "http://127.0.0.1:8000"

Set-Location (Join-Path $scriptDir "backend")
& $pythonExe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
