@echo off
echo ==========================================
echo   Tebita SLA System - First Run Setup
echo ==========================================

:: Check for Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.12+ and try again.
    pause
    exit /b
)

:: Check for Node
call npm --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo Please install Node.js 18+ and try again.
    pause
    exit /b
)

:: 1. Backend Setup
echo.
echo [1/2] Setting up Backend...
cd backend

:: Create venv if missing
IF NOT EXIST ".venv" (
    echo    - Creating virtual environment...
    python -m venv .venv
)

:: Activate venv
call .venv\Scripts\activate

:: Install dependencies
echo    - Installing Python dependencies...
pip install -r requirements.txt

:: Create .env if missing
IF NOT EXIST ".env" (
    echo    - Creating .env file...
    echo DATABASE_URL=sqlite:///./tebita.db > .env
    echo APP_SECRET_KEY=secret >> .env
)

:: Create Admin User
echo    - Initializing database and admin user...
python create_admin.py

:: Start Backend in new window (Explicitly activate venv again to be safe)
echo    - Starting Backend Server...
start "Tebita Backend" cmd /k "call .venv\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

:: 2. Frontend Setup
echo.
echo [2/2] Setting up Frontend...
cd ..\frontend

:: Install node_modules if missing
IF NOT EXIST "node_modules" (
    echo    - Installing Node dependencies (this may take a while)...
    call npm install
)

:: Start Frontend in new window
echo    - Starting Frontend Server...
start "Tebita Frontend" cmd /k "npm run dev -- --host 0.0.0.0"

echo.
echo ==========================================
echo   Application Started!
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo ==========================================
echo   DO NOT CLOSE THIS WINDOW
pause
