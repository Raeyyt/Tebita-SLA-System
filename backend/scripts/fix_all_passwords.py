"""Standalone password reset - no imports from app"""
import sqlite3
import bcrypt

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

# Get all users
cursor.execute("SELECT id, username FROM users ORDER BY username")
users = cursor.fetchall()

print("="*80)
print("RESETTING USER PASSWORDS")
print("="*80)

default_password = b'password123'
special_cases = {
    'ems_division_manager': b'test123'
}

success_count = 0

for user_id, username in users:
    password_bytes = special_cases.get(username, default_password)
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
    
    cursor.execute("UPDATE users SET hashed_password = ? WHERE id = ?", (hashed, user_id))
    password_str = password_bytes.decode('utf-8')
    print(f"✅ {username:45} -> {password_str}")
    success_count += 1

conn.commit()
conn.close()

print("\n" + "="*80)
print(f"✅ {success_count} passwords reset successfully!")
print("="*80)
print("\nLogin credentials:")
print("  - Most users: password123")
print("  - ems_division_manager: test123")
print("\nAll accounts are now working!")
