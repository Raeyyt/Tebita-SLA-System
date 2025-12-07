"""Simple direct database check - which users exist and can they log in"""
import sqlite3

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

# Count users by role
cursor.execute("""
    SELECT role, COUNT(*) 
    FROM users 
    GROUP BY role
    ORDER BY role
""")

print("Users in tebita.db by role:")
print("="*50)
for role, count in cursor.fetchall():
    print(f"{role}: {count}")

# List first 5 users
print("\n" + "="*50)
print("Sample users (first 5):")
print("="*50)
cursor.execute("SELECT username, role, is_active FROM users LIMIT 5")
for username, role, is_active in cursor.fetchall():
    status = "ACTIVE" if is_active else "INACTIVE"
    print(f"{username:<40} | {role:<25} | {status}")

conn.close()

print("\n" + "="*50)
print("Database file: tebita.db")
print("Location: backend/tebita.db")
print("="*50)
