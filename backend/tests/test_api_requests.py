"""Test if the API endpoint returns requests"""
import requests
import json

# First login to get a token
login_url = "http://127.0.0.1:8001/auth/login"
login_data = {
    "username": "ems_division_manager",
    "password": "test123"
}

print("="*80)
print("API ENDPOINT TEST")
print("="*80)

try:
    # Login
    print("\n1. Logging in...")
    login_response = requests.post(login_url, data=login_data, timeout=5)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        exit(1)
    
    token = login_response.json()["access_token"]
    print(f"✅ Login successful! Got token")
    
    # Test requests endpoint
    print("\n2. Testing /requests endpoint...")
    requests_url = "http://127.0.0.1:8001/requests"
    headers = {"Authorization": f"Bearer {token}"}
    
    requests_response = requests.get(requests_url, headers=headers, timeout=5)
    
    print(f"Status Code: {requests_response.status_code}")
    
    if requests_response.status_code == 200:
        data = requests_response.json()
        print(f"✅ API returned {len(data)} requests")
        
        if len(data) > 0:
            print("\nSample request structure:")
            print(json.dumps(data[0], indent=2)[:500] + "...")
        else:
            print("⚠️  API returned empty list!")
    else:
        print(f"❌ API error: {requests_response.status_code}")
        print(requests_response.text[:500])
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Could not connect to backend!")
    print("Make sure backend is running on port 8001")
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n" + "="*80)
