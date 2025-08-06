#!/usr/bin/env python3

"""
Test script to verify LXCloud backend functionality
Tests controller registration, admin creation, and basic API endpoints
"""

import requests
import json
import time
import hashlib

BASE_URL = "http://localhost:5000/api"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_controller_registration():
    """Test controller registration with authentication"""
    serial_number = "TEST001"
    auth_key = hashlib.sha256(f"lxcloud-controller-{serial_number}".encode()).hexdigest()[:16]
    
    data = {
        "serial_number": serial_number,
        "latitude": 52.3676,
        "longitude": 4.9041,
        "auth_key": auth_key
    }
    
    try:
        response = requests.post(f"{BASE_URL}/controller/register", json=data, timeout=5)
        print(f"Controller registration: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Controller registration failed: {e}")
        return False

def test_admin_creation():
    """Test admin account creation"""
    data = {
        "username": "admin",
        "email": "admin@example.com", 
        "password": "admin123",
        "admin_key": "lxcloud-admin-setup-2024"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/admin/create-admin", json=data, timeout=5)
        print(f"Admin creation: {response.status_code} - {response.json()}")
        return response.status_code in [200, 201, 400]  # 400 if admin already exists
    except Exception as e:
        print(f"Admin creation failed: {e}")
        return False

def test_version():
    """Test version endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/version", timeout=5)
        print(f"Version: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Version check failed: {e}")
        return False

def main():
    print("Testing LXCloud Backend Functionality")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Version Check", test_version),
        ("Controller Registration", test_controller_registration),
        ("Admin Creation", test_admin_creation)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        success = test_func()
        results.append((name, success))
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print("Test Results:")
    for name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  {name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()