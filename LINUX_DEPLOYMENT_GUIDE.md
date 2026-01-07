# Linux Server Deployment Guide (Ubuntu/Debian)

This guide provides a complete, step-by-step process to deploy the Tebita SLA System on a fresh Linux server.

## Prerequisites
- A server running **Ubuntu 22.04 LTS** or **Debian 12**.
- **Root access** (or a user with `sudo` privileges).
- A domain name (optional, but recommended) pointing to your server's IP.

---

## Step 1: Update the Server
First, ensure your system is up to date.
```bash
sudo apt update
sudo apt upgrade -y
```

## Step 2: Install Required Software
We need Python, Node.js, PostgreSQL, Nginx (web server), and Git.

### 2.1 Install Python & Tools
```bash
sudo apt install -y python3-pip python3-venv git curl build-essential libpq-dev nano ufw
```

### 2.2 Install Node.js (Version 20)
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### 2.3 Install PostgreSQL
```bash
sudo apt install -y postgresql postgresql-contrib
```

### 2.4 Install Nginx
```bash
sudo apt install -y nginx
```

---

## Step 3: Configure the Database

1.  **Log in to PostgreSQL:**
    ```bash
    sudo -u postgres psql
    ```

2.  **Create Database & User:**
    *(Replace `secure_password` with a strong password)*
    ```sql
    CREATE DATABASE tebita_sla;
    CREATE USER tebita_user WITH PASSWORD 'secure_password';
    ALTER ROLE tebita_user SET client_encoding TO 'utf8';
    ALTER ROLE tebita_user SET default_transaction_isolation TO 'read committed';
    ALTER ROLE tebita_user SET timezone TO 'UTC';
    GRANT ALL PRIVILEGES ON DATABASE tebita_sla TO tebita_user;
    \q
    ```

---

## Step 4: Deploy the Backend

### 4.1 Clone the Repository
Navigate to the web root and clone your code.
```bash
cd /var/www
sudo git clone https://github.com/YOUR_USERNAME/Tebita-SLA-System.git
sudo chown -R $USER:$USER Tebita-SLA-System
cd Tebita-SLA-System/backend
```

### 4.2 Setup Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install gunicorn uvloop httptools
```

### 4.3 Configure Environment Variables
Create the `.env` file.
```bash
nano .env
```
Paste your production settings (make sure to use `localhost` for the database host):
```ini
DATABASE_URL=postgresql://tebita_user:secure_password@localhost/tebita_sla
APP_SECRET_KEY=your_generated_secret_key
# ... add other settings from .env.example
```
> [!IMPORTANT]
> Ensure `DATABASE_URL` uses `@localhost/` if PostgreSQL is running on the same server. Do not use `server` or other placeholders unless you have a remote database.

*Save and exit (Ctrl+O, Enter, Ctrl+X).*

### 4.4 Initialize Database
This will create the tables and seed initial data (divisions, departments, and admin users).
```bash
PYTHONPATH=. python scripts/init_db.py
```



### 4.5 Setup Systemd Service (Auto-Start)
Create a service file to keep the backend running.
```bash
sudo nano /etc/systemd/system/tebita-backend.service
```
Paste this content (adjust paths/user if needed):
```ini
[Unit]
Description=Gunicorn instance to serve Tebita Backend
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/Tebita-SLA-System/backend
Environment="PATH=/var/www/Tebita-SLA-System/backend/.venv/bin"
ExecStart=/var/www/Tebita-SLA-System/backend/.venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```
Start and enable the service:
```bash
sudo systemctl start tebita-backend
sudo systemctl enable tebita-backend
```

---

## Step 5: Deploy the Frontend

### 5.1 Build the React App
```bash
cd ../frontend
npm install
npm run build
```
This creates a `dist` folder with your static files.

### 5.2 Configure Nginx
Create a configuration file for your site.
```bash
sudo nano /etc/nginx/sites-available/tebita
```
Paste this configuration:
```nginx
server {
    listen 80; # Use 8080 if on ChromeOS/Penguin
    server_name your_domain_or_ip;

    # Serve Frontend
    location / {
        root /var/www/Tebita-SLA-System/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API Requests to Backend
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Proxy Auth Requests
    location /auth {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Proxy Docs (Swagger UI)
    location /docs {
        proxy_pass http://127.0.0.1:8000;
    }
    
    location /openapi.json {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

### 5.3 Enable the Site
```bash
sudo ln -s /etc/nginx/sites-available/tebita /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remove default site
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

---

## Step 6: Final Security Steps

### 6.1 Setup Firewall (UFW)
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 6.2 Setup SSL (HTTPS) - Optional but Recommended
If you have a domain name:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

---

## 🎉 Deployment Complete!
Visit `http://your_server_ip` (or your domain) in your browser. You should see the login page.
