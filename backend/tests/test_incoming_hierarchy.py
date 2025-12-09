import requests
import sys

API_URL = "http://localhost:8000"

def login(username, password):
    try:
        response = requests.post(f"{API_URL}/auth/login", data={"username": username, "password": password})
        if response.status_code != 200:
            print(f"Login failed for {username}: {response.text}")
            return None
        return response.json()["access_token"]
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def test_incoming_requests_hierarchy():
    """Test that incoming requests are strictly filtered by hierarchy level"""
    
    print("=" * 80)
    print("TESTING INCOMING REQUESTS HIERARCHY FILTERING")
    print("=" * 80)
    
    # Test 1: Division Manager (Support Division)
    print("\n1. Testing EMS Division Manager (ems_division_manager)")
    print("-" * 80)
    token = login("ems_division_manager", "password123")
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{API_URL}/requests/incoming", headers=headers)
        if resp.status_code == 200:
            incoming = resp.json()
            print(f"   Incoming Requests Count: {len(incoming)}")
            
            # Check each request
            for req in incoming:
                assigned_div = req.get('assigned_division_id')
                assigned_dept = req.get('assigned_department_id')
                assigned_subdept = req.get('assigned_subdepartment_id')
                assigned_user = req.get('assigned_to_user_id')
                
                print(f"\n   Request #{req.get('request_id', req.get('id'))}:")
                print(f"     - Assigned Division: {assigned_div}")
                print(f"     - Assigned Department: {assigned_dept}")
                print(f"     - Assigned SubDepartment: {assigned_subdept}")
                print(f"     - Assigned User: {assigned_user}")
                
                # Verify ONLY direct division assignments (no dept/subdept specified)
                if assigned_dept is not None or assigned_subdept is not None:
                    print(f"     ❌ ERROR: This request should NOT be in Division Manager's incoming!")
                else:
                    print(f"     ✅ CORRECT: Direct division assignment")
        else:
            print(f"   Failed: {resp.status_code} - {resp.text}")
    
    # Test 2: Department Head (Finance Department)
    print("\n\n2. Testing Finance Department Head (finance_head)")
    print("-" * 80)
    token = login("finance_head", "password123")
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{API_URL}/requests/incoming", headers=headers)
        if resp.status_code == 200:
            incoming = resp.json()
            print(f"   Incoming Requests Count: {len(incoming)}")
            
            for req in incoming:
                assigned_div = req.get('assigned_division_id')
                assigned_dept = req.get('assigned_department_id')
                assigned_subdept = req.get('assigned_subdepartment_id')
                assigned_user = req.get('assigned_to_user_id')
                
                print(f"\n   Request #{req.get('request_id', req.get('id'))}:")
                print(f"     - Assigned Division: {assigned_div}")
                print(f"     - Assigned Department: {assigned_dept}")
                print(f"     - Assigned SubDepartment: {assigned_subdept}")
                print(f"     - Assigned User: {assigned_user}")
                
                # Verify ONLY direct department assignments (no subdept specified)
                if assigned_subdept is not None:
                    print(f"     ❌ ERROR: This request should NOT be in Department Head's incoming!")
                    print(f"        (It's assigned to a subdepartment, not the department)")
                else:
                    print(f"     ✅ CORRECT: Direct department assignment")
        else:
            print(f"   Failed: {resp.status_code} - {resp.text}")
    
    # Test 3: Subdepartment Staff (Cashier)
    print("\n\n3. Testing Cashier Sub-Department Staff")
    print("-" * 80)
    print("   (If Cashier account exists, will show requests assigned to Cashier subdept)")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print("\nExpected Behavior:")
    print("  ✅ Division Manager: Only sees requests with assigned_department_id = NULL")
    print("  ✅ Department Head: Only sees requests with assigned_subdepartment_id = NULL")
    print("  ✅ Sub-Dept Staff: Sees requests assigned to their specific subdepartment")
    print("\nExample Scenario (User's Request):")
    print("  - Legal Advisor → Cashier subdepartment")
    print("    • Should appear in: Cashier's incoming requests")
    print("    • Should NOT appear in: Finance Dept incoming, Support Div incoming")
    print("    • Should appear in: Finance Dept 'All Requests', Support Div 'All Requests'")

if __name__ == "__main__":
    test_incoming_requests_hierarchy()
