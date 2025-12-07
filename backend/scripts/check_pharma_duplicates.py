"""Check for duplicate Pharmaceutical Import departments"""
import sqlite3

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

print("="*80)
print("CHECKING PHARMACEUTICAL IMPORT DEPARTMENTS")
print("="*80)

# Search for departments with "Pharmaceutical" in the name
cursor.execute("SELECT id, name, division_id FROM departments WHERE name LIKE '%Pharmaceutical%'")
depts = cursor.fetchall()

print(f"Found {len(depts)} departments:")
for d in depts:
    div_name = "Unknown"
    if d[2]:
        cursor.execute("SELECT name FROM divisions WHERE id = ?", (d[2],))
        div = cursor.fetchone()
        if div:
            div_name = div[0]
            
    print(f"  - ID {d[0]}: {d[1]} (Division: {div_name})")
    
    # Check sub-departments
    cursor.execute("SELECT count(*) FROM subdepartments WHERE department_id = ?", (d[0],))
    count = cursor.fetchone()[0]
    print(f"    Sub-departments: {count}")

conn.close()
print("="*80)
