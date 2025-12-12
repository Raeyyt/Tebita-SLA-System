import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

# Configuration
BACKUP_DIR = Path("backups")
DB_FILE = Path("tebita.db")

def list_backups():
    if not BACKUP_DIR.exists():
        print("No backups directory found.")
        return []
    
    backups = sorted(BACKUP_DIR.glob("tebita_backup_*.db"), reverse=True)
    return backups

def restore_backup():
    print("="*50)
    print("TEBITA SYSTEM RESTORE UTILITY")
    print("="*50)
    
    backups = list_backups()
    
    if not backups:
        print("No backups found!")
        return
    
    print(f"\nFound {len(backups)} backups:")
    for i, backup in enumerate(backups):
        size_kb = backup.stat().st_size / 1024
        timestamp = datetime.fromtimestamp(backup.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i+1}. {backup.name} ({size_kb:.1f} KB) - {timestamp}")
    
    print("\n0. Exit")
    
    try:
        choice = int(input("\nSelect backup to restore (0-{}): ".format(len(backups))))
        
        if choice == 0:
            print("Exiting...")
            return
        
        if choice < 1 or choice > len(backups):
            print("Invalid selection.")
            return
            
        selected_backup = backups[choice-1]
        
        print(f"\nWARNING: This will overwrite the current '{DB_FILE}' database.")
        print("Ensure the backend server is STOPPED before proceeding.")
        confirm = input(f"Are you sure you want to restore '{selected_backup.name}'? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("Restoration cancelled.")
            return
            
        # Perform restore
        print(f"\nRestoring {selected_backup.name}...")
        
        # Create a safety backup of current state just in case
        if DB_FILE.exists():
            safety_backup = BACKUP_DIR / f"pre_restore_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(DB_FILE, safety_backup)
            print(f"Created safety backup of current state: {safety_backup.name}")
        
        shutil.copy2(selected_backup, DB_FILE)
        print("\nSUCCESS! Database restored.")
        print("You can now restart the backend server.")
        
    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"\nERROR: Restoration failed - {e}")

if __name__ == "__main__":
    restore_backup()
