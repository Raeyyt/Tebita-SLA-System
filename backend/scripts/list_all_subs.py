"""List all sub-departments"""
import sqlite3

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

print("="*80)
print("ALL SUB-DEPARTMENTS")
print("="*80)

cursor.execute("""
    SELECT s.id, s.name, d.name 
    FROM subdepartments s
    LEFT JOIN departments d ON s.department_id = d.id
    ORDER BY d.name, s.name
""")
subs = cursor.fetchall()

for s_id, s_name, d_name in subs:
    print(f"ID {s_id}: {s_name} (Dept: {d_name})")

conn.close()
print("="*80)
