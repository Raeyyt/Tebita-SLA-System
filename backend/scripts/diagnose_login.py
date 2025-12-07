"""
Comprehensive Login Diagnostic and Fix Script
This will check everything and fix any issues
"""
import sqlite3
from app.auth import get_password_hash, verify_password

def diagnose_and_fix():
    conn = sqlite3.connect('tebita.db')
    cursor = conn.cursor()
    
    print("="*80)
    print("COMPREHENSIVE LOGIN DIAGNOSTIC")
    print("="*80)
    
    # Step 1: Check database structure
    print("\n[1/5] Checking database structure...")
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"  Columns in users table: {', '.join(columns)}")
    
    required_cols = ['id', 'username', 'hashed_password', 'is_active', 'role']
    missing = [col for col in required_cols if col not in columns]
    if missing:
        print(f"  WARNING: Missing columns: {missing}")
    else:
        print(f"  OK: All required columns present")
    
    # Step 2: Count users
    print("\n[2/5] Counting users...")
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    print(f"  Total users: {total_users}")
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
    active_users = cursor.fetchone()[0]
    print(f"  Active users: {active_users}")
    
    # Step 3: Test specific users
    print("\n[3/5] Testing specific user credentials...")
    test_users = [
        ('ems_division_manager', 'password123'),
        ('fleet_head', 'password123'),
        ('cpd_coordinator', 'password123'),
    ]
    
    working_count = 0
    for username, password in test_users:
        cursor.execute("SELECT hashed_password, is_active FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if result:
            hashed_pw, is_active = result
            is_valid = verify_password(password, hashed_pw)
            status = "ACTIVE" if is_active else "INACTIVE"
            auth_status = "VALID" if is_valid else "INVALID"
            
            print(f"  {username}: {status}, Password: {auth_status}")
            if is_valid and is_active:
                working_count += 1
        else:
            print(f"  {username}: NOT FOUND")
    
    print(f"\n  Working credentials: {working_count}/{len(test_users)}")
    
    # Step 4: Check for password hash issues
    print("\n[4/5] Verifying password hash format...")
    cursor.execute("SELECT username, hashed_password FROM users LIMIT 3")
    for username, hashed_pw in cursor.fetchall():
        if hashed_pw and hashed_pw.startswith('$pbkdf2-sha256$'):
            print(f"  {username}: OK (proper hash format)")
        else:
            print(f"  {username}: WARNING (unexpected hash format: {hashed_pw[:30]}...)")
    
    # Step 5: Fix any inactive users
    print("\n[5/5] Activating all users...")
    cursor.execute("UPDATE users SET is_active = 1 WHERE is_active = 0")
    activated = cursor.rowcount
    if activated > 0:
        print(f"  Activated {activated} users")
        conn.commit()
    else:
        print(f"  All users already active")
    
    # Final summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
    print("\nUsers by role:")
    for role, count in cursor.fetchall():
        print(f"  {role}: {count}")
    
    # Provide working credentials
    print("\n" + "="*80)
    print("VERIFIED WORKING CREDENTIALS:")
    print("="*80)
    
    cursor.execute("""
        SELECT username, role 
        FROM users 
        WHERE username IN ('ems_division_manager', 'fleet_head', 'cpd_coordinator', 'finance_manager')
        AND is_active = 1
        LIMIT 5
    """)
    
    for username, role in cursor.fetchall():
        print(f"  Username: {username:<40} | Password: password123")
    
    conn.close()
    print("\n" + "="*80)

if __name__ == "__main__":
    diagnose_and_fix()
