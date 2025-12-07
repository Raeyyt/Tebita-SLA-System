"""Quick backend connectivity test"""
import requests
import time

print("="*80)
print("BACKEND CONNECTIVITY TEST")
print("="*80)

# Test if backend is responding
backend_url = "http://127.0.0.1:8001"
endpoints_to_test = [
    "/",
    "/docs",
    "/auth/login"
]

for endpoint in endpoints_to_test:
    url = f"{backend_url}{endpoint}"
    try:
        print(f"\nTesting: {url}")
        response = requests.get(url, timeout=2)
        print(f"✅ Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection refused - backend NOT running on {backend_url}")
        print("\nPlease start the backend with:")
        print("  cd backend")
        print("  .venv\\Scripts\\activate")
        print("  python run.py")
        break
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "="*80)
