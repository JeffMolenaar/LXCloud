#!/usr/bin/env python3
"""
Test script for new LXCloud admin features and controller management
Tests the new API endpoints and functionality
"""

import requests
import json
import sys
import time
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:5000"
ADMIN_KEY = "lxcloud-admin-setup-2024"

def test_admin_creation():
    """Test creating initial admin account"""
    print("Testing admin account creation...")
    
    admin_data = {
        "username": f"admin_{int(time.time())}",
        "email": f"admin_{int(time.time())}@example.com",
        "password": "admin123456",
        "admin_key": ADMIN_KEY
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/admin/create-admin", json=admin_data, timeout=5)
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Admin account created - User: {data.get('user', {}).get('username')}")
            return True, admin_data
        else:
            print(f"✗ Admin creation failed - Status: {response.status_code}, Response: {response.text}")
            return False, None
    except requests.exceptions.RequestException as e:
        print(f"✗ Admin creation failed - Error: {e}")
        return False, None

def test_controller_registration():
    """Test controller self-registration"""
    print("Testing controller registration...")
    
    controller_data = {
        "serial_number": f"CTRL_{int(time.time())}",
        "latitude": 52.3676,
        "longitude": 4.9041
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/controller/register", json=controller_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Controller registered - SN: {controller_data['serial_number']}")
            return True, controller_data
        else:
            print(f"✗ Controller registration failed - Status: {response.status_code}, Response: {response.text}")
            return False, None
    except requests.exceptions.RequestException as e:
        print(f"✗ Controller registration failed - Error: {e}")
        return False, None

def test_user_login(user_data):
    """Test user login and return session"""
    print("Testing user login...")
    
    try:
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/login",
            json={
                "username": user_data["username"],
                "password": user_data["password"]
            },
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Login successful - User: {data.get('user', {}).get('username')}")
            return True, session
        else:
            print(f"✗ Login failed - Status: {response.status_code}, Response: {response.text}")
            return False, None
    except requests.exceptions.RequestException as e:
        print(f"✗ Login failed - Error: {e}")
        return False, None

def test_admin_get_screens(session):
    """Test admin getting all screens and unassigned controllers"""
    print("Testing admin screen view...")
    
    try:
        response = session.get(f"{BASE_URL}/api/screens", timeout=5)
        if response.status_code == 200:
            data = response.json()
            screens = data.get('screens', [])
            controllers = data.get('unassigned_controllers', [])
            print(f"✓ Admin screen view successful - {len(screens)} screens, {len(controllers)} unassigned controllers")
            return True
        else:
            print(f"✗ Admin screen view failed - Status: {response.status_code}, Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Admin screen view failed - Error: {e}")
        return False

def test_regular_user_registration():
    """Test regular user registration"""
    print("Testing regular user registration...")
    
    user_data = {
        "username": f"user_{int(time.time())}",
        "email": f"user_{int(time.time())}@example.com",
        "password": "user123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/register", json=user_data, timeout=5)
        if response.status_code == 201:
            data = response.json()
            print(f"✓ User registration successful - User: {data.get('user', {}).get('username')}")
            return True, user_data
        else:
            print(f"✗ User registration failed - Status: {response.status_code}, Response: {response.text}")
            return False, None
    except requests.exceptions.RequestException as e:
        print(f"✗ User registration failed - Error: {e}")
        return False, None

def test_screen_assignment(session, controller_data):
    """Test assigning controller to user"""
    print("Testing screen assignment...")
    
    screen_data = {
        "serial_number": controller_data["serial_number"],
        "custom_name": "Test Screen"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/screens", json=screen_data, timeout=5)
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Screen assignment successful - Screen: {data.get('screen', {}).get('serial_number')}")
            return True
        else:
            print(f"✗ Screen assignment failed - Status: {response.status_code}, Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Screen assignment failed - Error: {e}")
        return False

def test_duplicate_assignment(session, controller_data):
    """Test preventing duplicate assignment"""
    print("Testing duplicate assignment prevention...")
    
    screen_data = {
        "serial_number": controller_data["serial_number"],
        "custom_name": "Duplicate Test"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/screens", json=screen_data, timeout=5)
        if response.status_code == 400:
            print("✓ Duplicate assignment correctly prevented")
            return True
        else:
            print(f"✗ Duplicate assignment not prevented - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Duplicate assignment test failed - Error: {e}")
        return False

def main():
    """Run all tests"""
    print("LXCloud New Features Tests")
    print("=" * 50)
    print(f"Testing against: {BASE_URL}")
    print()
    
    tests_passed = 0
    total_tests = 7
    
    # Test 1: Controller registration
    controller_success, controller_data = test_controller_registration()
    if controller_success:
        tests_passed += 1
    print()
    
    # Test 2: Admin account creation
    admin_success, admin_data = test_admin_creation()
    if admin_success:
        tests_passed += 1
    print()
    
    # Test 3: Admin login
    admin_session = None
    if admin_data:
        login_success, admin_session = test_user_login(admin_data)
        if login_success:
            tests_passed += 1
        print()
    
    # Test 4: Admin screen view
    if admin_session:
        admin_view_success = test_admin_get_screens(admin_session)
        if admin_view_success:
            tests_passed += 1
        print()
    
    # Test 5: Regular user registration
    user_success, user_data = test_regular_user_registration()
    if user_success:
        tests_passed += 1
    print()
    
    # Test 6: User login and screen assignment
    user_session = None
    if user_data and controller_data:
        login_success, user_session = test_user_login(user_data)
        if login_success and user_session:
            assignment_success = test_screen_assignment(user_session, controller_data)
            if assignment_success:
                tests_passed += 1
        print()
    
    # Test 7: Duplicate assignment prevention
    if user_session and controller_data:
        duplicate_success = test_duplicate_assignment(user_session, controller_data)
        if duplicate_success:
            tests_passed += 1
        print()
    
    # Results
    print("=" * 50)
    print(f"New Features Tests: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("✓ All new feature tests passed!")
        return 0
    else:
        print("✗ Some new feature tests failed.")
        print("\nNote: These tests require the LXCloud backend to be running.")
        print("Start it with: cd backend && python3 app.py")
        return 1

if __name__ == "__main__":
    exit(main())