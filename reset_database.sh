#!/bin/bash

# LXCloud Database Reset Script
# This script completely resets the LXCloud database and creates a fresh setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Database configuration
DB_USER="lxcloud"
DB_PASS="lxcloud123"
DB_NAME="lxcloud"

# Check if MariaDB is running
if ! systemctl is-active --quiet mariadb; then
    error "MariaDB is not running. Please start MariaDB first: sudo systemctl start mariadb"
fi

# Confirm reset
echo -e "${YELLOW}WARNING: This will completely reset the LXCloud database!${NC}"
echo "All users, screens, controllers, and data will be permanently deleted."
read -p "Are you sure you want to continue? (type 'yes' to confirm): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Database reset cancelled."
    exit 0
fi

log "Stopping LXCloud backend service..."
sudo systemctl stop lxcloud-backend 2>/dev/null || true

log "Resetting LXCloud database..."

# Drop and recreate database
sudo mysql -u root -p${DB_PASS} <<EOF
DROP DATABASE IF EXISTS ${DB_NAME};
CREATE DATABASE ${DB_NAME};
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF

log "Database reset complete!"

# Start backend service to run migrations
log "Starting LXCloud backend to initialize schema..."
sudo systemctl start lxcloud-backend

# Wait a moment for the service to start
sleep 3

# Check if service started successfully
if systemctl is-active --quiet lxcloud-backend; then
    log "LXCloud backend started successfully"
    log "Database schema will be automatically created on first startup"
else
    warning "LXCloud backend failed to start. Check logs: sudo journalctl -u lxcloud-backend -f"
fi

echo ""
echo -e "${GREEN}Database reset completed successfully!${NC}"
echo ""
echo "To create an admin account, you can:"
echo "1. Use the web interface at http://your-server-ip/register (first user becomes admin)"
echo "2. Or use the API endpoint /api/admin/create-admin with admin_key: 'lxcloud-admin-setup-2024'"
echo ""
echo "Example curl command:"
echo "curl -X POST http://localhost:5000/api/admin/create-admin \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"username\":\"admin\",\"email\":\"admin@example.com\",\"password\":\"admin123\",\"admin_key\":\"lxcloud-admin-setup-2024\"}'"