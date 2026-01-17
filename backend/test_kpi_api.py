from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models import User, UserRole
import json

client = TestClient(app)

# Mock user for authentication
def get_test_token():
    # We need a real token or to mock the dependency
    # Let's try to find an admin user in the DB
    from app.database import SessionLocal
    db = SessionLocal()
    admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    db.close()
    
    if not admin:
        return None
    
    # We can't easily generate a JWT without the secret key and logic
    # But we can mock the get_current_active_user dependency
    return admin.username

# Instead of real HTTP calls, let's use a script that calls the logic directly or mocks the user
import unittest
from unittest.mock import patch

def test_kpi_endpoints():
    # Mocking get_current_active_user to return an admin
    from app.database import SessionLocal
    db = SessionLocal()
    admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    db.close()
    
    if not admin:
        print("No admin user found in database.")
        return

    app.dependency_overrides[app.dependencies[0]] = lambda: admin # This is not quite right for FastAPI

    # Let's just use the TestClient and override the auth dependency
    from app.auth import get_current_active_user
    app.dependency_overrides[get_current_active_user] = lambda: admin

    endpoints = [
        "/kpis/dashboard",
        "/kpis/metrics?period=month",
        "/kpis/scorecard?period=month",
        "/analytics/dashboard?days=30"
    ]

    for endpoint in endpoints:
        print(f"\n--- Testing {endpoint} ---")
        response = client.get(f"/api{endpoint}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response Data:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    test_kpi_endpoints()
