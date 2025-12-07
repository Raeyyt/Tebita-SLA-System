# Security Scan Report (auto-generated)

This file summarizes potential secrets and risky defaults found in the repository. Treat this as a high-priority checklist — rotate any exposed credentials and remove hard-coded secrets.

Findings

- `run_app.bat` contains a hard-coded `APP_SECRET_KEY=tebita-secret-key-123` output line. Remove and rotate.
- Multiple initializer scripts include default plaintext passwords used for demo or testing (e.g., `admin123`, `password123`, `rtxyz123`, `me123`, `ems123`, `hr123`). Files:
  - `backend/init_db.py` (prints default passwords)
  - `backend/simple_init.py` (many `password123` entries)
  - `backend/restructure_*` and `backend/create_test_user.py` (test passwords)
  - `backend/init_db.py` creates demo users with default passwords (admin123 etc.)
- `backend/.env.example` was added (good). Ensure you DO NOT commit a real `backend/.env` to Git.
- `docker-compose.yml` currently exposes `POSTGRES_PASSWORD=postgres` in the compose file used for local/dev; change before production.

Immediate remediation steps

1. Rotate secrets: change DB passwords, `APP_SECRET_KEY`, SMTP/Twilio credentials if they were used in any deployed instance.
2. Remove any files or scripts that print or store plaintext passwords in shared locations; move test/demo credentials to a secure vault or document privately.
3. Add `.env` to `.gitignore` (if not already) and verify there are no committed `.env` files via `git status` and `git log --all -- .env`.
4. Use environment variables or Docker secrets in production; consider a secrets manager (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault).
5. Run this scan periodically and before deployments.

If you'd like, I can:
- Rotate and replace values in `backend/.env.example` with safer placeholders.
- Add a simple pre-deploy script to check for accidental `.env` commits and suggest rotation steps.
