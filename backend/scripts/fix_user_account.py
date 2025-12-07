"""Check and fix specific user account"""
import sqlite3
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

# Check if user exists
username = "administration_and_finance_head"
cursor.execute("SELECT id, username, email, full_name, is_active FROM users WHERE username = ?", (username,))
user = cursor.fetchone()

print("="*80)
print(f"CHECKING USER: {username}")
print("="*80)

if not user:
    print(f"\n❌ User '{username}' NOT FOUND in database!")
    print("\nSearching for similar usernames...")
    cursor.execute("SELECT username FROM users WHERE username LIKE '%administration%' OR username LIKE '%finance%'")
    similar = cursor.fetchall()
    if similar:
        print("Found similar users:")
        for s in similar:
            print(f"  - {s[0]}")
    else:
        print("No similar users found")
else:
    user_id, db_username, email, full_name, is_active = user
    print(f"\n✅ User found!")
    print(f"  ID: {user_id}")
    print(f"  Username: {db_username}")
    print(f"  Email: {email}")
    print(f"  Full Name: {full_name}")
    print(f"  Active: {'Yes' if is_active else 'No'}")
    
    # Reset password to password123
    new_password = "password123"
    hashed_password = pwd_context.hash(new_password)
    
    cursor.execute("UPDATE users SET hashed_password = ? WHERE id = ?", (hashed_password, user_id))
    conn.commit()
    
    print(f"\n✅ Password has been reset to: {new_password}")
    print(f"  Hashed value: {hashed_password[:50]}...")
    
    # Verify it works
    cursor.execute("SELECT hashed_password FROM users WHERE id = ?", (user_id,))
    stored_hash = cursor.fetchone()[0]
    
    if pwd_context.verify(new_password, stored_hash):
        print(f"\n✅ Password verification SUCCESSFUL!")
        print(f"  You can now login with:")
        print(f"  Username: {db_username}")
        print(f"  Password: {new_password}")
    else:
        print(f"\n❌ Password verification FAILED!")

conn.close()
print("\n" + "="*80)
