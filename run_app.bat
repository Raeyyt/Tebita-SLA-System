@echo off
echo ==========================================
echo   Tebita SLA System - One-Click Start
echo ==========================================

cd backend
echo Checking for UV...
python -m uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing UV...
    pip install uv
)

echo Syncing dependencies with UV...
call python -m uv sync

if not exist .env (
    echo Creating .env file for SQLite...
    echo DATABASE_URL=sqlite:///./tebita.db > .env
    echo APP_SECRET_KEY=tebita-secret-key-123 >> .env
    echo REDIS_URL=redis://localhost:6379/0 >> .env
)

echo Initializing Database...
call python -m uv run python init_db.py

echo Starting Backend Server...
start "Tebita Backend" python -m uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

cd ..\frontend
echo Installing Frontend dependencies...
call npm install

echo Starting Frontend Server...
start http://localhost:5173
npm run dev -- --port 5173

pause
