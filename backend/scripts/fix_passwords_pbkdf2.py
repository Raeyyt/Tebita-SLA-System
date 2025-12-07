"""Fix passwords using CORRECT hash scheme - pbkdf2_sha256"""
import sqlite3
from passlib.context import CryptContext

# USE SAME CONTEXT AS auth.py - pbkdf2_sha256, NOT bcrypt!
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

print("="*80)
print("FIXING PASSWORDS WITH CORRECT HASH SCHEME (pbkdf2_sha256)")
print("="*80)

# Get all users
cursor.execute("SELECT id, username FROM users ORDER BY username")
users = cursor.fetchall()

passwords = {
    'ems_division_manager': 'test123',
    'raeyyt': 'password123'
}

default_password = 'password123'
fixed = 0

for user_id, username in users:
    password = passwords.get(username, default_password)
    
    # Hash using pbkdf2_sha256 (matches auth.py)
    hashed = pwd_context.hash(password)
    
    cursor.execute("UPDATE users SET hashed_password = ? WHERE id = ?", (hashed, user_id))
    print(f"✅ {username:45} -> {password}")
    fixed += 1

conn.commit()
conn.close()

print(f"\n{'='*80}")
print(f"✅ SUCCESSFULLY fixed {fixed} passwords!")
print(f"{'='*80}")
print("\nAll users can now login:")
print("  Standard: password123")
print("  ems_division_manager: test123")
print("\n🔄 Restart the backend and try logging in!")
