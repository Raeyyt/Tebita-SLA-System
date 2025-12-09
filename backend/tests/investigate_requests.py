import sqlite3
import sys

DB_PATH = "backend/tebita.db"

def investigate_requests():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    request_ids = ['REQ-20251115-018', 'REQ-20251128-011']
    
    print("=" * 100)
    print("INVESTIGATING INCOMING REQUESTS ISSUE")
    print("=" * 100)
    
    for req_id in request_ids:
        print(f"\n{'=' * 100}")
        print(f"Request: {req_id}")
        print("=" * 100)
        
        cursor.execute("""
            SELECT 
                id,
                request_id,
                requester_id,
                requester_division_id,
                requester_department_id,
                requester_subdepartment_id,
                assigned_division_id,
                assigned_department_id,
                assigned_subdepartment_id,
                assigned_to_user_id,
                status
            FROM requests
            WHERE request_id = ?
        """, (req_id,))
        
        row = cursor.fetchone()
        
        if row:
            print(f"\n  Database ID: {row[0]}")
            print(f"  Request ID: {row[1]}")
            print(f"\n  REQUESTER INFO:")
            print(f"    - Requester User ID: {row[2]}")
            print(f"    - Requester Division ID: {row[3]}")
            print(f"    - Requester Department ID: {row[4]}")
            print(f"    - Requester SubDepartment ID: {row[5]}")
            print(f"\n  ASSIGNMENT INFO:")
            print(f"    - Assigned Division ID: {row[6]}")
            print(f"    - Assigned Department ID: {row[7]}")
            print(f"    - Assigned SubDepartment ID: {row[8]}")
            print(f"    - Assigned to User ID: {row[9]}")
            print(f"\n  STATUS: {row[10]}")
            
            # Check if this should appear for EMS Division Manager
            print(f"\n  ANALYSIS FOR EMS DIVISION MANAGER:")
            
            # Get EMS division ID
            cursor.execute("SELECT id FROM divisions WHERE name LIKE '%EMS%'")
            ems_div_result = cursor.fetchone()
            ems_div_id = ems_div_result[0] if ems_div_result else None
            print(f"    - EMS Division ID: {ems_div_id}")
            
            assigned_div = row[6]
            assigned_dept = row[7]
            assigned_subdept = row[8]
            assigned_user = row[9]
            
            if assigned_user:
                print(f"    [YES] SHOULD APPEAR: Directly assigned to user (assigned_to_user_id = {assigned_user})")
            elif assigned_div == ems_div_id and assigned_dept is None and assigned_subdept is None:
                print(f"    [YES] SHOULD APPEAR: Assigned directly to EMS Division (no dept/subdept)")
            elif assigned_div == ems_div_id and (assigned_dept is not None or assigned_subdept is not None):
                print(f"    [NO] SHOULD NOT APPEAR: Assigned to sub-level of EMS Division")
                print(f"       - Department ID: {assigned_dept}")
                print(f"       - SubDepartment ID: {assigned_subdept}")
            elif assigned_div != ems_div_id:
                print(f"    [NO] SHOULD NOT APPEAR: Assigned to different division (Division ID: {assigned_div})")
            else:
                print(f"    [UNKNOWN] UNEXPECTED CASE")
                
            # Check who the EMS division manager is
            cursor.execute("""
                SELECT id, username, full_name 
                FROM users 
                WHERE role = 'DIVISION_MANAGER' AND division_id = ?
            """, (ems_div_id,))
            div_manager = cursor.fetchone()
            if div_manager:
                print(f"\n  EMS DIVISION MANAGER:")
                print(f"    - User ID: {div_manager[0]}")
                print(f"    - Username: {div_manager[1]}")
                print(f"    - Full Name: {div_manager[2]}")
                
                # Check if request is assigned to this user
                if assigned_user == div_manager[0]:
                    print(f"    [YES] Request IS assigned to Division Manager user")
        else:
            print(f"  [NOT FOUND] REQUEST NOT FOUND in database")
    
    conn.close()
    
    print("\n" + "=" * 100)
    print("INVESTIGATION COMPLETE")
    print("=" * 100)

if __name__ == "__main__":
    investigate_requests()
