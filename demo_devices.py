#!/usr/bin/env python3
"""
Demo script to create sample LED screens and data for testing LXCloud
"""

import requests
import json
import random
import time
from datetime import datetime, timedelta

# Configuration
SERVER_URL = "http://localhost"  # Change this to your server URL
DEMO_SCREENS = [
    {
        "serial_number": "DEMO001",
        "name": "Amsterdam Central Screen",
        "latitude": 52.3676,
        "longitude": 4.9041
    },
    {
        "serial_number": "DEMO002", 
        "name": "London Bridge Screen",
        "latitude": 51.5074,
        "longitude": -0.1278
    },
    {
        "serial_number": "DEMO003",
        "name": "Paris Louvre Screen", 
        "latitude": 48.8566,
        "longitude": 2.3522
    },
    {
        "serial_number": "DEMO004",
        "name": "Berlin Brandenburg Screen",
        "latitude": 52.5200,
        "longitude": 13.4050
    },
    {
        "serial_number": "DEMO005",
        "name": "New York Times Square Screen",
        "latitude": 40.7589,
        "longitude": -73.9851
    }
]

def simulate_device_updates():
    """Simulate Android devices sending updates to the server"""
    print("Simulating device updates...")
    
    for i, screen in enumerate(DEMO_SCREENS):
        # Add some randomness to location (simulate movement/drift)
        lat_offset = random.uniform(-0.001, 0.001)
        lng_offset = random.uniform(-0.001, 0.001)
        
        # Random status messages
        status_messages = [
            "Screen displaying advertising content",
            "System operating normally",
            "High brightness mode active",
            "Content updated successfully", 
            "Temperature normal, system stable",
            "Network connection excellent",
            "Displaying promotional content",
            "System diagnostics passed"
        ]
        
        data = {
            "serial_number": screen["serial_number"],
            "latitude": screen["latitude"] + lat_offset,
            "longitude": screen["longitude"] + lng_offset,
            "information": random.choice(status_messages)
        }
        
        try:
            response = requests.post(
                f"{SERVER_URL}/api/device/update",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✓ Updated {screen['name']} ({screen['serial_number']})")
            else:
                print(f"✗ Failed to update {screen['name']}: {response.status_code}")
                print(f"  Response: {response.text}")
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Network error updating {screen['name']}: {e}")
        
        # Small delay between updates
        time.sleep(0.5)

def simulate_continuous_updates(duration_minutes=5):
    """Simulate continuous updates for a specified duration"""
    print(f"Starting continuous simulation for {duration_minutes} minutes...")
    print("Press Ctrl+C to stop early")
    
    end_time = datetime.now() + timedelta(minutes=duration_minutes)
    update_count = 0
    
    try:
        while datetime.now() < end_time:
            simulate_device_updates()
            update_count += 1
            
            print(f"Completed update cycle {update_count}")
            print(f"Next update in 30 seconds...")
            
            # Wait 30 seconds between update cycles
            time.sleep(30)
    
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
    
    print(f"Simulation completed. Sent {update_count} update cycles.")

def test_api_connectivity():
    """Test if the LXCloud API is accessible"""
    print("Testing API connectivity...")
    
    try:
        # Try to access a simple endpoint that doesn't require authentication
        response = requests.get(f"{SERVER_URL}/api/user", timeout=5)
        
        if response.status_code in [401, 403]:
            print("✓ API is accessible (authentication required)")
            return True
        elif response.status_code == 200:
            print("✓ API is accessible")
            return True
        else:
            print(f"✗ API returned unexpected status: {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to {SERVER_URL}")
        print("  Make sure LXCloud is running and accessible")
        return False
    except requests.exceptions.Timeout:
        print(f"✗ Timeout connecting to {SERVER_URL}")
        return False
    except Exception as e:
        print(f"✗ Error testing API: {e}")
        return False

def main():
    print("LXCloud Demo Script")
    print("=" * 40)
    print(f"Server URL: {SERVER_URL}")
    print(f"Demo screens: {len(DEMO_SCREENS)}")
    print()
    
    # Test connectivity first
    if not test_api_connectivity():
        print("\nPlease ensure LXCloud is running and try again.")
        return 1
    
    print("\nSelect an option:")
    print("1. Send single update for all demo screens")
    print("2. Start continuous simulation (5 minutes)")
    print("3. Start continuous simulation (custom duration)")
    print("4. Exit")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            simulate_device_updates()
            print("\nDemo complete! Check your LXCloud dashboard for updates.")
        
        elif choice == "2":
            simulate_continuous_updates(5)
        
        elif choice == "3":
            try:
                duration = int(input("Enter duration in minutes: "))
                if duration > 0:
                    simulate_continuous_updates(duration)
                else:
                    print("Duration must be positive")
            except ValueError:
                print("Please enter a valid number")
        
        elif choice == "4":
            print("Goodbye!")
            return 0
        
        else:
            print("Invalid choice")
            return 1
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 0
    
    return 0

if __name__ == "__main__":
    exit(main())