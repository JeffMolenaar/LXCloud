#!/usr/bin/env python3
"""
LXCloud Network Diagnostic Tool
Helps diagnose network connectivity and configuration issues
"""

import socket
import subprocess
import sys
import requests
import json
from urllib.parse import urlparse

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote server to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        try:
            # Fallback method
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except:
            return "Unable to determine"

def check_port_listening(host, port):
    """Check if a port is listening"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def check_service_status(service_name):
    """Check systemd service status"""
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', service_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip() == 'active'
    except:
        return False

def test_api_endpoint(url):
    """Test API endpoint connectivity"""
    try:
        response = requests.get(url, timeout=5)
        return {
            'success': True,
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'content': response.text[:200] if response.text else ''
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': str(e)
        }

def check_firewall_status():
    """Check UFW firewall status"""
    try:
        result = subprocess.run(
            ['ufw', 'status'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout
    except:
        return "Unable to check firewall status"

def main():
    """Run network diagnostics"""
    print("LXCloud Network Diagnostic Tool")
    print("=" * 50)
    
    # System information
    print("\n🖥️  System Information:")
    print(f"   Hostname: {socket.gethostname()}")
    
    local_ip = get_local_ip()
    print(f"   Local IP: {local_ip}")
    
    try:
        # Try to get all IP addresses
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=5)
        all_ips = result.stdout.strip().split()
        print(f"   All IPs: {', '.join(all_ips)}")
    except:
        print("   All IPs: Unable to determine")
    
    # Service status
    print("\n🔧 Service Status:")
    services = ['lxcloud-backend', 'nginx', 'mariadb']
    for service in services:
        status = "✓ Running" if check_service_status(service) else "✗ Not running"
        print(f"   {service}: {status}")
    
    # Port connectivity
    print("\n🌐 Port Connectivity:")
    ports_to_check = [
        ('localhost', 5000, 'Backend API'),
        ('localhost', 80, 'Nginx HTTP'),
        ('localhost', 3306, 'MariaDB'),
    ]
    
    for host, port, description in ports_to_check:
        status = "✓ Listening" if check_port_listening(host, port) else "✗ Not listening"
        print(f"   {description} ({host}:{port}): {status}")
    
    # API endpoint tests
    print("\n🔗 API Endpoint Tests:")
    endpoints = [
        f"http://localhost:5000/api/health",
        f"http://{local_ip}:5000/api/health" if local_ip != "Unable to determine" else None,
        f"http://localhost/api/health",
        f"http://{local_ip}/api/health" if local_ip != "Unable to determine" else None,
    ]
    
    for endpoint in endpoints:
        if endpoint is None:
            continue
            
        parsed = urlparse(endpoint)
        test_result = test_api_endpoint(endpoint)
        
        if test_result['success']:
            print(f"   ✓ {endpoint} - Status: {test_result['status_code']} ({test_result['response_time']:.2f}s)")
        else:
            print(f"   ✗ {endpoint} - Error: {test_result['error']}")
    
    # Firewall status
    print("\n🛡️  Firewall Status:")
    firewall_output = check_firewall_status()
    if "Status: active" in firewall_output:
        print("   Status: Active")
        # Check if port 80 is allowed
        if "80" in firewall_output:
            print("   Port 80: ✓ Allowed")
        else:
            print("   Port 80: ✗ Not explicitly allowed")
    elif "Status: inactive" in firewall_output:
        print("   Status: Inactive (all ports open)")
    else:
        print("   Status: Unable to determine")
    
    # Network recommendations
    print("\n💡 Recommendations:")
    
    # Check if backend is running
    if not check_service_status('lxcloud-backend'):
        print("   • Start the backend service: sudo systemctl start lxcloud-backend")
    
    # Check if nginx is running
    if not check_service_status('nginx'):
        print("   • Start nginx service: sudo systemctl start nginx")
    
    # Check if backend port is accessible
    if not check_port_listening('localhost', 5000):
        print("   • Backend port 5000 is not accessible")
        print("     - Check if the backend service is running")
        print("     - Check backend logs: sudo journalctl -u lxcloud-backend -f")
    
    # Check if HTTP port is accessible
    if not check_port_listening('localhost', 80):
        print("   • HTTP port 80 is not accessible")
        print("     - Check if nginx is running and configured correctly")
        print("     - Check nginx logs: sudo journalctl -u nginx -f")
    
    # Firewall recommendations
    firewall_output = check_firewall_status()
    if "Status: active" in firewall_output and "80" not in firewall_output:
        print("   • Allow HTTP traffic through firewall: sudo ufw allow 80/tcp")
    
    print("\n📋 Network Access Information:")
    if local_ip != "Unable to determine":
        print(f"   • Local network access: http://{local_ip}")
        print(f"   • Android API endpoint: http://{local_ip}/api/device/update")
    print(f"   • Local access: http://localhost")
    
    print("\n🔍 Troubleshooting Commands:")
    print("   • Check backend logs: sudo journalctl -u lxcloud-backend -f")
    print("   • Check nginx logs: sudo journalctl -u nginx -f")
    print("   • Test API directly: curl http://localhost:5000/api/health")
    print("   • Restart services: sudo systemctl restart lxcloud-backend nginx")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError running diagnostics: {e}")
        sys.exit(1)