"""Debug acknowledge request failure"""
import requests
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8001"
USERNAME = "it_department"  # The user trying to acknowledge
PASSWORD = "password123"
REQUEST_ID = "REQ-GEN-20251204-001"  # From screenshot

print("="*80)
print(f"DEBUGGING ACKNOWLEDGE FAILURE FOR {REQUEST_ID}")
print("="*80)

# 1. Login
print(f"\n1. Logging in as {USERNAME}...")
try:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        sys.exit(1)
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
except Exception as e:
    print(f"❌ Connection error: {e}")
    sys.exit(1)

# 2. Get Request Details (to find internal ID)
print(f"\n2. Finding internal ID for {REQUEST_ID}...")
try:
    response = requests.get(f"{BASE_URL}/api/requests", headers=headers)
    requests_data = response.json()
    
    target_request = None
    for r in requests_data:
        if r["request_id"] == REQUEST_ID:
            target_request = r
            break
            
    if not target_request:
        print(f"❌ Request {REQUEST_ID} not found in user's view!")
        print("Available requests:")
        for r in requests_data[:3]:
            print(f"  - {r['request_id']}")
        sys.exit(1)
        
    internal_id = target_request["id"]
    print(f"✅ Found request! Internal ID: {internal_id}")
    print(f"   Status: {target_request['status']}")
    print(f"   Assigned Dept ID: {target_request['assigned_department_id']}")
    print(f"   Assigned User ID: {target_request['assigned_to_user_id']}")
    
except Exception as e:
    print(f"❌ Error fetching requests: {e}")
    sys.exit(1)

# 3. Attempt Acknowledge
print(f"\n3. Attempting to acknowledge request {internal_id}...")
try:
    url = f"{BASE_URL}/api/requests/{internal_id}/acknowledge"
    print(f"   POST {url}")
    
    response = requests.post(url, headers=headers)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! Request acknowledged.")
    else:
        print("\n❌ FAILURE! See error details above.")
        
except Exception as e:
    print(f"❌ Error calling acknowledge endpoint: {e}")

print("\n" + "="*80)
