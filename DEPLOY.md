# Windows Server Deployment Guide

## Prerequisites
1.  **Windows Server 2019/2022**
2.  **Docker Desktop** (or Docker Engine with WSL 2) installed and running.
3.  **Git** (optional, for pulling code) or file transfer access.

## Installation Steps

### 1. Prepare Directory
Create a folder for the application, e.g., `C:\apps\tebita-sla`.
Copy the following files/folders to this directory:
- `backend/`
- `frontend/`
- `nginx.conf`
- `docker-compose.yml`
- `deploy.ps1`
- `.env.example`

### 2. Configure Environment
1.  Copy `.env.example` to `.env`.
2.  Open `.env` and fill in the production values:
    - `DB_PASSWORD`: Set a strong password.
    - `APP_SECRET_KEY`: Generate a random string.
    - `SMTP_PASSWORD`: Your Gmail App Password.

### 3. Firewall Configuration
Allow traffic on Port 80 (HTTP). Run this in PowerShell as Administrator:
```powershell
New-NetFirewallRule -DisplayName "Allow HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow
```

### 4. Deploy
Open PowerShell in the application directory and run:
```powershell
.\deploy.ps1
```

## Maintenance
- **Update**: Pull new code/images and run `.\deploy.ps1` again.
- **Logs**: `docker-compose logs -f`
- **Restart**: `docker-compose restart`
