#!/bin/bash

# LXCloud Installation/Update Script for Ubuntu Server LTS 22.04
# This script installs, updates and configures the complete LXCloud platform
# Supports both fresh installations and updates from existing versions

set -e  # Exit on any error

# Version information
CURRENT_VERSION="1.1.3.0"
MINIMUM_SUPPORTED_VERSION="1.0.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration flags
CLEAN_OLD_DATA=false
INTERACTIVE_MODE=true
FORCE_UPDATE=false
SKIP_BACKUP=false

# Installation state
EXISTING_INSTALLATION=false
CURRENT_INSTALLED_VERSION=""

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

success() {
    echo -e "${PURPLE}[SUCCESS] $1${NC}"
}

# Function to detect existing installation
detect_existing_installation() {
    log "Checking for existing LXCloud installation..."
    
    # Check if systemd service exists
    if [ -f "/etc/systemd/system/lxcloud-backend.service" ]; then
        EXISTING_INSTALLATION=true
        info "Found existing systemd service"
    fi
    
    # Check if application directory exists
    if [ -d "/opt/lxcloud" ]; then
        EXISTING_INSTALLATION=true
        info "Found existing application directory"
        
        # Try to get version from running service
        if systemctl is-active --quiet lxcloud-backend 2>/dev/null; then
            info "LXCloud backend service is running"
            
            # Try to get version via API
            local version_response
            version_response=$(curl -s --connect-timeout 5 http://localhost:5000/api/version 2>/dev/null || echo "")
            
            if [ -n "$version_response" ]; then
                CURRENT_INSTALLED_VERSION=$(echo "$version_response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('app_version', 'unknown'))
except:
    print('unknown')
" 2>/dev/null || echo "unknown")
                
                if [ "$CURRENT_INSTALLED_VERSION" != "unknown" ]; then
                    info "Detected installed version: $CURRENT_INSTALLED_VERSION"
                else
                    warning "Could not determine installed version from API"
                fi
            else
                warning "Could not connect to LXCloud API to check version"
            fi
        else
            info "LXCloud backend service is not running"
        fi
    fi
    
    # Check database
    if command -v mysql >/dev/null 2>&1; then
        if mysql -u lxcloud -plxcloud123 -e "USE lxcloud; SHOW TABLES;" >/dev/null 2>&1; then
            EXISTING_INSTALLATION=true
            info "Found existing LXCloud database"
        fi
    fi
    
    if [ "$EXISTING_INSTALLATION" = true ]; then
        success "Existing LXCloud installation detected"
        if [ -n "$CURRENT_INSTALLED_VERSION" ] && [ "$CURRENT_INSTALLED_VERSION" != "unknown" ]; then
            info "Installed version: $CURRENT_INSTALLED_VERSION"
            info "Available version: $CURRENT_VERSION"
        fi
    else
        info "No existing installation found - will perform fresh installation"
    fi
}

# Function to create database backup
create_database_backup() {
    local backup_file="/tmp/lxcloud_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    log "Creating database backup..."
    if mysqldump -u lxcloud -plxcloud123 lxcloud > "$backup_file" 2>/dev/null; then
        success "Database backup created: $backup_file"
        info "You can restore it later with: mysql -u lxcloud -plxcloud123 lxcloud < $backup_file"
        return 0
    else
        warning "Failed to create database backup"
        return 1
    fi
}

# Function to compare versions
version_greater_or_equal() {
    local version1="$1"
    local version2="$2"
    
    # Simple version comparison (assumes semantic versioning)
    printf '%s\n%s\n' "$version2" "$version1" | sort -V -C
}

# Function to record installation/update
record_installation() {
    local install_type="$1"
    local previous_version="$2"
    local notes="$3"
    
    # Try to record in database if available
    if command -v mysql >/dev/null 2>&1; then
        mysql -u lxcloud -plxcloud123 lxcloud -e "
            INSERT INTO app_info (app_version, install_type, previous_version, notes)
            VALUES ('$CURRENT_VERSION', '$install_type', $([ -n "$previous_version" ] && echo "'$previous_version'" || echo "NULL"), $([ -n "$notes" ] && echo "'$notes'" || echo "NULL"));
        " 2>/dev/null || true
    fi
}

# Function to clean old data
cleanup_old_data() {
    log "Cleaning up old LXCloud data..."
    
    # Stop services if running
    sudo systemctl stop lxcloud-backend 2>/dev/null || true
    sudo systemctl stop nginx 2>/dev/null || true
    
    # Drop and recreate database
    sudo mysql -u root -plxcloud123 <<EOF
DROP DATABASE IF EXISTS lxcloud;
CREATE DATABASE lxcloud;
GRANT ALL PRIVILEGES ON lxcloud.* TO 'lxcloud'@'localhost';
FLUSH PRIVILEGES;
EOF
    
    # Remove old application directory if it exists
    if [ -d "/opt/lxcloud" ]; then
        sudo rm -rf /opt/lxcloud
        log "Removed old application directory"
    fi
    
    # Remove old systemd service
    if [ -f "/etc/systemd/system/lxcloud-backend.service" ]; then
        sudo systemctl disable lxcloud-backend 2>/dev/null || true
        sudo rm -f /etc/systemd/system/lxcloud-backend.service
        sudo systemctl daemon-reload
        log "Removed old systemd service"
    fi
    
    # Remove old nginx configuration
    if [ -f "/etc/nginx/sites-available/lxcloud" ]; then
        sudo rm -f /etc/nginx/sites-available/lxcloud
        sudo rm -f /etc/nginx/sites-enabled/lxcloud
        log "Removed old nginx configuration"
    fi
    
    log "Old data cleanup completed"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --clean-data)
            CLEAN_OLD_DATA=true
            shift
            ;;
        --non-interactive)
            INTERACTIVE_MODE=false
            shift
            ;;
        --force-update)
            FORCE_UPDATE=true
            shift
            ;;
        --skip-backup)
            SKIP_BACKUP=true
            shift
            ;;
        -h|--help)
            echo "LXCloud Installation/Update Script"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --clean-data        Clean all old LXCloud data before installation"
            echo "  --non-interactive   Run without interactive prompts"
            echo "  --force-update      Force update even if versions match"
            echo "  --skip-backup       Skip database backup during updates"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Installation Types:"
            echo "  Fresh Install:      Run on a system without LXCloud"
            echo "  Update:             Run on a system with existing LXCloud installation"
            echo "  Clean Install:      Use --clean-data to remove all existing data"
            echo ""
            echo "Update Process:"
            echo "  1. Detects existing installation and version"
            echo "  2. Creates database backup (unless --skip-backup)"
            echo "  3. Updates application files"
            echo "  4. Runs database migrations"
            echo "  5. Restarts services"
            echo ""
            echo "Version: $CURRENT_VERSION"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

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

