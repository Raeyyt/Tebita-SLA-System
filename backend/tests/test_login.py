"""Test login with specific credentials"""
from app.auth import verify_password
import sqlite3

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

# Test several usernames
test_users = [
    'raeyyt',
    'ems_division_manager',
    'hr_manager',
    'fleet_head'
]

print("Testing login credentials:\n")
print("="*80)

for username in test_users:
    cursor.execute("SELECT hashed_password, role, is_active FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    if result:
        hashed_pw, role, is_active = result
        # Test password
        is_valid = verify_password("password123", hashed_pw)
        active_text = "ACTIVE" if is_active else "INACTIVE"
        valid_text = "VALID" if is_valid else "INVALID"
        
        print(f"Username: {username}")
        print(f"  Role: {role}")
        print(f"  Status: {active_text}")
        print(f"  Password 'password123': {valid_text}")
        print()
    else:
        print(f"Username: {username}")
        print(f"  NOT FOUND IN DATABASE!")
        print()

conn.close()
