# Quick Start Guide - Tebita SLA System (SQLite Version)

## Prerequisites
- Python 3.12+
- Node.js 18+

## 🚀 The Easiest Way (One-Click)

1. Double-click `run_app.bat`
2. That's it! It will set up everything and start the app.

## Manual Setup (SQLite)

### 1. Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
echo "DATABASE_URL=sqlite:///./tebita.db" > .env
echo "APP_SECRET_KEY=secret" >> .env

# Initialize DB
python init_db.py

# Run Server
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

## Access
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## Default Login
- **Admin**: admin / admin123
- **M&E Staff**: me_staff / me123
