#!/bin/bash

# LXCloud Startup Script
# This script starts both the backend and frontend services

set -e

echo "============================================================"
echo "LXCloud Startup Script"
echo "============================================================"

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting LXCloud services...${NC}"

# Check if MySQL/MariaDB is running
echo -e "${YELLOW}Checking database service...${NC}"
if ! systemctl is-active --quiet mysql && ! systemctl is-active --quiet mariadb; then
    echo -e "${YELLOW}Starting database service...${NC}"
    sudo systemctl start mysql 2>/dev/null || sudo systemctl start mariadb 2>/dev/null || {
        echo -e "${RED}Failed to start database service${NC}"
        echo "Please install and start MySQL/MariaDB manually"
        exit 1
    }
fi

# Setup database if needed
echo -e "${YELLOW}Setting up database...${NC}"
mysql -u root -e "CREATE DATABASE IF NOT EXISTS lxcloud; CREATE USER IF NOT EXISTS 'lxcloud'@'localhost' IDENTIFIED BY 'lxcloud123'; GRANT ALL PRIVILEGES ON lxcloud.* TO 'lxcloud'@'localhost'; FLUSH PRIVILEGES;" 2>/dev/null || {
    echo -e "${YELLOW}Database setup failed, continuing anyway...${NC}"
}

# Check if virtual environment exists, if not create it
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install netifaces
    cd ..
fi

# Check if frontend is built
if [ ! -d "frontend/dist" ]; then
    echo -e "${YELLOW}Building frontend...${NC}"
    cd frontend
    npm install
    npm run build
    cd ..
fi

# Get network information
HOSTNAME=$(hostname)
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo -e "${GREEN}Starting backend server...${NC}"
echo -e "${BLUE}The application will be accessible at:${NC}"
echo -e "  ${GREEN}http://localhost:5000${NC}"
echo -e "  ${GREEN}http://127.0.0.1:5000${NC}"
if [ ! -z "$LOCAL_IP" ]; then
    echo -e "  ${GREEN}http://$LOCAL_IP:5000${NC}"
fi
echo ""
echo -e "${YELLOW}Note: The backend serves both API and frontend files${NC}"
echo -e "${YELLOW}If you get 'ERR_CONNECTION_REFUSED', make sure firewall allows port 5000${NC}"
echo ""
echo -e "${BLUE}To stop the server, press Ctrl+C${NC}"
echo "============================================================"

# Start the backend (which also serves the frontend)
cd backend
source venv/bin/activate
python app.py