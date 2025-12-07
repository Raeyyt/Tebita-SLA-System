"""Fix corrupted password hashes - use passlib bcrypt"""
import sqlite3
from passlib.context import CryptContext

# Match the exact context from auth.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

print("="*80)
print("FIXING CORRUPTED PASSWORD HASHES")
print("="*80)

# Get all users
cursor.execute("SELECT id, username FROM users ORDER BY username")
users = cursor.fetchall()

passwords = {
    'ems_division_manager': 'test123',
    'raeyyt': 'password123'  # Reset admin to password123 too
}

default_password = 'password123'
fixed = 0

for user_id, username in users:
    password = passwords.get(username, default_password)
    
    # Use passlib's bcrypt hashing (same as auth.py)
    hashed = pwd_context.hash(password)
    
    cursor.execute("UPDATE users SET hashed_password = ? WHERE id = ?", (hashed, user_id))
    print(f"✅ {username:45} -> {password}")
    fixed += 1

conn.commit()
conn.close()

print(f"\n{'='*80}")
print(f"✅ Fixed {fixed} user passwords!")
print(f"{'='*80}")
print("\nAll users can now login:")
print("  Standard: password123")
print("  ems_division_manager: test123")
