"""Create users for the newly added subdepartments"""
import sqlite3
from app.auth import get_password_hash

def create_new_subdept_users():
    conn = sqlite3.connect('tebita.db')
    cursor = conn.cursor()
    
    try:
        print("Creating users for new sub-departments...")
        
        # Get all subdepartments that don't have users yet
        cursor.execute("""
            SELECT s.id, s.name, s.department_id
            FROM subdepartments s
            WHERE s.id NOT IN (SELECT subdepartment_id FROM users WHERE subdepartment_id IS NOT NULL)
            ORDER BY s.name
        """)
        
        new_subdepts = cursor.fetchall()
        print(f"\nFound {len(new_subdepts)} sub-departments without users\n")
        
        hashed_pw = get_password_hash("password123")
        created = 0
        
        for subdept_id, name, dept_id in new_subdepts:
            username = name.lower().replace(" ", "_").replace("&", "and").replace("(", "").replace(")", "")[:50]
            
            # Get division_id from department
            cursor.execute("SELECT division_id FROM departments WHERE id = ?", (dept_id,))
            div_id = cursor.fetchone()[0]
            
            # Create user
            cursor.execute("""
                INSERT INTO users (username, full_name, email, hashed_password, role, division_id, department_id, subdepartment_id, is_active)
                VALUES (?, ?, ?, ?, 'SUB_DEPARTMENT_STAFF', ?, ?, ?, 1)
            """, (username, name, f"{username}@tebita.com", hashed_pw, div_id, dept_id, subdept_id))
            
            print(f"  + {username}")
            created += 1
        
        conn.commit()
        
        # Get total user count
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM subdepartments")
        total_subdepts = cursor.fetchone()[0]
        
        print(f"\n{'='*60}")
        print(f"Created {created} new users")
        print(f"Total users in system: {total_users}")
        print(f"Total sub-departments: {total_subdepts}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    create_new_subdept_users()
