"""
Database Migration: Add SLA Policy System
Creates sla_policies table and adds activity_type to requests table
"""

import sqlite3
from pathlib import Path

def migrate():
    db_path = Path(__file__).parent.parent / "tebita.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Starting SLA Policy System migration...")
        
        # Step 1: Create sla_policies table
        print("\n1. Creating sla_policies table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sla_policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                division_id INTEGER,
                department_id INTEGER,
                resource_type VARCHAR(50) NOT NULL,
                activity_type VARCHAR(200),
                priority VARCHAR(20) NOT NULL,
                response_time_hours REAL NOT NULL,
                completion_time_hours REAL NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT 1 NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY (division_id) REFERENCES divisions(id),
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        """)
        
        # Create indexes for fast lookup
        print("   - Creating indexes on sla_policies...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sla_division ON sla_policies(division_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sla_department ON sla_policies(department_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sla_resource ON sla_policies(resource_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sla_activity ON sla_policies(activity_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sla_priority ON sla_policies(priority)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sla_active ON sla_policies(is_active)")
        
        # Step 2: Check if activity_type column exists in requests
        print("\n2. Checking requests table for activity_type column...")
        cursor.execute("PRAGMA table_info(requests)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'activity_type' not in columns:
            print("   - Adding activity_type column to requests table...")
            cursor.execute("ALTER TABLE requests ADD COLUMN activity_type VARCHAR(200)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_request_activity ON requests(activity_type)")
            print("   ✓ activity_type column added")
        else:
            print("   ✓ activity_type column already exists")
        
        # Commit all changes
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM sla_policies")
        policy_count = cursor.fetchone()[0]
        print(f"\nSummary:")
        print(f"  - sla_policies table: Created")
        print(f"  - Current SLA policies: {policy_count}")
        print(f"  - requests.activity_type: Added")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
