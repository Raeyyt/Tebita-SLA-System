"""
Add missing sub-departments - updated version
"""
import sqlite3

def add_missing_subdepartments():
    conn = sqlite3.connect('tebita.db')
    cursor = conn.cursor()
    
    try:
        print("Adding missing sub-departments...")
        
        # Get department IDs - try different name variations
        cursor.execute("SELECT id, name FROM departments")
        all_depts = cursor.fetchall()
        
        print("\nAvailable departments:")
        for dept_id, name in all_depts:
            print(f"  {dept_id}: {name}")
        
        # Find Finance department (could be "Finance" or "Finance Department")
        cursor.execute("SELECT id FROM departments WHERE name LIKE '%Finance%' LIMIT 1")
        finance_result = cursor.fetchone()
        finance_dept_id = finance_result[0] if finance_result else None
        
        # Find HR department (could be various names)
        cursor.execute("SELECT id FROM departments WHERE name LIKE '%HR%' OR name LIKE '%Human%' LIMIT 1")
        hr_result = cursor.fetchone()
        hr_dept_id = hr_result[0] if hr_result else None
        
        print(f"\nFinance Department ID: {finance_dept_id}")
        print(f"HR Department ID: {hr_dept_id}")
        
        # Finance Department sub-departments (6 total)
        finance_subdepts = [
            "Senior Revenue & Collection Accountant",
            "Costing Accountant",
            "Store Office",
            "Senior Payment & Disbursement Officer",
            "Junior Accountant",
            "Cashier"
        ]
        
        # HR Department sub-departments (6 total)
        hr_subdepts = [
            "Office Assistant",
            "Legal Advisor",
            "Procurement",
            "IT Department",
            "Maintenance",
            "Communication Officer"
        ]
        
        added_count = 0
        
        # Add Finance sub-departments
        if finance_dept_id:
            print("\nAdding Finance sub-departments:")
            for subdept_name in finance_subdepts:
                # Check if already exists
                cursor.execute("SELECT COUNT(*) FROM subdepartments WHERE name = ?", (subdept_name,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO subdepartments (name, department_id, description, created_at)
                        VALUES (?, ?, ?, datetime('now'))
                    """, (subdept_name, finance_dept_id, f"{subdept_name} sub-department"))
                    added_count += 1
                    print(f"  + {subdept_name}")
                else:
                    print(f"  - {subdept_name} (already exists)")
        else:
            print("\nWARNING: Finance department not found!")
        
        # Add HR sub-departments
        if hr_dept_id:
            print("\nAdding HR sub-departments:")
            for subdept_name in hr_subdepts:
                # Check if already exists
                cursor.execute("SELECT COUNT(*) FROM subdepartments WHERE name = ?", (subdept_name,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO subdepartments (name, department_id, description, created_at)
                        VALUES (?, ?, ?, datetime('now'))
                    """, (subdept_name, hr_dept_id, f"{subdept_name} sub-department"))
                    added_count += 1
                    print(f"  + {subdept_name}")
                else:
                    print(f"  - {subdept_name} (already exists)")
        else:
            print("\nWARNING: HR department not found!")
        
        conn.commit()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM subdepartments")
        total = cursor.fetchone()[0]
        
        print(f"\n{'='*60}")
        print(f"Added {added_count} new sub-departments")
        print(f"Total sub-departments in system: {total}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    add_missing_subdepartments()