log "Starting LXCloud installation/update process..."
log "Target version: $CURRENT_VERSION"

# Detect existing installation
detect_existing_installation

# Determine installation type and show appropriate prompts
if [ "$EXISTING_INSTALLATION" = true ]; then
    success "=== UPDATE MODE ==="
    info "LXCloud installation detected"
    
    if [ -n "$CURRENT_INSTALLED_VERSION" ] && [ "$CURRENT_INSTALLED_VERSION" != "unknown" ]; then
        info "Current version: $CURRENT_INSTALLED_VERSION"
        info "Target version:  $CURRENT_VERSION"
        
        # Check if update is needed
        if [ "$CURRENT_INSTALLED_VERSION" = "$CURRENT_VERSION" ] && [ "$FORCE_UPDATE" = false ]; then
            success "LXCloud is already up to date (version $CURRENT_VERSION)"
            info "Use --force-update to reinstall the same version"
            exit 0
        fi
        
        # Check if downgrade
        if version_greater_or_equal "$CURRENT_INSTALLED_VERSION" "$CURRENT_VERSION" && [ "$CURRENT_INSTALLED_VERSION" != "$CURRENT_VERSION" ]; then
            warning "You are trying to install an older version ($CURRENT_VERSION) over a newer one ($CURRENT_INSTALLED_VERSION)"
            if [ "$INTERACTIVE_MODE" = true ]; then
                read -p "Do you want to continue? (y/N): " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    info "Update cancelled"
                    exit 0
                fi
            fi
        fi
    fi
    
    # Interactive update options
    if [ "$INTERACTIVE_MODE" = true ] && [ "$CLEAN_OLD_DATA" = false ]; then
        echo
        info "=== UPDATE OPTIONS ==="
        echo
        info "Choose update type:"
        echo "1. Standard update (preserve data, run migrations)"
        echo "2. Clean update (remove all data and start fresh) - DATA LOSS WARNING"
        echo "3. Exit and backup data manually"
        echo
        read -p "Enter your choice (1-3): " -n 1 -r
        echo
        echo
        
        case $REPLY in
            1)
                info "Will perform standard update with data preservation"
                ;;
            2)
                CLEAN_OLD_DATA=true
                warning "Will perform clean update - ALL DATA WILL BE LOST"
                read -p "Are you absolutely sure? Type 'YES' to confirm: " confirm
                if [ "$confirm" != "YES" ]; then
                    info "Update cancelled"
                    exit 0
                fi
                ;;
            3)
                info "Update cancelled. Please backup your data and run the script again."
                info "Database backup command: mysqldump -u lxcloud -plxcloud123 lxcloud > backup.sql"
                exit 0
                ;;
            *)
                warning "Invalid choice. Defaulting to standard update."
                ;;
        esac
    fi
    
    # Create backup for standard updates
    if [ "$CLEAN_OLD_DATA" = false ] && [ "$SKIP_BACKUP" = false ]; then
        if [ "$INTERACTIVE_MODE" = true ]; then
            read -p "Create database backup before update? (Y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Nn]$ ]]; then
                warning "Skipping database backup"
            else
                create_database_backup
            fi
        else
            create_database_backup
        fi
    fi
    
