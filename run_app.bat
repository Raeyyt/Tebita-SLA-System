@echo off
echo ==========================================
echo   Tebita SLA System - One-Click Start
echo ==========================================

echo Stopping existing processes...
taskkill /F /IM uvicorn.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1

cd backend
echo Starting Backend Server (Port 8000)...
start "Tebita Backend" python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

cd ..\frontend
echo Starting Frontend Server (Port 5173)...
start http://localhost:5173
npm run dev -- --port 5173 --host

pause
