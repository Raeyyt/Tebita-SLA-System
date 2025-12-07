import requests
import sys

BASE_URL = "http://localhost:8001"

def get_token():
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": "admin", "password": "password123"}
        )
        if response.status_code != 200:
            print(f"Failed to login: {response.text}")
            return None
        return response.json()["access_token"]
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def test_dashboard(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/analytics/dashboard?days=30", headers=headers)
        
        if response.status_code == 200:
            print("✅ Dashboard API Success!")
            data = response.json()
            print(f"Keys: {list(data.keys())}")
            print(f"Scorecard keys: {list(data['scorecard'].keys())}")
            print(f"Integration Index keys: {list(data['integration_index'].keys())}")
        else:
            print(f"❌ Dashboard API Failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    print("Testing Analytics API...")
    token = get_token()
    if token:
        test_dashboard(token)
    else:
        print("Skipping dashboard test due to login failure")