else
    success "=== FRESH INSTALLATION MODE ==="
    info "No existing LXCloud installation found"
    
    # Interactive data cleanup prompt for fresh installs (in case of partial installs)
    if [ "$INTERACTIVE_MODE" = true ] && [ "$CLEAN_OLD_DATA" = false ]; then
        echo
        warning "IMPORTANT: Data Cleanup Options"
        echo
        info "This installer can clean up any partial LXCloud data before installation."
        info "This includes:"
        info "  - Database records (users, screens, data)"
        info "  - Application files"
        info "  - Configuration files"
        echo
        echo "Choose an option:"
        echo "1. Clean install (remove any old data) - RECOMMENDED for fresh start"
        echo "2. Keep any existing data (may cause conflicts)"
        echo "3. Exit and backup data manually"
        echo
        read -p "Enter your choice (1-3): " -n 1 -r
        echo
        echo
        
        case $REPLY in
            1)
                CLEAN_OLD_DATA=true
                log "Will perform clean installation"
                ;;
            2)
                log "Will keep any existing data"
                ;;
            3)
                info "Installation cancelled. Please backup your data and run the script again."
                exit 0
                ;;
            *)
                warning "Invalid choice. Defaulting to keep existing data."
                ;;
        esac
    fi
fi

# Perform data cleanup if requested
if [ "$CLEAN_OLD_DATA" = true ]; then
    cleanup_old_data
fi

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

# Save the repository directory before changing directories
REPO_DIR="$(dirname "$(readlink -f "$0")")"

# Create application directory
APP_DIR="/opt/lxcloud"
log "Creating application directory at $APP_DIR..."
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Clone or create application files
log "Creating application files..."
cd $APP_DIR

