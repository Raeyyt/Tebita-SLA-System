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


# Backup directory configuration
BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)

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
            print(f"[Backup] Deleted old backup: {old_backup.name}")


def backup_sqlite() -> Path:
    """Backup SQLite database using the safe backup API."""
    try:
        # Extract database path from URL (sqlite:///./tebita.db -> tebita.db)
        db_url = settings.database_url
        db_path_str = db_url.replace("sqlite:///", "")
        
        # Handle Windows paths and relative paths
        db_path = Path(db_path_str)
        
        print(f"[Backup] Attempting to backup SQLite DB: {db_path.absolute()}")
        
        # If not found, try common locations
        if not db_path.exists():
            # Try relative to backend directory if we are in root
            alt_path = Path("backend") / db_path_str.lstrip("./")
            print(f"[Backup] Primary path not found, trying alt: {alt_path.absolute()}")
            if alt_path.exists():
                db_path = alt_path
            else:
                # Try relative to current directory without ./
                alt_path = Path(db_path_str.lstrip("./"))
                print(f"[Backup] Alt path not found, trying another: {alt_path.absolute()}")
                if alt_path.exists():
                    db_path = alt_path
        
        if not db_path.exists():
            print(f"[Backup] ERROR: SQLite database not found at any expected location.")
            return None
        
        backup_filename = get_backup_filename()
        backup_path = BACKUP_DIR / backup_filename
        
        print(f"[Backup] Creating backup at: {backup_path.absolute()}")
        
        # Use sqlite3 backup API for a safe online backup
        # This avoids "file in use" errors on Windows
        src_conn = sqlite3.connect(str(db_path))
        dest_conn = sqlite3.connect(str(backup_path))
        try:
            with dest_conn:
                src_conn.backup(dest_conn)
            print(f"[Backup] SQLite backup API completed successfully.")
        finally:
            dest_conn.close()
            src_conn.close()
        
        file_size = backup_path.stat().st_size / 1024  # Size in KB
        print(f"[Backup] SUCCESS: SQLite backup created - {backup_path.name} ({file_size:.2f} KB)")
        
        cleanup_old_backups()
        return backup_path
        
    except Exception as e:
        import traceback
        print(f"[Backup] ERROR: SQLite backup failed - {e}")
        traceback.print_exc()
        return None


def backup_postgresql() -> Path:
    """Backup PostgreSQL database using pg_dump."""
    import subprocess
    from urllib.parse import urlparse
    
    try:
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

        # Use custom format (-Fc) which is compressed and flexible
        cmd = [
            "pg_dump",
            "-h", host,
            "-p", str(port),
            "-U", username,
            "-F", "c",
            "-f", str(backup_path),
            dbname
        ]

        # Run pg_dump
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"[Backup] ERROR: pg_dump failed - {result.stderr}")
            # Fallback to a simple message if pg_dump is missing
            if "not found" in result.stderr.lower() or "not recognized" in result.stderr.lower():
                print("[Backup] ERROR: 'pg_dump' utility not found on system path.")
            return None

        file_size = backup_path.stat().st_size / 1024  # Size in KB
        print(f"[Backup] SUCCESS: PostgreSQL backup created - {backup_path.name} ({file_size:.2f} KB)")
        
        cleanup_old_backups()
        return backup_path
        
    except Exception as e:
        print(f"[Backup] ERROR: PostgreSQL backup failed - {e}")
        return None


def create_database_backup() -> Path:
    """
    Create a database backup based on the configured database type.
    
    Returns:
        Path to the backup file if successful, None otherwise.
    """
    print(f"\n[Backup] Starting automatic database backup at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if settings.database_url.startswith("sqlite"):
        return backup_sqlite()
    else:
        return backup_postgresql()


def get_latest_backup() -> Path:
    """Get the most recent backup file."""
    backups = sorted(BACKUP_DIR.glob("tebita_backup_*"))
    return backups[-1] if backups else None
