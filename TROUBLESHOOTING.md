# Troubleshooting Blank Page Issues

If you're seeing a blank page when accessing LXCloud (e.g., at http://192.168.2.171), this guide will help you diagnose and fix the issue.

## Quick Diagnosis

Run the diagnostic script to check your setup:

```bash
cd LXCloud
python3 diagnose.py
```

This script will check:
- Python and Node.js versions
- Frontend build status
- Backend dependencies
- Network configuration
- Running services

## Common Causes and Solutions

### 1. Frontend Not Built

**Symptoms:** Blank page, 404 errors for static files

**Solution:**
```bash
cd frontend
npm install
npm run build
```

**Verification:** Check that `frontend/dist/index.html` exists

### 2. Backend Not Running or Database Issues

**Symptoms:** API errors, "Cannot connect to server" messages

**Quick Solution (No Database Required):**
```bash
cd backend
source venv/bin/activate
python app_standalone.py
```

**Full Solution (With Database):**
```bash
# Install and setup database first
sudo apt install mariadb-server
sudo mysql_secure_installation

# Create database
sudo mysql -u root -p
CREATE DATABASE lxcloud;
CREATE USER 'lxcloud'@'localhost' IDENTIFIED BY 'lxcloud123';
GRANT ALL PRIVILEGES ON lxcloud.* TO 'lxcloud'@'localhost';
EXIT;

# Start backend
cd backend
source venv/bin/activate
python app.py
```

### 3. CORS / Network Access Issues

**Symptoms:** Works on localhost but not on local network IP

**Solution:** The updated `app.py` now includes improved CORS handling that allows access from any local network IP. No additional configuration needed.

### 4. Port or Service Conflicts

**Symptoms:** "Address already in use" errors

**Solution:**
```bash
# Check what's using the ports
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :5000

# Kill conflicting processes or use different ports
```

## Testing Modes

### 1. Standalone Mode (Recommended for Testing)

Runs frontend and backend together without database requirements:

```bash
cd backend
source venv/bin/activate
python app_standalone.py
```

Access at: `http://[your-ip]:80`

### 2. Development Mode

Backend only (requires separate frontend serving):

```bash
cd backend
source venv/bin/activate
python app.py
```

Frontend development server:
```bash
cd frontend
npm run dev
```

### 3. Production Mode

Full setup with nginx (see main README.md installation guide)

## Network Access Configuration

For local network access (e.g., http://192.168.2.171):

1. **Ensure firewall allows traffic:**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 5000/tcp
   ```

2. **Check your IP address:**
   ```bash
   ip addr show | grep inet
   ```

3. **Test connectivity:**
   ```bash
   # From another device on the network
   curl http://[your-ip]/api/health
   ```

## Specific Error Messages

### "Cannot connect to server"
- Backend not running → Start backend with `python app.py` or `python app_standalone.py`
- Wrong port → Check if backend is on port 5000 (development) or 80 (standalone)
- Firewall blocking → Allow ports 80 and 5000

### "Network Error" / "CORS Error"
- Fixed in updated version → Use the improved `app.py` with CORS support
- Still having issues → Try standalone mode: `python app_standalone.py`

### Database Connection Errors
- For testing → Use `python app_standalone.py` (no database required)
- For production → Install MariaDB/MySQL and run installation script

### "Frontend not found" / 404 Errors
- Build frontend → `cd frontend && npm run build`
- Check dist folder → Ensure `frontend/dist/index.html` exists

## Quick Fix Commands

```bash
# Complete setup from scratch
cd LXCloud

# 1. Build frontend
cd frontend && npm install && npm run build && cd ..

# 2. Setup backend
cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && cd ..

# 3. Start in standalone mode (easiest)
cd backend && source venv/bin/activate && python app_standalone.py

# Access at http://[your-ip]:80
```

## Getting Help

1. Run `python3 diagnose.py` for automated diagnosis
2. Check logs when starting backend
3. Test with standalone mode first
4. Verify network connectivity with curl
5. Check firewall settings

For persistent issues, check the main README.md for full installation instructions or create an issue on GitHub.