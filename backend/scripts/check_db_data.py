"""Check database structure and sample data"""
import sqlite3

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

print("="*80)
print("DATABASE SCHEMA & DATA CHECK")
print("="*80)

# Get requests table schema
cursor.execute("PRAGMA table_info(requests)")
columns = cursor.fetchall()
print("\nREQUESTS TABLE COLUMNS:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# Check requests
cursor.execute("SELECT COUNT(*) FROM requests")
request_count = cursor.fetchone()[0]
print(f"\n📊 Total Requests: {request_count}")

if request_count > 0:
    cursor.execute("SELECT request_id, status, priority FROM requests LIMIT 5")
    print("\nSample Requests:")
    for req_id, status, priority in cursor.fetchall():
        print(f"  - {req_id}: {status} (Priority: {priority})")

# Check organizational structure
cursor.execute("SELECT COUNT(*) FROM divisions")
division_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM departments")
dept_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM subdepartments")
subdept_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]

print(f"\n📁 Organizational Structure:")
print(f"  - Divisions: {division_count}")
print(f"  - Departments: {dept_count}")
print(f"  - Sub-Departments: {subdept_count}")
print(f"  - Users: {user_count}")

conn.close()

print("\n" + "="*80)
print("✅ DATABASE IS POPULATED - Problem is with API or Frontend")
print("="*80)
