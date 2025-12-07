"""Create sub-departments for MEDCOM"""
import sqlite3

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

print("="*80)
print("CREATING MEDCOM SUB-DEPARTMENTS")
print("="*80)

# Define sub-departments to create
new_subs = [
    # Medical Equipment Production (ID 7)
    (7, "Assembly Line"),
    (7, "Quality Control"),
    (7, "Maintenance"),
    
    # Pharmaceutical Production (ID 8)
    (8, "Formulation"),
    (8, "Packaging"),
    (8, "Quality Assurance")
]

created_count = 0

for dept_id, sub_name in new_subs:
    # Check if exists
    cursor.execute("SELECT id FROM subdepartments WHERE department_id = ? AND name = ?", (dept_id, sub_name))
    exists = cursor.fetchone()
    
    if not exists:
        cursor.execute("INSERT INTO subdepartments (name, department_id) VALUES (?, ?)", (sub_name, dept_id))
        print(f"✅ Created '{sub_name}' for Dept ID {dept_id}")
        created_count += 1
    else:
        print(f"⚠️ '{sub_name}' already exists for Dept ID {dept_id}")

conn.commit()
conn.close()

print("\n" + "="*80)
print(f"✅ Created {created_count} new sub-departments!")
print("="*80)
