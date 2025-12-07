"""Reset all user passwords - FIXED VERSION"""
import sqlite3
import sys
sys.path.insert(0, 'app')

from auth import get_password_hash

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

# Get all users
cursor.execute("SELECT id, username FROM users ORDER BY username")
users = cursor.fetchall()

print("="*80)
print("RESETTING USER PASSWORDS")
print("="*80)

# Define passwords
passwords = {
    'ems_division_manager': 'test123'
}

default_password = 'password123'
success_count = 0
error_count = 0

for user_id, username in users:
    try:
        password = passwords.get(username, default_password)
        hashed = get_password_hash(password)
        
        cursor.execute("UPDATE users SET hashed_password = ? WHERE id = ?", (hashed, user_id))
        print(f"✅ {username:45} -> {password}")
        success_count += 1
    except Exception as e:
        print(f"❌ {username:45} -> ERROR: {e}")
        error_count += 1

conn.commit()
conn.close()

print("\n" + "="*80)
print(f"SUCCESS: {success_count} passwords reset")
print(f"ERRORS: {error_count}")
print("="*80)
if success_count > 0:
    print("\n✅ All user passwords have been reset!")
    print("   Default password: password123")
    print("   Special: ems_division_manager -> test123")
