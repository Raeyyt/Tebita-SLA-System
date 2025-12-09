import requests
import sys

API_URL = "http://localhost:8009"

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

def verify_division_fixes():
    print("--- Verifying Division Dashboard Fixes ---")
    token = login("ems_division_manager", "password123")
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 1. Check Notifications (Unread Count)
    print("\n1. Checking Notifications (Unread Count)...")
    resp = requests.get(f"{API_URL}/notifications/unread-count", headers=headers)
    if resp.status_code == 200:
        print(f"   Notification Count: {resp.json()['count']}")
    else:
        print(f"   Failed: {resp.status_code} - {resp.text}")

    # 2. Check Incoming Requests (for comparison)
    print("\n2. Checking Incoming Requests...")
    resp = requests.get(f"{API_URL}/requests/incoming", headers=headers)
    if resp.status_code == 200:
        incoming_count = len(resp.json())
        print(f"   Incoming Requests Count: {incoming_count}")
    else:
        print(f"   Failed: {resp.status_code} - {resp.text}")

    # 3. Check M&E Dashboard Stats
    print("\n3. Checking M&E Dashboard Stats...")
    resp = requests.get(f"{API_URL}/me/dashboard", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        print(f"   Total Requests: {data['total_requests']}")
        print(f"   Pending: {data['status_breakdown']['pending']}")
        print(f"   Completed: {data['status_breakdown']['completed']}")
        print(f"   Division Stats: {len(data['division_stats'])} divisions shown")
    else:
        print(f"   Failed: {resp.status_code} - {resp.text}")

    # 4. Check SLA Compliance
    print("\n4. Checking SLA Compliance...")
    resp = requests.get(f"{API_URL}/sla/compliance", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        print(f"   Total Requests (SLA): {data['total_requests']}")
    else:
        print(f"   Failed: {resp.status_code} - {resp.text}")

    # 5. Check Department Ratings
    print("\n5. Checking Department Ratings (Analytics)...")
    resp = requests.get(f"{API_URL}/satisfaction/analytics/all-departments", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        print(f"   Total Departments Rated: {data['total_departments_rated']}")
        for dept in data['departments']:
            print(f"   - {dept['department_name']} (ID: {dept['department_id']})")
    else:
        print(f"   Failed: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    verify_division_fixes()
