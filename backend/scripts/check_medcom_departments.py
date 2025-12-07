"""Check MEDCOM division departments"""
import sqlite3

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

print("="*80)
print("CHECKING MEDCOM DIVISION DEPARTMENTS")
print("="*80)

# Get MEDCOM division
cursor.execute("SELECT id, name FROM divisions WHERE name LIKE '%MEDCOM%'")
medcom = cursor.fetchone()

if not medcom:
    print("\n❌ MEDCOM Division not found!")
else:
    div_id, div_name = medcom
    print(f"\n✅ Found Division: {div_name} (ID: {div_id})")
    
    # Get all departments in MEDCOM
    cursor.execute("SELECT id, name, division_id FROM departments WHERE division_id = ?", (div_id,))
    depts = cursor.fetchall()
    
    print(f"\nDepartments in {div_name}:")
    print(f"Total: {len(depts)}")
    for dept_id, dept_name, dept_div_id in depts:
        print(f"  - ID {dept_id}: {dept_name}")
        
        # Check for subdepartments
        cursor.execute("SELECT COUNT(*) FROM subdepartments WHERE department_id = ?", (dept_id,))
        subdept_count = cursor.fetchone()[0]
        print(f"    Sub-departments: {subdept_count}")

# Check if there are departments with wrong division_id
cursor.execute("""
    SELECT id, name, division_id 
    FROM departments 
    WHERE name LIKE '%Medical%' OR name LIKE '%Equipment%' OR name LIKE '%Production%'
""")
all_medical_depts = cursor.fetchall()

print(f"\n{'='*80}")
print("ALL MEDICAL/EQUIPMENT/PRODUCTION DEPARTMENTS:")
for dept_id, dept_name, dept_div_id in all_medical_depts:
    cursor.execute("SELECT name FROM divisions WHERE id = ?", (dept_div_id,))
    div = cursor.fetchone()
    div_name = div[0] if div else "UNKNOWN"
    print(f"  - {dept_name} (Dept ID: {dept_id}, Division: {div_name})")

conn.close()
print(f"\n{'='*80}")
