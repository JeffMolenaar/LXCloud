#!/usr/bin/env python3
"""
Simple test script to validate LXCloud backend functionality
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

def test_python_imports():
    """Test if all required Python packages can be imported"""
    print("Testing Python imports...")
    try:
        import flask
        import flask_cors
        import flask_socketio
        import pymysql
        import werkzeug
        print("✓ All Python dependencies available")
        return True
    except ImportError as e:
        print(f"✗ Missing Python dependency: {e}")
        return False

def test_frontend_build():
    """Test if frontend can be built"""
    print("Testing frontend build...")
    frontend_dir = Path(__file__).parent / "frontend"
    dist_dir = frontend_dir / "dist"
    
    if dist_dir.exists() and (dist_dir / "index.html").exists():
        print("✓ Frontend build exists")
        return True
    else:
        print("✗ Frontend build not found")
        return False

def test_app_structure():
    """Test if all required files exist"""
    print("Testing application structure...")
    base_dir = Path(__file__).parent
    
    required_files = [
        "backend/app.py",
        "backend/requirements.txt",
        "frontend/package.json",
        "frontend/webpack.config.js",
        "frontend/src/App.js",
        "install.sh",
        "cleanup_data.py",
        "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (base_dir / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("✗ Missing files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print("✓ All required files present")
        return True

def test_api_endpoints_syntax():
    """Test if the Flask app can be loaded without database connection"""
    print("Testing backend syntax...")
    backend_dir = Path(__file__).parent / "backend"
    
    try:
        # Add backend directory to Python path
        sys.path.insert(0, str(backend_dir))
        
        # Try to import the app module to check syntax
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", backend_dir / "app.py")
        app_module = importlib.util.module_from_spec(spec)
        
        # This will check syntax but not execute database operations
        with open(backend_dir / "app.py", 'r') as f:
            code = f.read()
            compile(code, 'app.py', 'exec')
        
        print("✓ Backend syntax is valid")
        return True
    except SyntaxError as e:
        print(f"✗ Backend syntax error: {e}")
        return False
    except Exception as e:
        print(f"✗ Backend error: {e}")
        return False

def test_installation_script():
    """Test if installation script has correct permissions and basic syntax"""
    print("Testing installation script...")
    install_script = Path(__file__).parent / "install.sh"
    
    if not install_script.exists():
        print("✗ install.sh not found")
        return False
    
    # Check if executable
    if not os.access(install_script, os.X_OK):
        print("✗ install.sh is not executable")
        return False
    
    # Basic bash syntax check
    try:
        result = subprocess.run(
            ["bash", "-n", str(install_script)], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            print("✓ Installation script syntax is valid")
            return True
        else:
            print(f"✗ Installation script syntax error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Installation script syntax check timed out")
        return False
    except Exception as e:
        print(f"✗ Error checking installation script: {e}")
        return False

def main():
    """Run all tests"""
    print("LXCloud Basic Validation Tests")
    print("=" * 40)
    
    tests = [
        ("File Structure", test_app_structure),
        ("Python Dependencies", test_python_imports),
        ("Frontend Build", test_frontend_build),
        ("Backend Syntax", test_api_endpoints_syntax),
        ("Installation Script", test_installation_script),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All tests passed! The LXCloud platform appears to be correctly set up.")
        print("\nNext steps:")
        print("1. Run the installation script: ./install.sh")
        print("2. Or manually install dependencies and start the services")
        print("3. Access the web interface and register a user")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues before proceeding.")
        return 1

if __name__ == "__main__":
    exit(main())