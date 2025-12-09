import requests

API_URL = "http://localhost:8000"

# Login as MEDCOM Division Manager
response = requests.post(f"{API_URL}/auth/login", data={
    "username": "medcom_division_manager",
    "password": "password123"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get notification count
notif_resp = requests.get(f"{API_URL}/notifications/unread-count", headers=headers)
notif_count = notif_resp.json()["count"]

# Get incoming requests
incoming_resp = requests.get(f"{API_URL}/requests/incoming", headers=headers)
incoming = incoming_resp.json()

print(f"Notification Count (Badge): {notif_count}")
print(f"Actual Incoming Requests: {len(incoming)}")
print(f"\nMismatch: {notif_count != len(incoming)}")

if notif_count != len(incoming):
    print(f"\nIncoming Request Details:")
    for i, req in enumerate(incoming[:10], 1):
        print(f"  {i}. ID: {req['request_id']}, Status: {req['status']}")
