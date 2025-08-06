# LXCloud Update System Guide

## Overview

LXCloud now includes a comprehensive update system that allows you to always update to the latest version with a single runnable script. The system handles database migrations, preserves your data, and provides multiple update options.

## Key Features

✅ **Automatic Version Detection**: Detects existing installations and compares versions  
✅ **Data Preservation**: Updates preserve all user data by default  
✅ **Database Migrations**: Automatically updates database schema when needed  
✅ **Automatic Backups**: Creates database backups before updates  
✅ **Installation Tracking**: Records all installations and updates in the database  
✅ **Multiple Update Modes**: Standard, clean, or forced updates  

## Quick Start

### Fresh Installation
```bash
git clone https://github.com/JeffMolenaar/LXCloud.git
cd LXCloud
./install.sh
```

### Update Existing Installation
```bash
cd LXCloud
git pull origin main
./install.sh
```

Or use the dedicated update script:
```bash
cd LXCloud
git pull origin main
./update.sh
```

## Update Options

| Option | Description |
|--------|-------------|
| `--force-update` | Force update even if versions match |
| `--skip-backup` | Skip database backup during update |
| `--clean-data` | Remove all data and start fresh (⚠️ DATA LOSS) |
| `--non-interactive` | Run without interactive prompts |

## Examples

### Standard Update (Recommended)
```bash
./install.sh
```
- Preserves all data
- Creates automatic backup
- Runs database migrations
- Interactive prompts for confirmation

### Force Update (Same Version)
```bash
./install.sh --force-update
```
- Useful for re-applying updates or fixing issues
- Still preserves data and creates backups

### Non-Interactive Update
```bash
./install.sh --non-interactive
```
- Suitable for automated deployments
- Uses safe defaults (preserves data, creates backup)

### Clean Update (⚠️ Removes All Data)
```bash
./install.sh --clean-data
```
- Removes all existing data
- Useful for fresh start or fixing corruption
- **WARNING**: All users, screens, and data will be lost

## Version Checking

Check your current version:
```bash
curl http://localhost:5000/api/version
```

Example response:
```json
{
  "app_version": "1.1.0",
  "database_version": 2,
  "target_database_version": 2,
  "installation_history": [
    {
      "app_version": "1.1.0",
      "install_type": "update",
      "previous_version": "1.0.0",
      "installed_at": "2024-01-15T10:30:00",
      "notes": "Updated via install.sh script"
    }
  ]
}
```

## Update Process

1. **Detection**: Script detects existing installation and current version
2. **Comparison**: Compares current vs target version
3. **Backup**: Creates database backup (unless skipped)
4. **Application Update**: Updates application files
5. **Database Migration**: Runs any required schema migrations
6. **Service Restart**: Restarts backend and nginx services
7. **Verification**: Verifies services are running correctly

## Migration System

The system includes an automatic database migration system:

- **Version 1**: Initial database schema (users, screens, controllers, screen_data)
- **Version 2**: Added version tracking (schema_version, app_info tables)
- **Future versions**: New migrations can be easily added

Migrations are:
- ✅ **Automatic**: Run during updates without user intervention
- ✅ **Safe**: Won't modify existing data
- ✅ **Incremental**: Only applies missing migrations
- ✅ **Logged**: All migration activities are logged

## Troubleshooting

### Update Detection Issues
If the script doesn't detect your existing installation:
1. Check if `/opt/lxcloud` directory exists
2. Check if `lxcloud-backend.service` exists: `systemctl status lxcloud-backend`
3. Verify database connection: `mysql -u lxcloud -plxcloud123 lxcloud -e "SHOW TABLES;"`

### Version Check Fails
If version API is not responding:
1. Check if backend is running: `systemctl status lxcloud-backend`
2. Check logs: `journalctl -u lxcloud-backend -f`
3. Verify port 5000 is accessible: `netstat -tlnp | grep 5000`

### Backup Fails
If automatic backup fails:
1. Create manual backup: `mysqldump -u lxcloud -plxcloud123 lxcloud > backup.sql`
2. Use `--skip-backup` to proceed without backup
3. Check database permissions and disk space

### Migration Fails
If database migration fails:
1. Check database logs: `journalctl -u mariadb -f`
2. Verify database credentials in `/opt/lxcloud/backend/app.py`
3. Try manual migration by restarting the backend service

## Recovery

### Restore from Backup
```bash
# Stop services
sudo systemctl stop lxcloud-backend

# Restore database
mysql -u lxcloud -plxcloud123 lxcloud < /tmp/lxcloud_backup_YYYYMMDD_HHMMSS.sql

# Restart services
sudo systemctl start lxcloud-backend
```

### Complete Reinstall
```bash
# Clean install (removes all data)
./install.sh --clean-data --non-interactive
```

## Support

- **Version Info**: `curl http://localhost:5000/api/version`
- **Service Status**: `systemctl status lxcloud-backend nginx`
- **Logs**: `journalctl -u lxcloud-backend -f`
- **Database**: `mysql -u lxcloud -plxcloud123 lxcloud`