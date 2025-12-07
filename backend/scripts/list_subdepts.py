"""Check what subdepartments currently exist"""
import sqlite3

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

# Get all subdepartments with their departments
cursor.execute("""
    SELECT s.name, d.name, div.name
    FROM subdepartments s
    JOIN departments d ON s.department_id = d.id
    JOIN divisions div ON d.division_id = div.id
    ORDER BY div.name, d.name, s.name
""")

subdepts = cursor.fetchall()

print(f"Current Sub-Departments ({len(subdepts)} total):\n")
print(f"{'Sub-Department':<40} | {'Department':<30} | {'Division'}")
print("="*100)

for subdept, dept, div in subdepts:
    print(f"{subdept:<40} | {dept:<30} | {div}")

# Also show departments
print("\n\nDepartments in system:")
cursor.execute("SELECT name FROM departments ORDER BY name")
for (name,) in cursor.fetchall():
    print(f"  - {name}")

conn.close()
