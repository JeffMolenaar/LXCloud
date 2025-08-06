#!/bin/bash

# LXCloud Version Checker
# Quick script to check current installation version and available updates

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo "LXCloud Version Checker"
echo "======================"
echo ""

# Check if LXCloud is installed
if [ ! -f "/etc/systemd/system/lxcloud-backend.service" ] && [ ! -d "/opt/lxcloud" ]; then
    echo -e "${RED}LXCloud installation not found.${NC}"
    echo "Please install LXCloud first using ./install.sh"
    exit 1
fi

# Check if service is running
if ! systemctl is-active --quiet lxcloud-backend 2>/dev/null; then
    echo -e "${YELLOW}Warning: LXCloud backend service is not running${NC}"
    echo "Try: sudo systemctl start lxcloud-backend"
    echo ""
fi

# Get version information from API
echo "Checking current installation..."
VERSION_INFO=$(curl -s --connect-timeout 5 http://localhost:5000/api/version 2>/dev/null || echo "")

if [ -n "$VERSION_INFO" ]; then
    echo -e "${GREEN}✓ LXCloud is running${NC}"
    echo ""
    
    # Parse JSON response (simple parsing)
    CURRENT_VERSION=$(echo "$VERSION_INFO" | grep -o '"app_version":"[^"]*"' | cut -d'"' -f4)
    DB_VERSION=$(echo "$VERSION_INFO" | grep -o '"database_version":[0-9]*' | cut -d':' -f2)
    TARGET_DB_VERSION=$(echo "$VERSION_INFO" | grep -o '"target_database_version":[0-9]*' | cut -d':' -f2)
    
    echo -e "${BLUE}Current Installation:${NC}"
    echo "  App Version:      $CURRENT_VERSION"
    echo "  Database Version: $DB_VERSION"
    if [ "$DB_VERSION" != "$TARGET_DB_VERSION" ]; then
        echo -e "  ${YELLOW}Database needs migration to version $TARGET_DB_VERSION${NC}"
    fi
    echo ""
    
    # Check available version from local files
    if [ -f "VERSION" ]; then
        AVAILABLE_VERSION=$(cat VERSION)
        echo -e "${BLUE}Available Version:${NC}    $AVAILABLE_VERSION"
        
        if [ "$CURRENT_VERSION" = "$AVAILABLE_VERSION" ]; then
            echo -e "${GREEN}✓ Your installation is up to date!${NC}"
        else
            echo -e "${YELLOW}⚠ Update available: $CURRENT_VERSION → $AVAILABLE_VERSION${NC}"
            echo ""
            echo "To update:"
            echo "  git pull origin main"
            echo "  ./install.sh"
            echo ""
            echo "Or use:"
            echo "  ./update.sh"
        fi
    else
        echo -e "${YELLOW}Cannot determine available version (VERSION file not found)${NC}"
        echo "Make sure you're in the LXCloud directory and run 'git pull origin main'"
    fi
    
    echo ""
    
    # Show installation history
    HISTORY=$(echo "$VERSION_INFO" | grep -o '"installation_history":\[[^]]*\]' | sed 's/.*://') 2>/dev/null || echo "[]"
    if [ "$HISTORY" != "[]" ] && [ -n "$HISTORY" ]; then
        echo -e "${BLUE}Recent Installation History:${NC}"
        # Simple history parsing (shows last entry)
        LAST_INSTALL=$(echo "$HISTORY" | grep -o '{"app_version":"[^"]*","install_type":"[^"]*"[^}]*}' | head -1)
        if [ -n "$LAST_INSTALL" ]; then
            LAST_VERSION=$(echo "$LAST_INSTALL" | grep -o '"app_version":"[^"]*"' | cut -d'"' -f4)
            LAST_TYPE=$(echo "$LAST_INSTALL" | grep -o '"install_type":"[^"]*"' | cut -d'"' -f4)
            echo "  Last: $LAST_VERSION ($LAST_TYPE)"
        fi
    fi
    
else
    echo -e "${RED}✗ Cannot connect to LXCloud API${NC}"
    echo ""
    echo "Possible issues:"
    echo "  - Backend service not running: sudo systemctl start lxcloud-backend"
    echo "  - Port 5000 not accessible"
    echo "  - Database connection issues"
    echo ""
    echo "Check service status:"
    echo "  sudo systemctl status lxcloud-backend"
    echo "  sudo journalctl -u lxcloud-backend -f"
fi

echo ""
echo "System Status:"
echo "============="

# Check systemd services
if systemctl is-active --quiet lxcloud-backend 2>/dev/null; then
    echo -e "  Backend Service: ${GREEN}✓ Running${NC}"
else
    echo -e "  Backend Service: ${RED}✗ Not Running${NC}"
fi

if systemctl is-active --quiet nginx 2>/dev/null; then
    echo -e "  Nginx Service:   ${GREEN}✓ Running${NC}"
else
    echo -e "  Nginx Service:   ${RED}✗ Not Running${NC}"
fi

if systemctl is-active --quiet mariadb 2>/dev/null; then
    echo -e "  Database:        ${GREEN}✓ Running${NC}"
else
    echo -e "  Database:        ${RED}✗ Not Running${NC}"
fi

echo ""
echo "Quick Commands:"
echo "==============="
echo "  Check logs:    sudo journalctl -u lxcloud-backend -f"
echo "  Restart:       sudo systemctl restart lxcloud-backend"
echo "  Update:        ./install.sh"
echo "  Clean update:  ./install.sh --clean-data"