# If this script is run from the repo, copy files, otherwise create them
if [ -f "$REPO_DIR/backend/app.py" ]; then
    log "Copying application files from repository..."
    cp -r "$REPO_DIR"/* .
else
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

# Get the server's IP address for network access info
SERVER_IP=$(hostname -I | awk '{print $1}')

sudo tee /etc/nginx/sites-available/lxcloud > /dev/null <<EOF
server {
    listen 80;
    server_name _ $SERVER_IP;

    # Frontend static files
    location / {
        root $APP_DIR/frontend/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
        
        # Add headers for local network access
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # CORS headers for API
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
        
        # Handle preflight requests
        if (\$request_method = 'OPTIONS') {
            return 204;
        }
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
SERVER_IP=$(hostname -I | awk '{print $1}')
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Unable to determine")

# Record this installation/update
if [ "$EXISTING_INSTALLATION" = true ]; then
    record_installation "update" "$CURRENT_INSTALLED_VERSION" "Updated via install.sh script"
    INSTALL_TYPE="UPDATE"
else
    record_installation "fresh" "" "Fresh installation via install.sh script"
    INSTALL_TYPE="INSTALLATION"
fi

log "$INSTALL_TYPE completed successfully!"
info ""
info "==================================================================="
if [ "$EXISTING_INSTALLATION" = true ]; then
    info "                    LXCloud Update Complete"
    if [ -n "$CURRENT_INSTALLED_VERSION" ] && [ "$CURRENT_INSTALLED_VERSION" != "unknown" ]; then
        info "                 $CURRENT_INSTALLED_VERSION → $CURRENT_VERSION"
    else
        info "                   Updated to $CURRENT_VERSION"
    fi
else
    info "                    LXCloud Installation Complete"
    info "                      Version $CURRENT_VERSION"
fi
info "==================================================================="
info ""
info "Your LXCloud platform is now ready!"
info ""
info "Access URLs:"
info "  Local Access:      http://localhost"
info "  Network Access:    http://$SERVER_IP"
if [ "$PUBLIC_IP" != "Unable to determine" ] && [ "$PUBLIC_IP" != "$SERVER_IP" ]; then
info "  Public Access:     http://$PUBLIC_IP (if firewall allows)"
fi
info ""
info "For local network access from other devices:"
info "  1. Ensure devices are on the same network"
info "  2. Use the Network Access URL above"
info "  3. Make sure firewall allows port 80"
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
if [ "$EXISTING_INSTALLATION" = false ]; then
    info "Demo Data:"
    info "  To create demo screens and data, run:"
    info "  cd $APP_DIR && python3 create_demo_data.py"
    info ""
fi
info "Data Management:"
info "  Clean old data:  cd $APP_DIR && python3 cleanup_data.py"
info "  Backup database: mysqldump -u lxcloud -plxcloud123 lxcloud > backup.sql"
info "  Check version:   curl http://localhost:5000/api/version"
info ""
info "Configuration Files:"
info "  Application:     $APP_DIR"
info "  Nginx Config:    /etc/nginx/sites-available/lxcloud"
info "  Service File:    /etc/systemd/system/lxcloud-backend.service"
info ""
if [ "$EXISTING_INSTALLATION" = false ]; then
    info "Next Steps:"
    info "1. Visit one of the access URLs above"
    info "2. Register a new user account"
    info "3. Add your LED screens using their serial numbers"
    info "4. Configure your Android devices to send data to:"
    info "   http://$SERVER_IP/api/device/update"
    info ""
fi
info "Troubleshooting:"
info "  If you can't access from other devices:"
info "  - Check firewall: sudo ufw status"
info "  - Verify network connectivity: ping $SERVER_IP"
info "  - Check services: sudo systemctl status lxcloud-backend nginx"
info ""
info "Update Information:"
info "  To update to future versions, simply run this script again"
info "  Your data will be preserved unless you use --clean-data"
info "  Automatic backups are created during updates"
info ""
info "==================================================================="

# Optional: Create demo data (only for fresh installs)
if [ "$EXISTING_INSTALLATION" = false ]; then
    if [ "$INTERACTIVE_MODE" = true ]; then
        read -p "Would you like to create demo screens and data for testing? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log "Creating demo data..."
            cd $APP_DIR
            python3 create_demo_data.py
            info "Demo data created! You can now test the platform with sample screens."
        fi
    fi
fi

log "LXCloud installation/update script finished."