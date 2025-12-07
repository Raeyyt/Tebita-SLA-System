"""
Fix existing user roles in database before restructuring
This updates any old role values to valid ones
"""
import sqlite3

def fix_user_roles():
    conn = sqlite3.connect('tebita.db')
    cursor = conn.cursor()
    
    try:
        print("Checking and fixing user roles...")
        
        # Get all users
        cursor.execute("SELECT id, username, role FROM users")
        users = cursor.fetchall()
        
        print(f"Found {len(users)} users")
        
        # Update all users except raeyyt to a valid temporary role
        for user_id, username, role in users:
            if username == 'raeyyt':
                # Set raeyyt to ADMIN
                cursor.execute("UPDATE users SET role = 'ADMIN' WHERE id = ?", (user_id,))
                print(f"  ✓ {username}: ADMIN")
            else:
                # Set others to SUB_DEPARTMENT_STAFF temporarily (will be deleted anyway)
                cursor.execute("UPDATE users SET role = 'SUB_DEPARTMENT_STAFF' WHERE id = ?", (user_id,))
        
        conn.commit()
        print(f"\n✓ Updated {len(users)} user roles")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_user_roles()
