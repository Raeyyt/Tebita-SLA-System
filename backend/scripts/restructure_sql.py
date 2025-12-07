"""Simple SQL-based restructuring"""
import sqlite3
from app.auth import get_password_hash

def restructure():
    conn = sqlite3.connect('tebita.db')
    cursor = conn.cursor()
    
    try:
        print("Starting restructuring...")
        
        # Delete all users except raeyyt
        cursor.execute("DELETE FROM users WHERE username != 'raeyyt'")
        deleted = cursor.rowcount
        print(f"Deleted {deleted} users")
        
        # Update raeyyt to ADMIN
        cursor.execute("UPDATE users SET role = 'ADMIN' WHERE username = 'raeyyt'")
        print("Updated raeyyt to ADMIN")
        
        # Get division IDs
        cursor.execute("SELECT id, name FROM divisions")
        divisions = {name: id for id, name in cursor.fetchall()}
        
        # Get department IDs
        cursor.execute("SELECT id, name, division_id FROM departments")
        departments = {name: (id, div_id) for id, name, div_id in cursor.fetchall()}
        
        # Get subdepartment IDs
        cursor.execute("SELECT id, name, department_id FROM subdepartments")
        subdepts = cursor.fetchall()
        
        hashed_pw = get_password_hash("password123")
        
        # Insert Division Managers
        div_mgrs = [
            ("ems_division_manager", "EMS Division Manager", "ems.manager@tebita.com", "DIVISION_MANAGER", divisions.get("EMS Division")),
            ("medcom_division_manager", "MEDCOM Division Manager", "medcom.manager@tebita.com", "DIVISION_MANAGER", divisions.get("MEDCOM Division")),
            ("support_division_liaison", "Support Division Liaison", "support.liaison@tebita.com", "DIVISION_MANAGER", divisions.get("Support Division"))
        ]
        
        for username, full_name, email, role, div_id in div_mgrs:
            cursor.execute("""
                INSERT INTO users (username, full_name, email, hashed_password, role, division_id, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (username, full_name, email, hashed_pw, role, div_id))
        print(f"Created {len(div_mgrs)} division managers")
        
        # Insert Department Heads
        dept_heads = [
            ("ambulance_services_head", "Comprehensive Ambulance Service Head", "DEPARTMENT_HEAD", "Comprehensive Ambulance Service"),
            ("cpd_training_head", "CPD Short Term Training Head", "DEPARTMENT_HEAD", "CPD Short Term Training"),
            ("vocational_training_head", "Vocational Training Head", "DEPARTMENT_HEAD", "Vocational Training"),
            ("medical_equipment_head", "Medical Equipment Production Head", "DEPARTMENT_HEAD", "Medical Equipment Production"),
            ("pharma_import_head", "Pharmaceutical Import Head", "DEPARTMENT_HEAD", "Pharmaceutical Import"),
            ("hr_manager", "HR Manager", "DEPARTMENT_HEAD", "HR"),
            ("finance_manager", "Finance Manager", "DEPARTMENT_HEAD", "Finance")
        ]
        
        for username, full_name, role, dept_name in dept_heads:
            if dept_name in departments:
                dept_id, div_id = departments[dept_name]
                cursor.execute("""
                    INSERT INTO users (username, full_name, email, hashed_password, role, division_id, department_id, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """, (username, full_name, f"{username}@tebita.com", hashed_pw, role, div_id, dept_id))
        print(f"Created {len(dept_heads)} department heads")
        
        # Insert Sub-Department Staff
        cursor.execute("SELECT id, name, department_id FROM subdepartments")
        subdepts = cursor.fetchall()
        
        for subdept_id, name, dept_id in subdepts:
            username = name.lower().replace(" ", "_").replace("&", "and")[:50]
            cursor.execute("SELECT division_id FROM departments WHERE id = ?", (dept_id,))
            div_id = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO users (username, full_name, email, hashed_password, role, division_id, department_id, subdepartment_id, is_active)
                VALUES (?, ?, ?, ?, 'SUB_DEPARTMENT_STAFF', ?, ?, ?, 1)
            """, (username, name, f"{username}@tebita.com", hashed_pw, div_id, dept_id, subdept_id))
        
        print(f"Created {len(subdepts)} sub-department staff")
        
        conn.commit()
        print("\nRESTRUCTURING COMPLETE!")
        print(f"Total users: {1 + len(div_mgrs) + len(dept_heads) + len(subdepts)}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    restructure()
