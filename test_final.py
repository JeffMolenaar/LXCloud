#!/usr/bin/env python3
"""
Final test script for LXCloud backend functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_basic_functionality():
    """Test basic backend functionality"""
    print("Testing LXCloud Backend Functionality")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 6
    
    # Test 1: Health check
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ Health check passed")
            tests_passed += 1
        else:
            print("✗ Health check failed")
    except:
        print("✗ Health check failed")
    
    # Test 2: Version check
    try:
        response = requests.get(f"{BASE_URL}/api/version", timeout=5)
        if response.status_code == 200:
            print("✓ Version check passed")
            tests_passed += 1
        else:
            print("✗ Version check failed")
    except:
        print("✗ Version check failed")
    
    # Test 3: User registration
    test_user = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/register", json=test_user, timeout=5)
        if response.status_code in [200, 201]:
            print("✓ User registration passed")
            tests_passed += 1
            cookies = response.cookies
        else:
            print("✗ User registration failed")
            cookies = None
    except:
        print("✗ User registration failed")
        cookies = None
    
    # Test 4: User login
    try:
        response = requests.post(f"{BASE_URL}/api/login", json={
            "username": test_user["username"],
            "password": test_user["password"]
        }, timeout=5)
        if response.status_code == 200:
            print("✓ User login passed")
            tests_passed += 1
            login_cookies = response.cookies
        else:
            print("✗ User login failed")
            login_cookies = cookies
    except:
        print("✗ User login failed")
        login_cookies = cookies
    
    # Test 5: Get user info
    if login_cookies:
        try:
            response = requests.get(f"{BASE_URL}/api/user", cookies=login_cookies, timeout=5)
            if response.status_code == 200:
                print("✓ Get user info passed")
                tests_passed += 1
            else:
                print("✗ Get user info failed")
        except:
            print("✗ Get user info failed")
    else:
        print("✗ Get user info skipped (no login cookies)")
    
    # Test 6: Controller registration (no auth)
    try:
        response = requests.post(f"{BASE_URL}/api/controller/register", json={
            "serial_number": f"TEST_DEVICE_{int(time.time())}",
            "latitude": 52.3676,
            "longitude": 4.9041
        }, timeout=5)
        if response.status_code == 200:
            print("✓ Controller registration passed")
            tests_passed += 1
        else:
            print("✗ Controller registration failed")
    except:
        print("✗ Controller registration failed")
    
    print()
    print(f"Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✓ All tests passed! Backend is working correctly.")
        return True
    else:
        print("✗ Some tests failed.")
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    exit(0 if success else 1)