import requests

API_URL = "http://localhost:8000"

# Login as EMS Division Manager
response = requests.post(f"{API_URL}/auth/login", data={
    "username": "ems_division_manager",
    "password": "password123"
})
token = response.json()["access_token"]

# Get incoming requests
headers = {"Authorization": f"Bearer {token}"}
incoming = requests.get(f"{API_URL}/requests/incoming", headers=headers).json()

print(f"Incoming Requests Count: {len(incoming)}")

# Check for the problematic requests
problematic_ids = ['REQ-20251115-018', 'REQ-20251128-011']
problematic = [r for r in incoming if r['request_id'] in problematic_ids]

print(f"\nProblematic requests still showing: {len(problematic)}")
if problematic:
    for r in problematic:
        print(f"  - {r['request_id']}")
else:
    print("  None - FIXED!")

print(f"\nAll incoming requests:")
for r in incoming:
    print(f"  - {r['request_id']}: FROM div={r.get('requester_division_id')} TO div={r.get('assigned_division_id')}")
