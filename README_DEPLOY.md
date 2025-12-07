# Deployment (Docker Compose)

This file explains how to run the Tebita SLA System using Docker Compose on a single host. It includes Postgres, Redis, backend, Celery worker, frontend build, and Nginx as a reverse proxy.

Prerequisites
- Docker & Docker Compose installed on the server
- At least 2-4 GB RAM (more for larger loads)

Quick start (from repo root)

1. Copy the example env file and edit values:
```powershell
cp backend/.env.example backend/.env
# edit backend/.env and replace secrets
```

2. Build and start the stack:
```powershell
docker compose up -d --build
```

3. Check logs:
```powershell
docker compose logs -f backend
```

Notes & next steps
- Run Alembic migrations before using the app in production. You can add a one-off service or run a container to apply migrations.
- Set up TLS with Let's Encrypt (recommended). Replace the Nginx config with one that includes TLS and certificate renewal.
- Configure scheduled backups for Postgres (e.g., periodic `pg_dump` to remote storage).
- Keep `.env` out of source control. Use a secrets manager for production.
