"""
Generate a markdown list of credentials grouped by role
"""
import sqlite3
from app.auth import verify_password

def generate_credentials_md():
    conn = sqlite3.connect('tebita.db')
    cursor = conn.cursor()
    
    # Get all users
    cursor.execute("SELECT username, role, hashed_password FROM users ORDER BY role, username")
    users = cursor.fetchall()
    
    # Group by role
    grouped = {}
    for username, role, hashed_pw in users:
        if role not in grouped:
            grouped[role] = []
        
        password = "???"
        if verify_password("password123", hashed_pw):
            password = "password123"
        elif verify_password("test123", hashed_pw):
            password = "test123"
        else:
            password = "*User's Original Password*"
            
        grouped[role].append((username, password))
    
    # Generate Markdown
    md = "# System Credentials\n\n"
    md += "Here is the complete list of users who can log in to the system.\n\n"
    
    role_order = ["ADMIN", "DIVISION_MANAGER", "DEPARTMENT_HEAD", "SUB_DEPARTMENT_STAFF"]
    
    for role in role_order:
        if role in grouped:
            md += f"## {role}\n\n"
            md += "| Username | Password | Status |\n"
            md += "|----------|----------|--------|\n"
            for username, password in grouped[role]:
                status = "✅ Verified" if password != "???" else "⚠️ Unknown"
                md += f"| `{username}` | `{password}` | {status} |\n"
            md += "\n"
            
    with open('credentials.md', 'w', encoding='utf-8') as f:
        f.write(md)
    print("Credentials written to credentials.md")

if __name__ == "__main__":
    generate_credentials_md()
