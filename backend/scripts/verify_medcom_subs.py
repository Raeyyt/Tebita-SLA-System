"""Verify sub-departments for MEDCOM departments"""
import sqlite3

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

print("="*80)
print("VERIFYING MEDCOM SUB-DEPARTMENTS")
print("="*80)

# Get MEDCOM division
cursor.execute("SELECT id, name FROM divisions WHERE name LIKE '%MEDCOM%'")
medcom = cursor.fetchone()
div_id = medcom[0]

# Get departments
cursor.execute("SELECT id, name FROM departments WHERE division_id = ?", (div_id,))
depts = cursor.fetchall()

for dept_id, dept_name in depts:
    print(f"\nDepartment: {dept_name} (ID: {dept_id})")
    
    # Get sub-departments
    cursor.execute("SELECT id, name FROM subdepartments WHERE department_id = ?", (dept_id,))
    subs = cursor.fetchall()
    
    if subs:
        print(f"  ✅ Found {len(subs)} sub-departments:")
        for s in subs:
            print(f"    - {s[1]} (ID: {s[0]})")
    else:
        print("  ❌ NO SUB-DEPARTMENTS FOUND!")

conn.close()
print("\n" + "="*80)
