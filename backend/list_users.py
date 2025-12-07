import sqlite3
import os

# Connect to database
db_path = 'tebita.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"{'Username':<30} | {'Role':<20} | {'Active'}")
print("-" * 60)

try:
    cursor.execute("SELECT username, role, is_active FROM users ORDER BY role, username")
    users = cursor.fetchall()
    for user in users:
        print(f"{user[0]:<30} | {user[1]:<20} | {user[2]}")
except Exception as e:
    print(f"Error: {e}")

conn.close()
