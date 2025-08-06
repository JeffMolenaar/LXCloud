#!/usr/bin/env python3
"""
LXCloud Setup Checker
This script helps diagnose common setup issues when getting a blank page.
"""

import os
import sys
import subprocess
import json
from urllib.request import urlopen
from urllib.error import URLError
import socket

def check_python():
    """Check Python version"""
    print("🐍 Python Version Check")
    version = sys.version_info
    print(f"   Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print("   ✅ Python version is compatible")
        return True
    else:
        print("   ❌ Python 3.8+ required")
        return False

def check_nodejs():
    """Check Node.js and npm"""
    print("\n📦 Node.js & NPM Check")
    try:
        node_version = subprocess.check_output(['node', '--version'], stderr=subprocess.DEVNULL).decode().strip()
        npm_version = subprocess.check_output(['npm', '--version'], stderr=subprocess.DEVNULL).decode().strip()
        print(f"   Node.js version: {node_version}")
        print(f"   NPM version: {npm_version}")
        print("   ✅ Node.js and NPM are available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ❌ Node.js or NPM not found")
        print("   Install Node.js 18+ from https://nodejs.org/")
        return False

def check_frontend_build():
    """Check if frontend is built"""
    print("\n🎨 Frontend Build Check")
    frontend_dist = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')
    index_html = os.path.join(frontend_dist, 'index.html')
    
    if os.path.exists(index_html):
        print(f"   ✅ Frontend built at: {frontend_dist}")
        return True
    else:
        print(f"   ❌ Frontend not built. Missing: {index_html}")
        print("   Run: cd frontend && npm install && npm run build")
        return False

def check_backend_deps():
    """Check backend dependencies"""
    print("\n🔧 Backend Dependencies Check")
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    venv_dir = os.path.join(backend_dir, 'venv')
    requirements_file = os.path.join(backend_dir, 'requirements.txt')
    
    if os.path.exists(venv_dir):
        print(f"   ✅ Virtual environment found: {venv_dir}")
    else:
        print(f"   ❌ Virtual environment not found: {venv_dir}")
        print("   Run: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt")
        return False
    
    if os.path.exists(requirements_file):
        print(f"   ✅ Requirements file found: {requirements_file}")
        return True
    else:
        print(f"   ❌ Requirements file not found: {requirements_file}")
        return False

def check_network_interfaces():
    """Check available network interfaces"""
    print("\n🌐 Network Interfaces Check")
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"   Hostname: {hostname}")
        print(f"   Local IP: {local_ip}")
        
        # Get all network interfaces
        import subprocess
        try:
            result = subprocess.check_output(['ip', 'addr', 'show'], stderr=subprocess.DEVNULL).decode()
            lines = result.split('\n')
            ips = []
            for line in lines:
                if 'inet ' in line and '127.0.0.1' not in line:
                    parts = line.strip().split()
                    if len(parts) > 1:
                        ip = parts[1].split('/')[0]
                        ips.append(ip)
            
            if ips:
                print("   Available IPs for local network access:")
                for ip in ips:
                    print(f"     http://{ip}")
                    print(f"     http://{ip}:5000 (if backend running)")
        except:
            pass
            
        return True
    except Exception as e:
        print(f"   ❌ Network check failed: {e}")
        return False

def test_backend_api():
    """Test if backend API is responding"""
    print("\n🔌 Backend API Test")
    test_urls = [
        'http://localhost:5000/api/health',
        'http://127.0.0.1:5000/api/health'
    ]
    
    for url in test_urls:
        try:
            response = urlopen(url, timeout=5)
            data = json.loads(response.read().decode())
            print(f"   ✅ API responding at {url}")
            print(f"      Status: {data.get('status', 'unknown')}")
            print(f"      Database: {data.get('database', 'unknown')}")
            return True
        except URLError:
            print(f"   ❌ API not responding at {url}")
        except Exception as e:
            print(f"   ❌ API test failed at {url}: {e}")
    
    print("   💡 To start backend: cd backend && source venv/bin/activate && python app.py")
    return False

def test_frontend_access():
    """Test if frontend is accessible"""
    print("\n🖥️  Frontend Access Test")
    test_urls = [
        'http://localhost:80',
        'http://127.0.0.1:80',
        'http://localhost:3000',
        'http://127.0.0.1:3000'
    ]
    
    for url in test_urls:
        try:
            response = urlopen(url, timeout=5)
            content = response.read().decode()
            if 'LXCloud' in content:
                print(f"   ✅ Frontend accessible at {url}")
                return True
            else:
                print(f"   ⚠️  Response at {url} but no LXCloud content")
        except URLError:
            print(f"   ❌ Frontend not accessible at {url}")
        except Exception as e:
            print(f"   ❌ Frontend test failed at {url}: {e}")
    
    return False

def provide_solutions():
    """Provide common solutions"""
    print("\n🔧 Common Solutions for Blank Page Issues:")
    print()
    print("1. Build the frontend:")
    print("   cd frontend")
    print("   npm install")
    print("   npm run build")
    print()
    print("2. Start the backend:")
    print("   cd backend")
    print("   python3 -m venv venv")
    print("   source venv/bin/activate")
    print("   pip install -r requirements.txt")
    print("   python app.py")
    print()
    print("3. For database issues:")
    print("   - Install MariaDB/MySQL")
    print("   - Run the install.sh script")
    print("   - Or use standalone mode: python app_standalone.py")
    print()
    print("4. For network access issues:")
    print("   - Ensure firewall allows port 80 and 5000")
    print("   - Check CORS settings in backend/app.py")
    print("   - Use standalone mode for testing")
    print()
    print("5. Quick test setup:")
    print("   python app_standalone.py  # Runs frontend + backend on port 80")

def main():
    """Main check function"""
    print("LXCloud Setup Diagnosis")
    print("=" * 50)
    
    checks = [
        check_python(),
        check_nodejs(),
        check_frontend_build(),
        check_backend_deps(),
        check_network_interfaces()
    ]
    
    # Test running services
    backend_running = test_backend_api()
    frontend_running = test_frontend_access()
    
    print("\n📊 Summary")
    print("=" * 50)
    basic_setup = all(checks)
    services_running = backend_running or frontend_running
    
    if basic_setup and services_running:
        print("✅ Setup looks good! LXCloud should be working.")
    elif basic_setup:
        print("⚠️  Setup is correct but services aren't running.")
        print("   Start the backend and/or frontend services.")
    else:
        print("❌ Setup issues detected. See solutions below.")
    
    if not services_running:
        provide_solutions()

if __name__ == '__main__':
    main()