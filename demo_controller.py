#!/usr/bin/env python3
"""
Demo controller simulator for LXCloud
Demonstrates the new controller registration and data sending functionality
"""

import requests
import json
import time
import random
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
CONTROLLER_SN = f"DEMO_CTRL_{int(time.time())}"

def simulate_controller():
    """Simulate a controller registering and sending data"""
    print(f"🤖 Starting LXCloud Controller Simulator")
    print(f"Controller Serial Number: {CONTROLLER_SN}")
    print(f"Target Server: {BASE_URL}")
    print("=" * 60)
    
    # Initial registration
    print("📡 Registering controller with LXCloud...")
    registration_data = {
        "serial_number": CONTROLLER_SN,
        "latitude": 52.3676 + random.uniform(-0.01, 0.01),  # Amsterdam area
        "longitude": 4.9041 + random.uniform(-0.01, 0.01),
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/controller/register", json=registration_data, timeout=5)
        if response.status_code == 200:
            print("✅ Controller registered successfully!")
            print(f"   Location: {registration_data['latitude']:.6f}, {registration_data['longitude']:.6f}")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Registration failed: {e}")
        return
    
    print()
    print("📍 Controller is now visible in admin panel but not storing data yet")
    print("   Users can assign this controller by entering its serial number")
    print()
    
    # Simulate ongoing updates
    print("🔄 Starting periodic updates...")
    update_count = 0
    
    try:
        while update_count < 10:  # Run for 10 iterations
            update_count += 1
            
            # Simulate sensor data
            temperature = random.uniform(18.0, 25.0)
            humidity = random.uniform(40.0, 70.0)
            
            update_data = {
                "serial_number": CONTROLLER_SN,
                "latitude": registration_data['latitude'] + random.uniform(-0.001, 0.001),
                "longitude": registration_data['longitude'] + random.uniform(-0.001, 0.001),
                "information": json.dumps({
                    "timestamp": datetime.now().isoformat(),
                    "temperature": round(temperature, 1),
                    "humidity": round(humidity, 1),
                    "status": "online",
                    "update_count": update_count
                })
            }
            
            try:
                response = requests.post(f"{BASE_URL}/api/device/update", json=update_data, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if "not assigned" in data.get('message', ''):
                        status = "🟡 Unassigned"
                    else:
                        status = "🟢 Assigned"
                    
                    print(f"   Update #{update_count:2d}: {status} | Temp: {temperature:4.1f}°C | Humidity: {humidity:4.1f}%")
                else:
                    print(f"   Update #{update_count:2d}: ❌ Failed ({response.status_code})")
                    
            except requests.exceptions.RequestException as e:
                print(f"   Update #{update_count:2d}: ❌ Error: {e}")
            
            time.sleep(3)  # Wait 3 seconds between updates
            
    except KeyboardInterrupt:
        print("\n⏹️  Simulation stopped by user")
    
    print()
    print("📋 Simulation Summary:")
    print(f"   Serial Number: {CONTROLLER_SN}")
    print(f"   Total Updates: {update_count}")
    print(f"   Location: {registration_data['latitude']:.6f}, {registration_data['longitude']:.6f}")
    print()
    print("ℹ️  To assign this controller to a user:")
    print("   1. Login to LXCloud as any user")
    print("   2. Go to 'Manage Screens' or click the '+' button")
    print(f"   3. Enter serial number: {CONTROLLER_SN}")
    print("   4. The controller will start storing data once assigned!")
    print()
    print("👑 To view unassigned controllers:")
    print("   1. Create an admin account using the admin key")
    print("   2. Visit the Admin Panel")
    print("   3. View all controllers in the 'Unassigned Controllers' section")

if __name__ == "__main__":
    simulate_controller()