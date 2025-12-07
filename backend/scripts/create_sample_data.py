"""Create sample requests for testing if database is empty"""
import sqlite3
from datetime import datetime
import random

conn = sqlite3.connect('tebita.db')
cursor = conn.cursor()

# Check current request count
cursor.execute("SELECT COUNT(*) FROM requests")
current_count = cursor.fetchone()[0]

print(f"Current requests in database: {current_count}")

if current_count == 0:
    print("\nDatabase is empty! Creating sample requests...")
    
    # Get some users
    cursor.execute("SELECT id FROM users LIMIT 5")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    # Get divisions, departments, subdepartments
    cursor.execute("SELECT id FROM divisions")
    division_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM departments")
    dept_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM subdepartments")
    subdept_ids = [row[0] for row in cursor.fetchall()]
    
    if not user_ids or not division_ids or not dept_ids:
        print("ERROR: No users, divisions, or departments found!")
        conn.close()
        exit(1)
    
    # Create 10 sample requests
    statuses = ['PENDING', 'IN_PROGRESS', 'COMPLETED']
    priorities = ['HIGH', 'MEDIUM', 'LOW']
    
    for i in range(10):
        request_id = f"REQ-{datetime.now().strftime('%Y%m%d')}-{1000+i}"
        requester_id = random.choice(user_ids)
        assigned_div = random.choice(division_ids)
        assigned_dept = random.choice(dept_ids)
        status = random.choice(statuses)
        priority = random.choice(priorities)
        
        cursor.execute("""
            INSERT INTO requests (
                request_id, requester_id, assigned_division_id, 
                assigned_department_id, status, priority, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            request_id,
            requester_id,
            assigned_div,
            assigned_dept,
            status,
            priority,
            datetime.now()
        ))
    
    conn.commit()
    print(f"✅ Created 10 sample requests!")
else:
    print("✅ Database already has requests - no need to create samples")

conn.close()
