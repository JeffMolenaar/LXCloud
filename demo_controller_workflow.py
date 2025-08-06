#!/usr/bin/env python3

"""
LXCloud Controller Demo Script

This script demonstrates the complete controller workflow:
1. Controllers register themselves via API
2. Admin can see all unassigned controllers
3. Users can assign controllers by serial number
4. Data is only stored when controllers are assigned
"""

import requests
import json
import time
import hashlib
import random

BASE_URL = "http://localhost:5000/api"

def generate_auth_key(serial_number):
    """Generate authentication key for controller"""
    return hashlib.sha256(f"lxcloud-controller-{serial_number}".encode()).hexdigest()[:16]

def register_controller(serial_number, latitude=None, longitude=None):
    """Register a controller via API"""
    if latitude is None:
        latitude = round(random.uniform(51.0, 53.0), 6)
    if longitude is None:
        longitude = round(random.uniform(3.0, 6.0), 6)
    
    auth_key = generate_auth_key(serial_number)
    
    data = {
        "serial_number": serial_number,
        "latitude": latitude,
        "longitude": longitude,
        "auth_key": auth_key
    }
    
    try:
        response = requests.post(f"{BASE_URL}/controller/register", json=data, timeout=5)
        print(f"Registered controller {serial_number}: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  Status: {result.get('status')}")
            print(f"  Expected auth key: {result.get('expected_auth_key')}")
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to register controller {serial_number}: {e}")
        return False

def send_controller_data(serial_number, information="Controller heartbeat"):
    """Send data from controller (simulates Android device)"""
    latitude = round(random.uniform(51.0, 53.0), 6)
    longitude = round(random.uniform(3.0, 6.0), 6)
    
    data = {
        "serial_number": serial_number,
        "latitude": latitude,
        "longitude": longitude,
        "information": information
    }
    
    try:
        response = requests.post(f"{BASE_URL}/device/update", json=data, timeout=5)
        status = "Data stored" if "assigned" in response.text else "Controller updated (no data storage)"
        print(f"  {serial_number}: {status}")
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send data for {serial_number}: {e}")
        return False

def create_admin():
    """Create admin account if it doesn't exist"""
    data = {
        "username": "admin",
        "email": "admin@lxcloud.com",
        "password": "admin123",
        "admin_key": "lxcloud-admin-setup-2024"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/admin/create-admin", json=data, timeout=5)
        if response.status_code in [200, 201]:
            print("Admin account created successfully")
            return True
        elif response.status_code == 400:
            print("Admin account already exists")
            return True
        else:
            print(f"Failed to create admin: {response.json()}")
            return False
    except Exception as e:
        print(f"Admin creation error: {e}")
        return False

def login_admin():
    """Login as admin and return session"""
    session = requests.Session()
    
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = session.post(f"{BASE_URL}/login", json=data, timeout=5)
        if response.status_code == 200:
            print("Admin logged in successfully")
            return session
        else:
            print(f"Admin login failed: {response.json()}")
            return None
    except Exception as e:
        print(f"Admin login error: {e}")
        return None

def get_screens_as_admin(session):
    """Get all screens and controllers as admin"""
    try:
        response = session.get(f"{BASE_URL}/screens", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Assigned screens: {len(data.get('screens', []))}")
            print(f"Unassigned controllers: {len(data.get('unassigned_controllers', []))}")
            
            for controller in data.get('unassigned_controllers', []):
                print(f"  Unassigned: {controller['serial_number']} - {controller['online_status']}")
            
            return data
        else:
            print(f"Failed to get screens: {response.json()}")
            return None
    except Exception as e:
        print(f"Error getting screens: {e}")
        return None

def assign_controller(session, serial_number, custom_name="Demo Screen"):
    """Assign controller to admin user"""
    data = {
        "serial_number": serial_number,
        "custom_name": custom_name
    }
    
    try:
        response = session.post(f"{BASE_URL}/screens", json=data, timeout=5)
        if response.status_code == 201:
            print(f"Successfully assigned {serial_number} to user")
            return True
        else:
            print(f"Failed to assign controller: {response.json()}")
            return False
    except Exception as e:
        print(f"Error assigning controller: {e}")
        return False

def main():
    print("LXCloud Controller Demo")
    print("=" * 60)
    
    # Step 1: Create admin account
    print("\n1. Setting up admin account...")
    if not create_admin():
        print("Failed to create admin account. Exiting.")
        return
    
    # Step 2: Register some controllers
    print("\n2. Registering controllers...")
    controllers = ["DEMO001", "DEMO002", "DEMO003"]
    
    for serial in controllers:
        register_controller(serial)
        time.sleep(0.5)
    
    # Step 3: Controllers send data (should not be stored yet)
    print("\n3. Controllers sending data (before assignment)...")
    for serial in controllers:
        send_controller_data(serial, "Pre-assignment heartbeat")
        time.sleep(0.5)
    
    # Step 4: Admin login
    print("\n4. Admin login...")
    admin_session = login_admin()
    if not admin_session:
        print("Failed to login as admin. Exiting.")
        return
    
    # Step 5: Admin views unassigned controllers
    print("\n5. Admin viewing unassigned controllers...")
    get_screens_as_admin(admin_session)
    
    # Step 6: Admin assigns a controller
    print("\n6. Admin assigning controller...")
    if assign_controller(admin_session, "DEMO001", "First Demo Screen"):
        print("Assignment successful!")
    
    # Step 7: Controllers send data again (now one should store data)
    print("\n7. Controllers sending data (after assignment)...")
    for serial in controllers:
        send_controller_data(serial, "Post-assignment data")
        time.sleep(0.5)
    
    # Step 8: Admin views screens again
    print("\n8. Admin viewing screens after assignment...")
    get_screens_as_admin(admin_session)
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("\nKey points demonstrated:")
    print("- Controllers can register via API with authentication")
    print("- Unassigned controllers don't store data")
    print("- Admin can see all controllers (assigned and unassigned)")
    print("- Controllers store data only after assignment")
    print("- Users assign controllers by serial number")

if __name__ == "__main__":
    main()