"""Make direct HTTP call to test login"""
import sys
import json

try:
    import requests
except ImportError:
    print("requests library not found, installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# Try login with known working credentials
url = "http://localhost:8001/auth/login"
credentials = {
    "username": "ems_division_manager",
    "password": "password123"
}

print(f"Testing login at: {url}")
print(f"Username: {credentials['username']}")
print(f"Password: {credentials['password']}")
print("="*80)

try:
    response = requests.post(url, data=credentials, timeout=5)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"\nResponse Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    
    if response.status_code == 200:
        print("\n" + "="*80)
        print("SUCCESS! Login endpoint is working!")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("FAILED! Login returned error")
        print("="*80)
        
except requests.exceptions.ConnectionError:
    print("\nERROR: Could not connect to backend server!")
    print("Make sure backend is running on port 8001")
except Exception as e:
    print(f"\nERROR: {e}")
