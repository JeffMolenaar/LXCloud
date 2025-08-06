#!/bin/bash

# LXCloud Installation Script for Ubuntu Server LTS 22.04
# This script installs and configures the complete LXCloud platform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root. Please run as a regular user with sudo privileges."
fi

# Check if sudo is available
if ! command -v sudo >/dev/null 2>&1; then
    error "sudo command not found. Please install sudo first."
fi

# Check if user has sudo privileges (check group membership or sudo access)
if ! (groups | grep -qE '(sudo|wheel|admin)' || sudo -l >/dev/null 2>&1); then
    error "This script requires sudo privileges. Please ensure your user has sudo access."
fi

# Check Ubuntu version
if ! grep -q "Ubuntu 22.04" /etc/os-release; then
    warning "This script is designed for Ubuntu 22.04 LTS. Your system may not be supported."
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

log "Starting LXCloud installation..."

# Update system packages
log "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
log "Installing system dependencies..."
sudo apt install -y \
    curl \
    wget \
    git \
    nginx \
    ufw \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Install Node.js 18.x
log "Installing Node.js 18.x..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Python 3.10 and pip
log "Installing Python and pip..."
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install MariaDB
log "Installing MariaDB..."
sudo apt install -y mariadb-server mariadb-client

# Secure MariaDB installation
log "Securing MariaDB installation..."
sudo mysql_secure_installation <<EOF

y
lxcloud123
lxcloud123
y
y
y
y
EOF

# Create MariaDB database and user
log "Creating database and user..."
sudo mysql -u root -plxcloud123 <<EOF
CREATE DATABASE IF NOT EXISTS lxcloud;
CREATE USER IF NOT EXISTS 'lxcloud'@'localhost' IDENTIFIED BY 'lxcloud123';
GRANT ALL PRIVILEGES ON lxcloud.* TO 'lxcloud'@'localhost';
FLUSH PRIVILEGES;
EOF

# Create application directory
APP_DIR="/opt/lxcloud"
log "Creating application directory at $APP_DIR..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Clone or create application files
cd $APP_DIR

