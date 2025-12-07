"""
List all users and verify their passwords to provide a complete credential list
"""
import sqlite3
from app.auth import verify_password

def list_all_credentials():
    conn = sqlite3.connect('tebita.db')
    cursor = conn.cursor()
    
    print(f"{'USERNAME':<40} | {'ROLE':<25} | {'PASSWORD':<15} | {'STATUS'}")
    print("="*100)
    
    cursor.execute("SELECT username, role, hashed_password, is_active FROM users ORDER BY role, username")
    users = cursor.fetchall()
    
    for username, role, hashed_pw, is_active in users:
        password_display = "???"
        
        # Check against known passwords
        if verify_password("password123", hashed_pw):
            password_display = "password123"
        elif verify_password("test123", hashed_pw):
            password_display = "test123"
        else:
            password_display = "*Original*"
            
        status = "Active" if is_active else "Inactive"
        
        print(f"{username:<40} | {role:<25} | {password_display:<15} | {status}")
        
    conn.close()

if __name__ == "__main__":
    list_all_credentials()
