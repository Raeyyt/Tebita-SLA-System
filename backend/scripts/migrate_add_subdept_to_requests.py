"""
Add missing subdepartment columns to requests table
"""
import sqlite3

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

print("="*80)
print("ADDING SUBDEPARTMENT COLUMNS TO REQUESTS TABLE")
print("="*80)

# Check current schema
cursor.execute("PRAGMA table_info(requests)")
columns = [col[1] for col in cursor.fetchall()]
print(f"\nCurrent columns: {len(columns)}")

# Add requester_subdepartment_id if missing
if 'requester_subdepartment_id' not in columns:
    print("\nAdding requester_subdepartment_id column...")
    cursor.execute("""
        ALTER TABLE requests 
        ADD COLUMN requester_subdepartment_id INTEGER 
        REFERENCES subdepartments(id)
    """)
    print("✅ Added requester_subdepartment_id")
else:
    print("\n✅ requester_subdepartment_id already exists")

# Add assigned_subdepartment_id if missing
if 'assigned_subdepartment_id' not in columns:
    print("\nAdding assigned_subdepartment_id column...")
    cursor.execute("""
        ALTER TABLE requests 
        ADD COLUMN assigned_subdepartment_id INTEGER 
        REFERENCES subdepartments(id)
    """)
    print("✅ Added assigned_subdepartment_id")
else:
    print("\n✅ assigned_subdepartment_id already exists")

conn.commit()

# Verify the changes
cursor.execute("PRAGMA table_info(requests)")
new_columns = [col[1] for col in cursor.fetchall()]
print(f"\n{'='*80}")
print(f"MIGRATION COMPLETE")
print(f"{'='*80}")
print(f"Total columns now: {len(new_columns)}")
print(f"✅ requester_subdepartment_id: {'YES' if 'requester_subdepartment_id' in new_columns else 'NO'}")
print(f"✅ assigned_subdepartment_id: {'YES' if 'assigned_subdepartment_id' in new_columns else 'NO'}")

conn.close()
print("\n✅ Database migration successful! Backend should now start correctly.")
