#!/bin/bash

# LXCloud Quick Update Script
# This is a simple wrapper around the main install.sh script for updates

set -e

echo "LXCloud Quick Update"
echo "===================="
echo ""
echo "This will update your LXCloud installation to the latest version."
echo "Your data will be preserved and a backup will be created."
echo ""

# Check if LXCloud is installed
if [ ! -f "/etc/systemd/system/lxcloud-backend.service" ] && [ ! -d "/opt/lxcloud" ]; then
    echo "ERROR: LXCloud installation not found."
    echo "Please use ./install.sh for fresh installation."
    exit 1
fi

echo "Existing LXCloud installation detected."
echo ""

# Get the directory of this script
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

# Run the main install script in update mode
exec "$SCRIPT_DIR/install.sh" "$@"