# If this script is run from the repo, copy files, otherwise create them
if [ -f "$(dirname $0)/backend/app.py" ]; then
    log "Copying application files from repository..."
    cp -r "$(dirname $0)"/* .
else
    log "Creating application files..."
    # Create directory structure
    mkdir -p backend frontend

    # Create backend files (app.py and requirements.txt would be created here)
    # For now, we'll assume the files exist in the repository
    error "Application files not found. Please run this script from the LXCloud repository directory."
fi

# Install Python dependencies
log "Installing Python dependencies..."
cd $APP_DIR/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Node.js dependencies and build frontend
log "Installing Node.js dependencies..."
cd $APP_DIR/frontend
npm install

log "Building frontend..."
npm run build

# Create systemd service for backend
log "Creating systemd service..."
sudo tee /etc/systemd/system/lxcloud-backend.service > /dev/null <<EOF
[Unit]
Description=LXCloud Backend
After=network.target mariadb.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR/backend
Environment=PATH=$APP_DIR/backend/venv/bin
ExecStart=$APP_DIR/backend/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
log "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/lxcloud > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    # Frontend static files
    location / {
        root $APP_DIR/frontend/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # WebSocket support
    location /socket.io/ {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/lxcloud /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Configure firewall
log "Configuring firewall..."
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS (for future SSL)
sudo ufw --force enable

# Start and enable services
log "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable lxcloud-backend
sudo systemctl start lxcloud-backend
sudo systemctl enable nginx
sudo systemctl restart nginx
sudo systemctl enable mariadb
sudo systemctl restart mariadb

# Create demo data script
log "Creating demo data script..."
tee $APP_DIR/create_demo_data.py > /dev/null <<EOF
#!/usr/bin/env python3
import pymysql
import random
from datetime import datetime, timedelta

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'lxcloud',
    'password': 'lxcloud123',
    'database': 'lxcloud',
    'charset': 'utf8mb4'
}

def create_demo_data():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Sample locations (major cities)
    locations = [
        (52.3676, 4.9041, "Amsterdam"),
        (51.5074, -0.1278, "London"),
        (48.8566, 2.3522, "Paris"),
        (52.5200, 13.4050, "Berlin"),
        (40.7128, -74.0060, "New York"),
        (34.0522, -118.2437, "Los Angeles"),
        (35.6762, 139.6503, "Tokyo"),
        (37.7749, -122.4194, "San Francisco"),
        (55.7558, 37.6176, "Moscow"),
        (39.9042, 116.4074, "Beijing")
    ]
    
    # Create demo screens
    for i in range(10):
        lat, lng, city = random.choice(locations)
        # Add some randomness to location
        lat += random.uniform(-0.1, 0.1)
        lng += random.uniform(-0.1, 0.1)
        
        serial = f"DEMO{1000 + i}"
        custom_name = f"{city} Screen {i + 1}"
        online = random.choice([True, False])
        
        cursor.execute("""
            INSERT IGNORE INTO screens (serial_number, custom_name, latitude, longitude, online_status, last_seen)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (serial, custom_name, lat, lng, online, datetime.now() - timedelta(hours=random.randint(0, 48))))
        
        screen_id = cursor.lastrowid or cursor.execute("SELECT id FROM screens WHERE serial_number = %s", (serial,)) or cursor.fetchone()[0]
        
        # Add some demo data for each screen
        for j in range(random.randint(5, 20)):
            info = f"Demo data entry {j + 1} for {city}"
            timestamp = datetime.now() - timedelta(hours=random.randint(0, 720))  # Last 30 days
            cursor.execute("""
                INSERT INTO screen_data (screen_id, information, timestamp, year)
                VALUES (%s, %s, %s, %s)
            """, (screen_id, info, timestamp, timestamp.year))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Demo data created successfully!")

if __name__ == "__main__":
    create_demo_data()
EOF

chmod +x $APP_DIR/create_demo_data.py

# Check service status
log "Checking service status..."
sleep 5  # Give services time to start

if systemctl is-active --quiet lxcloud-backend; then
    log "Backend service is running"
else
    error "Backend service failed to start. Check logs with: sudo journalctl -u lxcloud-backend -f"
fi

if systemctl is-active --quiet nginx; then
    log "Nginx service is running"
else
    error "Nginx service failed to start. Check logs with: sudo journalctl -u nginx -f"
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

log "Installation completed successfully!"
info ""
info "==================================================================="
info "                    LXCloud Installation Complete"
info "==================================================================="
info ""
info "Your LXCloud platform is now ready!"
info ""
info "Access URLs:"
info "  Web Interface: http://$SERVER_IP"
info "  Local Access:  http://localhost"
info ""
info "Default Database Credentials:"
info "  Database: lxcloud"
info "  Username: lxcloud"
info "  Password: lxcloud123"
info ""
info "Service Management:"
info "  Backend Status:  sudo systemctl status lxcloud-backend"
info "  Backend Logs:    sudo journalctl -u lxcloud-backend -f"
info "  Nginx Status:    sudo systemctl status nginx"
info "  Restart Backend: sudo systemctl restart lxcloud-backend"
info "  Restart Nginx:   sudo systemctl restart nginx"
info ""
info "Demo Data:"
info "  To create demo screens and data, run:"
info "  cd $APP_DIR && python3 create_demo_data.py"
info ""
info "Configuration Files:"
info "  Application:     $APP_DIR"
info "  Nginx Config:    /etc/nginx/sites-available/lxcloud"
info "  Service File:    /etc/systemd/system/lxcloud-backend.service"
info ""
info "Next Steps:"
info "1. Visit http://$SERVER_IP to access the web interface"
info "2. Register a new user account"
info "3. Add your LED screens using their serial numbers"
info "4. Configure your Android devices to send data to:"
info "   http://$SERVER_IP/api/device/update"
info ""
info "==================================================================="

# Optional: Create demo data
read -p "Would you like to create demo screens and data for testing? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "Creating demo data..."
    cd $APP_DIR
    python3 create_demo_data.py
    info "Demo data created! You can now test the platform with sample screens."
fi

log "LXCloud installation script finished."