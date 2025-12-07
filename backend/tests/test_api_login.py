"""Test the login endpoint directly"""
import requests

# Test with the backend on port 8001
url = "http://localhost:8001/auth/login"

# Test credentials
test_credentials = [
    ("ems_division_manager", "password123"),
    ("fleet_head", "password123"),
    ("finance_manager", "password123"),
]

print("Testing login endpoint at:", url)
print("="*80)

for username, password in test_credentials:
    print(f"\nTesting: {username} / {password}")
    
    # Prepare form data (OAuth2 format)
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  SUCCESS! Token received")
            json_data = response.json()
            if 'access_token' in json_data:
                print(f"  Token type: {json_data.get('token_type', 'N/A')}")
        else:
            print(f"  FAILED! Response: {response.text}")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "="*80)
