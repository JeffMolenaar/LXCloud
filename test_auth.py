#!/usr/bin/env python3
"""
Test script for LXCloud authentication endpoints
Tests registration and login functionality
"""

import requests
import json
import sys
import time
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_USER = {
    "username": "testuser_" + str(int(time.time())),
    "email": f"test_{int(time.time())}@example.com",
    "password": "testpass123"
}

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed - Status: {data.get('status')}")
            return True
        else:
            print(f"✗ Health check failed - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Health check failed - Error: {e}")
        return False

def test_registration():
    """Test user registration"""
    print("Testing user registration...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/register",
            json=TEST_USER,
            timeout=5
        )
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Registration successful - User: {data.get('user', {}).get('username')}")
            return True, response.cookies
        else:
            print(f"✗ Registration failed - Status: {response.status_code}, Response: {response.text}")
            return False, None
    except requests.exceptions.RequestException as e:
        print(f"✗ Registration failed - Error: {e}")
        return False, None

def test_login(cookies=None):
    """Test user login"""
    print("Testing user login...")
    try:
        session = requests.Session()
        if cookies:
            session.cookies.update(cookies)
            
        response = session.post(
            f"{BASE_URL}/api/login",
            json={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            },
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Login successful - User: {data.get('user', {}).get('username')}")
            return True, session.cookies
        else:
            print(f"✗ Login failed - Status: {response.status_code}, Response: {response.text}")
            return False, None
    except requests.exceptions.RequestException as e:
        print(f"✗ Login failed - Error: {e}")
        return False, None

def test_get_user(cookies):
    """Test get current user endpoint"""
    print("Testing get current user...")
    try:
        session = requests.Session()
        session.cookies.update(cookies)
        
        response = session.get(f"{BASE_URL}/api/user", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Get user successful - User: {data.get('user', {}).get('username')}")
            return True
        else:
            print(f"✗ Get user failed - Status: {response.status_code}, Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Get user failed - Error: {e}")
        return False

def test_logout(cookies):
    """Test user logout"""
    print("Testing user logout...")
    try:
        session = requests.Session()
        session.cookies.update(cookies)
        
        response = session.post(f"{BASE_URL}/api/logout", timeout=5)
        if response.status_code == 200:
            print("✓ Logout successful")
            return True
        else:
            print(f"✗ Logout failed - Status: {response.status_code}, Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Logout failed - Error: {e}")
        return False

def main():
    """Run authentication tests"""
    print("LXCloud Authentication Tests")
    print("=" * 40)
    print(f"Testing against: {BASE_URL}")
    print(f"Test user: {TEST_USER['username']}")
    print()
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Health check
    if test_health_check():
        tests_passed += 1
    print()
    
    # Test 2: Registration
    reg_success, reg_cookies = test_registration()
    if reg_success:
        tests_passed += 1
    print()
    
    # Test 3: Login
    login_success, login_cookies = test_login()
    if login_success:
        tests_passed += 1
        cookies_to_use = login_cookies
    elif reg_cookies:
        cookies_to_use = reg_cookies
    else:
        cookies_to_use = None
    print()
    
    # Test 4: Get current user
    if cookies_to_use and test_get_user(cookies_to_use):
        tests_passed += 1
    print()
    
    # Test 5: Logout
    if cookies_to_use and test_logout(cookies_to_use):
        tests_passed += 1
    print()
    
    # Results
    print("=" * 40)
    print(f"Authentication Tests: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("✓ All authentication tests passed!")
        return 0
    else:
        print("✗ Some authentication tests failed.")
        print("\nNote: These tests require the LXCloud backend to be running.")
        print("Start it with: cd backend && python3 app.py")
        return 1

if __name__ == "__main__":
    exit(main())