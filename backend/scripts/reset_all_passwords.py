"""Reset all user passwords to 'password123' (except specified users)"""
import sqlite3
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

# Get all users
cursor.execute("SELECT id, username FROM users ORDER BY username")
users = cursor.fetchall()

print("="*80)
print("RESETTING ALL USER PASSWORDS")
print("="*80)

# Special cases
special_passwords = {
    'ems_division_manager': 'test123',
    # Add raeyyt original password if known, otherwise will be set to password123
}

default_password = 'password123'
fixed_count = 0

for user_id, username in users:
    # Determine password
    password = special_passwords.get(username, default_password)
    
    # Hash and update
    hashed = pwd_context.hash(password)
    cursor.execute("UPDATE users SET hashed_password = ? WHERE id = ?", (hashed, user_id))
    
    print(f"✅ {username:40} -> {password}")
    fixed_count += 1

conn.commit()
conn.close()

print("\n" + "="*80)
print(f"✅ {fixed_count} user passwords have been reset!")
print("="*80)
print("\nStandard password: password123")
print("Special cases:")
print("  - ems_division_manager: test123")
print("\nAll users can now login!")
