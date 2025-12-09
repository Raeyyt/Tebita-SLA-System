
import requests
import sys
import os

# Add parent dir to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_URL = "http://localhost:8008"

def login(username, password):
    try:
        response = requests.post(f"{API_URL}/auth/login", data={"username": username, "password": password})
        if response.status_code != 200:
            print(f"Login failed for {username}: {response.text}")
            return None
        return response.json()["access_token"]
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Is it running on port 8005?")
        return None

def check_visibility(role_name, username, password):
    print(f"\n--- Checking visibility for {role_name} ({username}) ---")
    token = login(username, password)
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 1. Dashboard Stats
    try:
        response = requests.get(f"{API_URL}/api/dashboard/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"Dashboard Stats: Total Requests = {stats.get('total_requests')}")
        else:
            print(f"Failed to get dashboard stats: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error getting dashboard stats: {e}")

    # 2. Incoming Requests
    try:
        response = requests.get(f"{API_URL}/requests/incoming", headers=headers)
        if response.status_code == 200:
            incoming = response.json()
            print(f"Incoming Requests: {len(incoming)}")
        else:
            print(f"Failed to get incoming requests: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error getting incoming requests: {e}")

    # 3. All Requests
    try:
        response = requests.get(f"{API_URL}/requests/", headers=headers)
        if response.status_code == 200:
            all_reqs = response.json()
            print(f"All Requests: {len(all_reqs)}")
        else:
            print(f"Failed to get all requests: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error getting all requests: {e}")

def main():
    # Admin (should see everything)
    check_visibility("ADMIN", "raeyyt", "password123") 

    # Division Manager
    check_visibility("DIVISION MANAGER", "ems_division_manager", "password123")

    # Department Head
    check_visibility("DEPARTMENT HEAD", "comprehensive_ambulance_services_head", "password123")

if __name__ == "__main__":
    main()
