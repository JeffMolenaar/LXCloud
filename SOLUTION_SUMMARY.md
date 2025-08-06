# 🚀 LXCloud Update System - COMPLETE SOLUTION

## 📋 Problem Solved

**Original Issue (Dutch):** *"ik zie de vorige updates niet zodra ik het install script gebruik. zorg ervoor dat ik altijd kan updaten naar de laatste versie. zorg ervoor dat dat 1 runnable script is die alles aan past. ook de database tables. desnoods verwijderd die de volledige database en maakt ie een nieuwe aan"*

**Translation:** "I don't see the previous updates as soon as I use the install script. Make sure I can always update to the latest version. Make sure it's 1 runnable script that adjusts everything, including the database tables. If necessary, delete the entire database and create a new one."

## ✅ Solution Implemented

### 🎯 **ONE RUNNABLE SCRIPT FOR EVERYTHING**
```bash
./install.sh    # Handles BOTH installation AND updates
```

### 🔄 **ALWAYS UPDATE TO LATEST VERSION**
- Automatic version detection
- Compares current vs available version
- Updates only when needed (or --force-update)

### 📚 **SEE PREVIOUS UPDATES**
```bash
curl http://localhost:5000/api/version
```
Shows complete installation/update history

### 🗄️ **DATABASE TABLE UPDATES**
- Automatic schema migrations
- Version tracking system
- Preserves existing data

### 🧹 **CLEAN DATABASE OPTION**
```bash
./install.sh --clean-data    # Completely recreates database
```

## 🛠️ How to Use

### First Time Installation
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

### Quick Update
```bash
./update.sh
```

### Check Current Version
```bash
./check_version.sh
```

### Force Update (Same Version)
```bash
./install.sh --force-update
```

### Clean Update (Removes All Data)
```bash
./install.sh --clean-data
```

## 🔍 Version Tracking

The system now tracks:
- ✅ Current application version
- ✅ Database schema version  
- ✅ Installation/update history
- ✅ Previous versions installed
- ✅ Update timestamps and notes

## 🛡️ Data Safety

### Automatic Backups
Every update creates a database backup:
```
/tmp/lxcloud_backup_YYYYMMDD_HHMMSS.sql
```

### Restore from Backup
```bash
mysql -u lxcloud -plxcloud123 lxcloud < backup.sql
```

### Skip Backup (Faster Updates)
```bash
./install.sh --skip-backup
```

## 📊 Update Process

1. **Detection** - Finds existing installation
2. **Version Check** - Compares current vs target
3. **Backup** - Creates database backup
4. **Update** - Updates application files
5. **Migration** - Updates database schema
6. **Restart** - Restarts services
7. **Record** - Logs update in history

## 🧪 Testing

Test the system:
```bash
./test_update_system.sh
```

## 📖 Available Scripts

| Script | Purpose |
|--------|---------|
| `install.sh` | Main installation/update script |
| `update.sh` | Quick update wrapper |
| `check_version.sh` | Version checker |
| `test_update_system.sh` | System testing |

## 🆘 Help & Options

```bash
./install.sh --help
```

Options:
- `--clean-data` - Remove all data (fresh start)
- `--force-update` - Update even if same version
- `--skip-backup` - Skip database backup
- `--non-interactive` - No prompts (automation)

## 🎉 Result

**EXACTLY what was requested:**
- ✅ Single runnable script (`./install.sh`)
- ✅ Always updates to latest version
- ✅ Shows previous updates (version history)
- ✅ Updates database tables (migrations)
- ✅ Can clean database if needed (`--clean-data`)

**The user can now run `./install.sh` at any time and it will:**
1. Detect if LXCloud is already installed
2. Show current vs available version
3. Preserve data and create backups
4. Update everything including database schema
5. Record the update so it's visible in history

**No more missing updates!** 🎯