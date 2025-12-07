"""Cleanup duplicate Pharmaceutical Import departments"""
import sqlite3

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

print("="*80)
print("CLEANING UP DUPLICATE PHARMACEUTICAL IMPORT DEPARTMENTS")
print("="*80)

# Identify the correct and incorrect departments
# Correct one should be in MEDCOM division (ID 2)
cursor.execute("SELECT id FROM divisions WHERE name LIKE '%MEDCOM%'")
medcom_id = cursor.fetchone()[0]

cursor.execute("SELECT id, name, division_id FROM departments WHERE name LIKE '%Pharmaceutical%'")
depts = cursor.fetchall()

correct_id = None
duplicates = []

for d in depts:
    if d[2] == medcom_id:
        correct_id = d[0]
        print(f"✅ KEEPING: ID {d[0]} ({d[1]}) - In MEDCOM Division")
    else:
        duplicates.append(d[0])
        print(f"❌ REMOVING: ID {d[0]} ({d[1]}) - Wrong/No Division")

if not correct_id:
    print("❌ Could not find correct department in MEDCOM division!")
    # Fallback: keep the first one and assign to MEDCOM
    correct_id = depts[0][0]
    duplicates = [d[0] for d in depts[1:]]
    print(f"⚠️ Fallback: Keeping ID {correct_id} and moving to MEDCOM")
    cursor.execute("UPDATE departments SET division_id = ? WHERE id = ?", (medcom_id, correct_id))

if not duplicates:
    print("\n✅ No duplicates found!")
else:
    print(f"\nFound {len(duplicates)} duplicates to remove:")
    for dup_id in duplicates:
        print(f"  - Processing Duplicate ID {dup_id}...")
        
        # Reassign users
        cursor.execute("UPDATE users SET department_id = ? WHERE department_id = ?", (correct_id, dup_id))
        if cursor.rowcount > 0:
            print(f"    Reassigned {cursor.rowcount} users")
            
        # Reassign requests (requester)
        cursor.execute("UPDATE requests SET requester_department_id = ? WHERE requester_department_id = ?", (correct_id, dup_id))
        if cursor.rowcount > 0:
            print(f"    Reassigned {cursor.rowcount} requests (requester)")

        # Reassign requests (assigned)
        cursor.execute("UPDATE requests SET assigned_department_id = ? WHERE assigned_department_id = ?", (correct_id, dup_id))
        if cursor.rowcount > 0:
            print(f"    Reassigned {cursor.rowcount} requests (assigned)")
            
        # Reassign subdepartments
        cursor.execute("UPDATE subdepartments SET department_id = ? WHERE department_id = ?", (correct_id, dup_id))
        if cursor.rowcount > 0:
            print(f"    Reassigned {cursor.rowcount} subdepartments")

        # Delete duplicate
        cursor.execute("DELETE FROM departments WHERE id = ?", (dup_id,))
        print("    ✅ Deleted")

    conn.commit()
    print("\n✅ Cleanup complete!")

# Verify final state
cursor.execute("SELECT id, name, division_id FROM departments WHERE name LIKE '%Pharmaceutical%'")
final_depts = cursor.fetchall()
print(f"\nFinal Pharmaceutical Departments ({len(final_depts)}):")
for d in final_depts:
    print(f"  - ID {d[0]}: {d[1]} (Division ID: {d[2]})")

# Create sub-departments if missing
cursor.execute("SELECT count(*) FROM subdepartments WHERE department_id = ?", (correct_id,))
count = cursor.fetchone()[0]
if count == 0:
    print("\n⚠️ No sub-departments found! Creating defaults...")
    subs = ["Import Logistics", "Regulatory Affairs", "Procurement"]
    for s in subs:
        cursor.execute("INSERT INTO subdepartments (name, department_id) VALUES (?, ?)", (s, correct_id))
        print(f"  + Created '{s}'")
    conn.commit()
else:
    print(f"\n✅ Department has {count} sub-departments")

conn.close()
print("="*80)
