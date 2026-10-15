@echo off
title LocalPDF Suite
chcp 65001 > nul
echo ========================================================
echo        LocalPDF Suite — %%100 Yerel ^& Güvenli
echo ========================================================
echo.

cd /d "%~dp0"

IF NOT EXIST ".venv\Scripts\python.exe" (
    echo [BILGI] Sanal ortam bulunamadi, olusturuluyor...
    python -m venv .venv
    echo [BILGI] Bagimliliklar yukleniyor...
    .venv\Scripts\pip install -r backend\requirements.txt
)

echo [BILGI] Sunucu baslatiliyor (http://127.0.0.1:8000)...
start http://127.0.0.1:8000

cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
