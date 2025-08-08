#!/bin/bash

# LXCloud Network Configuration Script
# This script configures firewall and network settings for external access

set -e

echo "============================================================"
echo "LXCloud Network Configuration"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get current IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo -e "${BLUE}Configuring network access for LXCloud...${NC}"
echo -e "${YELLOW}Current IP address: $LOCAL_IP${NC}"

# Check if ufw is installed and active
if command -v ufw &> /dev/null; then
    echo -e "${YELLOW}Configuring UFW firewall...${NC}"
    
    # Allow SSH (just in case)
    sudo ufw allow ssh >/dev/null 2>&1 || true
    
    # Allow LXCloud port
    echo -e "${YELLOW}Allowing port 5000 for LXCloud...${NC}"
    sudo ufw allow 5000/tcp >/dev/null 2>&1 || true
    
    # Enable firewall if not active
    if ! sudo ufw status | grep -q "Status: active"; then
        echo -e "${YELLOW}Enabling UFW firewall...${NC}"
        echo "y" | sudo ufw enable >/dev/null 2>&1 || true
    fi
    
    echo -e "${GREEN}UFW firewall configured successfully${NC}"
    sudo ufw status
else
    echo -e "${YELLOW}UFW not found, checking iptables...${NC}"
    
    # Check if iptables is available
    if command -v iptables &> /dev/null; then
        # Add rule to allow port 5000
        sudo iptables -C INPUT -p tcp --dport 5000 -j ACCEPT 2>/dev/null || \
        sudo iptables -I INPUT -p tcp --dport 5000 -j ACCEPT
        echo -e "${GREEN}iptables rule added for port 5000${NC}"
    else
        echo -e "${YELLOW}No firewall management tool found${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Network configuration complete!${NC}"
echo -e "${BLUE}LXCloud should now be accessible from:${NC}"
echo -e "  ${GREEN}http://localhost:5000${NC}"
echo -e "  ${GREEN}http://127.0.0.1:5000${NC}"
if [ ! -z "$LOCAL_IP" ]; then
    echo -e "  ${GREEN}http://$LOCAL_IP:5000${NC}"
fi

echo ""
echo -e "${YELLOW}If you still get 'ERR_CONNECTION_REFUSED':${NC}"
echo -e "1. Check if the LXCloud service is running (./start.sh)"
echo -e "2. Verify your network/router settings allow access to port 5000"
echo -e "3. Check if any antivirus/security software is blocking the connection"
echo "============================================================"