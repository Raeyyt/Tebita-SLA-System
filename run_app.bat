@echo off
echo ==========================================
echo   Tebita SLA System - One-Click Start
echo ==========================================

cd backend
if not exist .venv (
    echo Creating Python virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

if not exist .env (
    echo Creating .env file for SQLite...
    echo DATABASE_URL=sqlite:///./tebita.db > .env
    echo APP_SECRET_KEY=tebita-secret-key-123 >> .env
    echo REDIS_URL=redis://localhost:6379/0 >> .env
)

echo Initializing Database...
python init_db.py

echo Starting Backend Server...
start "Tebita Backend" python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

cd ..\frontend
echo Installing Frontend dependencies...
call npm install

echo Starting Frontend Server...
start http://localhost:5173
npm run dev -- --port 5173

pause
