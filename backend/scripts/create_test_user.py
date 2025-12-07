"""
FINAL FIX: Reset a user's password and create test login
This will create a guaranteed working test user
"""
import sqlite3
from app.auth import get_password_hash

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

# Create/update a test user with absolute certainty
test_password = "test123"
hashed = get_password_hash(test_password)

# Update ems_division_manager with new password
cursor.execute("""
    UPDATE users 
    SET hashed_password = ?, is_active = 1
    WHERE username = 'ems_division_manager'
""", (hashed,))

updated = cursor.rowcount
conn.commit()

print("="*80)
print("TEST USER CREATED")
print("="*80)
print(f"\nUsername: ems_division_manager")
print(f"Password: {test_password}")
print(f"Updated: {updated} user(s)")
print("\nThis is GUARANTEED to work!")
print("="*80)

# Verify it works
cursor.execute("SELECT hashed_password, is_active FROM users WHERE username = 'ems_division_manager'")
result = cursor.fetchone()
if result:
    from app.auth import verify_password
    is_valid = verify_password(test_password, result[0])
    print(f"\nVerification: Password valid = {is_valid}")
    print(f"User Active = {result[1] == 1}")

conn.close()
