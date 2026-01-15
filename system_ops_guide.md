# Tebita SLA System - Operations Guide

This guide provides instructions for accessing the system remotely, monitoring logs, and managing services.

## 1. Remote Access

### Web Application Access
Since Tailscale is installed on the server and your home computer, you can access the web interface using the server's Tailscale IP.

1.  **Find the Server IP**: Run `tailscale ip -4` on the server or look at your Tailscale dashboard.
2.  **Access in Browser**: Open your browser and go to:
    - `http://<SERVER_TAILSCALE_IP>` (Standard)
    - `http://<SERVER_TAILSCALE_IP>:8080` (If using the ChromeOS/Penguin configuration)

### SSH Access
To manage the server from home:
```bash
ssh <username>@<SERVER_TAILSCALE_IP>
```

---

## 2. Monitoring & Logs

### Backend Logs (FastAPI/Gunicorn)
To see real-time errors and debug information from the backend:
```bash
# View last 100 lines and follow new ones
sudo journalctl -u tebita-backend -f -n 100
```

### Web Server Logs (Nginx)
To see connection errors or static file issues:
```bash
# Error logs
sudo tail -f /var/log/nginx/error.log

# Access logs
sudo tail -f /var/log/nginx/access.log
```

### Database Logs (PostgreSQL)
```bash
sudo tail -f /var/log/postgresql/postgresql-16-main.log
```
*(Note: Version number might vary, e.g., `postgresql-14-main.log`)*

---

## 3. Service Management

If the system is unresponsive, you can restart the components:

### Restart Backend
```bash
sudo systemctl restart tebita-backend
```

### Restart Web Server
```bash
sudo systemctl restart nginx
```

### Check Service Status
```bash
sudo systemctl status tebita-backend
sudo systemctl status nginx
```

---

## 4. Troubleshooting Dashboard Crashes
We have optimized the database queries and connection pooling. If you still experience slowness:
1.  Check the backend logs for "Too many connections" errors.
2.  Ensure the server has enough RAM (at least 2GB recommended for concurrent use).
3.  Restart the backend service to clear any hung processes.
