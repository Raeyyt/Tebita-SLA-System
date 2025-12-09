import requests
import sys

# API_URL = "http://localhost:8008" # Using the last known good port
API_URL = "http://localhost:8008"

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

def check_incoming():
    print("Logging in as ems_division_manager...")
    token = login("ems_division_manager", "password123")
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}
    print("Fetching /requests/incoming...")
    try:
        response = requests.get(f"{API_URL}/requests/incoming", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Success! Count: {len(response.json())}")
            print(response.json())
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    check_incoming()
