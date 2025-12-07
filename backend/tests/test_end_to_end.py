"""
Comprehensive end-to-end test: Login → Fetch Requests → Display Structure
This will tell us exactly where the problem is
"""
import requests
import json

print("="*80)
print("END-TO-END DATA FLOW TEST")
print("="*80)

# Step 1: Login
print("\n[STEP 1] Testing login...")
try:
    login_response = requests.post(
        "http://127.0.0.1:8001/auth/login",
        data={"username": "ems_division_manager", "password": "test123"},
        timeout=5
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        exit(1)
    
    token = login_response.json()["access_token"]
    print(f"✅ Login successful")
    
except Exception as e:
    print(f"❌ Login error: {e}")
    exit(1)

# Step 2: Fetch user profile
print("\n[STEP 2] Fetching user profile...")
try:
    profile_response = requests.get(
        "http://127.0.0.1:8001/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5
    )
    
    if profile_response.status_code != 200:
        print(f"❌ Profile fetch failed: {profile_response.status_code}")
        print(profile_response.text)
    else:
        user_data = profile_response.json()
        print(f"✅ User: {user_data.get('full_name')} ({user_data.get('role')})")
        print(f"   Division ID: {user_data.get('division_id')}")
        print(f"   Department ID: {user_data.get('department_id')}")
        print(f"   Sub-Dept ID: {user_data.get('subdepartment_id')}")
        
except Exception as e:
    print(f"❌ Profile error: {e}")

# Step 3: Fetch requests
print("\n[STEP 3] Fetching requests...")
try:
    requests_response = requests.get(
        "http://127.0.0.1:8001/requests",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5
    )
    
    print(f"Status Code: {requests_response.status_code}")
    
    if requests_response.status_code != 200:
        print(f"❌ Requests fetch failed")
        print(f"Response: {requests_response.text[:500]}")
    else:
        data = requests_response.json()
        print(f"✅ API returned {len(data)} requests")
        
        if len(data) == 0:
            print("\n⚠️  PROBLEM FOUND: API returned empty list!")
            print("This means role-based filtering is too restrictive OR no matching data")
        else:
            print(f"\n✅ DATA IS AVAILABLE! Showing first request:")
            first_req = data[0]
            print(f"   Request ID: {first_req.get('request_id')}")
            print(f"   Status: {first_req.get('status')}")
            print(f"   Priority: {first_req.get('priority')}")
            print(f"   Requester: {first_req.get('requester', {}).get('full_name', 'N/A')}")
            print(f"\n   Full structure (first 800 chars):")
            print(json.dumps(first_req, indent=2)[:800])
            
except Exception as e:
    print(f"❌ Requests error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("DIAGNOSTIC COMPLETE")
print("="*80)
