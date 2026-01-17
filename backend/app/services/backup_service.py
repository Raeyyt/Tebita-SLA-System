"""
Database Backup Service

Provides automated database backup functionality for both SQLite and PostgreSQL.
Backups are stored in the `backups/` directory with timestamps.
"""
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from app.config import settings


# Backup directory configuration - Make it absolute relative to this file
BASE_DIR = Path(__file__).resolve().parent.parent.parent # Root of backend
BACKUP_DIR = BASE_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

DEBUG_LOG = BASE_DIR / "backup_debug.log"

def log_debug(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(DEBUG_LOG, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

# Retention settings (keep last N backups)
MAX_BACKUPS = 30  # Keep 30 days of backups


def get_backup_filename() -> str:
    """Generate a timestamped backup filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if settings.database_url.startswith("sqlite"):
        return f"tebita_backup_{timestamp}.db"
    else:
        return f"tebita_backup_{timestamp}.sql"


def cleanup_old_backups():
    """Remove old backups, keeping only the most recent MAX_BACKUPS files."""
    backups = sorted(BACKUP_DIR.glob("tebita_backup_*"))
    
    if len(backups) > MAX_BACKUPS:
        for old_backup in backups[:-MAX_BACKUPS]:
            old_backup.unlink()
            log_debug(f"[Backup] Deleted old backup: {old_backup.name}")


def backup_sqlite() -> Path:
    """Backup SQLite database using the safe backup API."""
    try:
        log_debug("--- Starting SQLite Backup ---")
        # Extract database path from URL (sqlite:///./tebita.db -> tebita.db)
        db_url = settings.database_url
        db_path_str = db_url.replace("sqlite:///", "")
        
        # Handle Windows paths and relative paths
        # If it starts with ./ or is just a filename, it's relative to BASE_DIR
        if db_path_str.startswith("./"):
            db_path = BASE_DIR / db_path_str[2:]
        elif not os.path.isabs(db_path_str):
            db_path = BASE_DIR / db_path_str
        else:
            db_path = Path(db_path_str)
            
        log_debug(f"[Backup] Resolved DB path: {db_path.absolute()}")
        
        if not db_path.exists():
            log_debug(f"[Backup] ERROR: SQLite database not found at {db_path}")
            # Try one more fallback: look in current working directory
            cwd_path = Path.cwd() / db_path_str.lstrip("./")
            log_debug(f"[Backup] Trying fallback CWD path: {cwd_path.absolute()}")
            if cwd_path.exists():
                db_path = cwd_path
            else:
                log_debug("[Backup] ERROR: All SQLite path resolutions failed.")
                return None
        
        backup_filename = get_backup_filename()
        backup_path = BACKUP_DIR / backup_filename
        
        log_debug(f"[Backup] Creating backup at: {backup_path.absolute()}")
        
        # Ensure backup directory exists
        BACKUP_DIR.mkdir(exist_ok=True)
        
        # Use sqlite3 backup API for a safe online backup
        src_conn = sqlite3.connect(str(db_path))
        dest_conn = sqlite3.connect(str(backup_path))
        try:
            with dest_conn:
                src_conn.backup(dest_conn)
            log_debug(f"[Backup] SQLite backup API completed successfully.")
        finally:
            dest_conn.close()
            src_conn.close()
        
        if not backup_path.exists():
            log_debug("[Backup] ERROR: Backup file was not created despite API success.")
            return None

        file_size = backup_path.stat().st_size / 1024  # Size in KB
        log_debug(f"[Backup] SUCCESS: SQLite backup created - {backup_path.name} ({file_size:.2f} KB)")
        
        cleanup_old_backups()
        return backup_path
        
    except Exception as e:
        import traceback
        log_debug(f"[Backup] ERROR: SQLite backup failed - {e}")
        log_debug(traceback.format_exc())
        return None


def backup_postgresql() -> Path:
    """Backup PostgreSQL database using pg_dump."""
    import subprocess
    from urllib.parse import urlparse
    
    try:
        log_debug("--- Starting PostgreSQL Backup ---")
        url = urlparse(settings.database_url)
        username = url.username
        password = url.password
        host = url.hostname
        port = url.port or 5432
        dbname = url.path.lstrip('/')

        backup_path = BACKUP_DIR / get_backup_filename()
        
        # Set password in environment for pg_dump to avoid interactive prompt
        env = os.environ.copy()
        if password:
            env["PGPASSWORD"] = password

        # Find pg_dump executable
        pg_dump_cmd = shutil.which("pg_dump") or "pg_dump"
        
        if os.name == 'nt' and pg_dump_cmd == "pg_dump": # Windows fallback
            # ... (existing Windows discovery logic)
            log_debug("[Backup] pg_dump not in PATH, searching in Program Files...")
            pg_base = Path("C:/Program Files/PostgreSQL")
            if pg_base.exists():
                versions = sorted([d for d in pg_base.iterdir() if d.is_dir() and d.name.isdigit()], 
                                 key=lambda x: int(x.name), reverse=True)
                for v in versions:
                    candidate = v / "bin" / "pg_dump.exe"
                    if candidate.exists():
                        pg_dump_cmd = str(candidate)
                        log_debug(f"[Backup] Found pg_dump at: {pg_dump_cmd}")
                        break

        log_debug(f"[Backup] Using pg_dump command: {pg_dump_cmd}")

        # Use custom format (-Fc) which is compressed and flexible
        cmd = [
            pg_dump_cmd,
            "-U", username,
            "-F", "c",
            "-f", str(backup_path)
        ]
        
        # Only add host and port if they are not default/local to allow socket connection on Linux
        if host and host not in ['localhost', '127.0.0.1']:
            cmd.extend(["-h", host, "-p", str(port)])
        elif os.name == 'nt': # Always add host on Windows
            cmd.extend(["-h", host or "localhost", "-p", str(port)])
            
        cmd.append(dbname)

        log_debug(f"[Backup] Running command: {' '.join([c for c in cmd if 'password' not in c.lower()])}")

        # Ensure directory is writable
        if not os.access(BACKUP_DIR, os.W_OK):
            log_debug(f"[Backup] ERROR: Backup directory {BACKUP_DIR} is not writable.")
            return None

        # Run pg_dump
        try:
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        except FileNotFoundError:
            log_debug(f"[Backup] ERROR: '{pg_dump_cmd}' utility not found.")
            return None
        
        if result.returncode != 0:
            log_debug(f"[Backup] ERROR: pg_dump failed with exit code {result.returncode}")
            log_debug(f"[Backup] Stderr: {result.stderr}")
            return None

        if not backup_path.exists():
            log_debug("[Backup] ERROR: Backup file was not created despite pg_dump success.")
            return None

        file_size = backup_path.stat().st_size / 1024  # Size in KB
        log_debug(f"[Backup] SUCCESS: PostgreSQL backup created - {backup_path.name} ({file_size:.2f} KB)")
        
        cleanup_old_backups()
        return backup_path
        
    except Exception as e:
        import traceback
        log_debug(f"[Backup] ERROR: PostgreSQL backup failed - {e}")
        log_debug(traceback.format_exc())
        return None


def create_database_backup() -> Path:
    """
    Create a database backup based on the configured database type.
    """
    log_debug(f"\n[Backup] Starting automatic database backup at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if settings.database_url.startswith("sqlite"):
        return backup_sqlite()
    else:
        return backup_postgresql()


def get_latest_backup() -> Path:
    """Get the most recent backup file."""
    backups = sorted(BACKUP_DIR.glob("tebita_backup_*"))
    return backups[-1] if backups else None
