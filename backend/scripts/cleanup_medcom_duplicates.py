"""Cleanup duplicate departments in MEDCOM"""
import sqlite3

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

print("="*80)
print("CLEANING UP DUPLICATE DEPARTMENTS IN MEDCOM")
print("="*80)

# Get MEDCOM division
cursor.execute("SELECT id, name FROM divisions WHERE name LIKE '%MEDCOM%'")
medcom = cursor.fetchone()

if not medcom:
    print("❌ MEDCOM Division not found!")
    exit()

div_id, div_name = medcom
print(f"Target Division: {div_name} (ID: {div_id})")

# Get all departments in MEDCOM
cursor.execute("SELECT id, name FROM departments WHERE division_id = ? ORDER BY id", (div_id,))
depts = cursor.fetchall()

print(f"\nFound {len(depts)} departments:")
for d in depts:
    print(f"  - ID {d[0]}: {d[1]}")

# Identify duplicates
seen_names = {}
duplicates = []

for dept_id, name in depts:
    if name in seen_names:
        original_id = seen_names[name]
        duplicates.append((dept_id, name, original_id))
    else:
        seen_names[name] = dept_id

if not duplicates:
    print("\n✅ No duplicates found!")
else:
    print(f"\nFound {len(duplicates)} duplicates to remove:")
    for dup_id, name, orig_id in duplicates:
        print(f"  - Removing ID {dup_id} ({name}) -> Keeping ID {orig_id}")
        
        # Reassign users
        cursor.execute("UPDATE users SET department_id = ? WHERE department_id = ?", (orig_id, dup_id))
        if cursor.rowcount > 0:
            print(f"    Reassigned {cursor.rowcount} users")
            
        # Reassign requests (requester)
        cursor.execute("UPDATE requests SET requester_department_id = ? WHERE requester_department_id = ?", (orig_id, dup_id))
        if cursor.rowcount > 0:
            print(f"    Reassigned {cursor.rowcount} requests (requester)")

        # Reassign requests (assigned)
        cursor.execute("UPDATE requests SET assigned_department_id = ? WHERE assigned_department_id = ?", (orig_id, dup_id))
        if cursor.rowcount > 0:
            print(f"    Reassigned {cursor.rowcount} requests (assigned)")
            
        # Reassign subdepartments
        cursor.execute("UPDATE subdepartments SET department_id = ? WHERE department_id = ?", (orig_id, dup_id))
        if cursor.rowcount > 0:
            print(f"    Reassigned {cursor.rowcount} subdepartments")

        # Delete duplicate
        cursor.execute("DELETE FROM departments WHERE id = ?", (dup_id,))
        print("    ✅ Deleted")

    conn.commit()
    print("\n✅ Cleanup complete!")

# Verify final state
cursor.execute("SELECT id, name FROM departments WHERE division_id = ? ORDER BY id", (div_id,))
final_depts = cursor.fetchall()
print(f"\nFinal Department List ({len(final_depts)}):")
for d in final_depts:
    print(f"  - ID {d[0]}: {d[1]}")

conn.close()
print("="*80)
