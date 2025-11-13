"""Integration test script for frontend-backend connection."""
import requests
import time
import sys

BACKEND_URL = "http://localhost:8000/api/v1"
FRONTEND_URL = "http://localhost:8080"

def test_backend():
    """Test if backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Backend is running: {data}")
            return True
        else:
            print(f"[FAIL] Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Backend is not running: {e}")
        return False

def test_frontend():
    """Test if frontend is running."""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print(f"[PASS] Frontend is running at {FRONTEND_URL}")
            return True
        else:
            print(f"[FAIL] Frontend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Frontend is not running: {e}")
        return False

def test_api_proxy():
    """Test if frontend can proxy API calls to backend."""
    try:
        # Test through frontend proxy (if configured)
        response = requests.get(f"{FRONTEND_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("[PASS] API proxy is working (frontend -> backend)")
            return True
        else:
            print(f"[WARN] API proxy returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[WARN] API proxy test failed: {e}")
        print("   (This is okay if proxy is not configured for direct testing)")
        return False

def main():
    """Run integration tests."""
    print("=" * 60)
    print("Frontend-Backend Integration Test")
    print("=" * 60)
    print()
    
    # Test backend
    print("Testing backend...")
    backend_ok = test_backend()
    print()
    
    # Test frontend
    print("Testing frontend...")
    frontend_ok = test_frontend()
    print()
    
    # Test API proxy
    print("Testing API proxy...")
    proxy_ok = test_api_proxy()
    print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Backend: {'[PASS] Running' if backend_ok else '[FAIL] Not Running'}")
    print(f"Frontend: {'[PASS] Running' if frontend_ok else '[FAIL] Not Running'}")
    print(f"API Proxy: {'[PASS] Working' if proxy_ok else '[WARN] Not Tested'}")
    print()
    
    if backend_ok and frontend_ok:
        print("[SUCCESS] Both servers are running!")
        print()
        print("You can now:")
        print(f"  1. Open frontend: {FRONTEND_URL}")
        print(f"  2. Check backend API docs: http://localhost:8000/docs")
        print("  3. Test the upload -> analyze -> estimate workflow")
    else:
        print("[WARN] Some servers are not running.")
        print()
        print("To start servers:")
        print("  Backend: python run.py")
        print("  Frontend: cd apps/web && npm run dev")

if __name__ == "__main__":
    main()

