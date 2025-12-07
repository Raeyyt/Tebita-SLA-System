# Tebita SLA System - Backend

## Setup

1. Create virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL database:
```bash
# Create database
createdb tebita_sla
```

4. Create `.env` file:
```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/tebita_sla
APP_SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379/0
```

5. Run the server:
```bash
python -m uvicorn app.main:app --reload --port 8000
```

## API Documentation

Once running, visit: http://localhost:8000/docs
