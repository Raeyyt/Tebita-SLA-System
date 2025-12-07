"""Check what users exist in the database and test authentication"""
import sqlite3
from app.auth import get_password_hash, verify_password

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

# Get all users
cursor.execute("SELECT id, username, role, is_active FROM users ORDER BY id")
users = cursor.fetchall()

print(f"Total users in database: {len(users)}\n")
print(f"{'ID':<5} | {'Username':<40} | {'Role':<25} | {'Active'}")
print("="*100)

for user_id, username, role, is_active in users:
    active_status = "Yes" if is_active else "No"
    print(f"{user_id:<5} | {username:<40} | {role:<25} | {active_status}")

# Test password for one user
print("\n" + "="*100)
print("Testing authentication for 'ems_division_manager'...")

cursor.execute("SELECT hashed_password FROM users WHERE username = ?", ("ems_division_manager",))
result = cursor.fetchone()

if result:
    hashed_pw = result[0]
    # Test with password123
    is_valid = verify_password("password123", hashed_pw)
    print(f"Password 'password123' valid: {is_valid}")
    
    # Show what the hash looks like
    print(f"\nStored hash starts with: {hashed_pw[:50]}...")
    
    # Create new hash to compare
    new_hash = get_password_hash("password123")
    print(f"New hash would be: {new_hash[:50]}...")
else:
    print("User 'ems_division_manager' NOT FOUND in database!")

# Check raeyyt
print("\n" + "="*100)
print("Checking 'raeyyt' user...")
cursor.execute("SELECT username, role, is_active FROM users WHERE username = 'raeyyt'")
raeyyt = cursor.fetchone()
if raeyyt:
    print(f"raeyyt found: role={raeyyt[1]}, active={raeyyt[2]}")
else:
    print("raeyyt NOT FOUND!")

conn.close()
