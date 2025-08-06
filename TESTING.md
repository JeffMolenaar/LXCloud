# LXCloud Testing and Troubleshooting Guide

## Quick Testing

### 1. Test Authentication (After Installation)

```bash
# Make sure the backend is running
cd /home/runner/work/LXCloud/LXCloud
python3 test_auth.py
```

### 2. Test Local Network Access

#### From the Server:
```bash
# Check what IP addresses are available
hostname -I

# Test local access
curl http://localhost/api/health
curl http://[YOUR_SERVER_IP]/api/health
```

#### From Another Device on the Network:
1. Find your server's IP address (from hostname -I above)
2. Open a web browser and go to: `http://[SERVER_IP]`
3. Try registering a new user
4. Try logging in

## Installation Options

### Clean Installation (Recommended)
```bash
./install.sh --clean-data
```

### Interactive Installation (Default)
```bash
./install.sh
# Choose option 1 for clean install when prompted
```

### Non-Interactive with Data Cleanup
```bash
./install.sh --clean-data --non-interactive
```

## Common Issues and Solutions

### 1. Cannot Access from Other Devices

**Problem**: Web interface works on server but not from other devices on network.

**Solutions**:
- Verify firewall allows port 80: `sudo ufw status`
- Check if nginx is running: `sudo systemctl status nginx`
- Verify server IP: `hostname -I`
- Test network connectivity from client: `ping [SERVER_IP]`

### 2. Registration/Login Fails

**Problem**: Frontend shows errors during registration or login.

**Solutions**:
- Check backend service: `sudo systemctl status lxcloud-backend`
- Check backend logs: `sudo journalctl -u lxcloud-backend -f`
- Test API directly: `curl http://localhost:5000/api/health`
- Verify database connection: `mysql -u lxcloud -plxcloud123 -e "USE lxcloud; SHOW TABLES;"`

### 3. CORS Errors in Browser

**Problem**: Browser console shows CORS errors.

**Solutions**:
- Restart backend service: `sudo systemctl restart lxcloud-backend`
- Check nginx configuration: `sudo nginx -t`
- Clear browser cache and cookies
- Try incognito/private mode

### 4. Database Connection Errors

**Problem**: Backend cannot connect to database.

**Solutions**:
- Check MariaDB status: `sudo systemctl status mariadb`
- Test database login: `mysql -u lxcloud -plxcloud123`
- Reset database user:
  ```sql
  sudo mysql -u root -p
  DROP USER 'lxcloud'@'localhost';
  CREATE USER 'lxcloud'@'localhost' IDENTIFIED BY 'lxcloud123';
  GRANT ALL PRIVILEGES ON lxcloud.* TO 'lxcloud'@'localhost';
  FLUSH PRIVILEGES;
  ```

## Manual Testing Steps

### 1. Test Backend API
```bash
# Health check
curl http://localhost:5000/api/health

# Register user
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123"}' \
  -c cookies.txt

# Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}' \
  -b cookies.txt -c cookies.txt

# Get current user
curl http://localhost:5000/api/user -b cookies.txt
```

### 2. Test Frontend (After Build)
```bash
cd frontend
npm install
npm run build
# Then access via nginx
```

## Environment Configuration

### Frontend Environment Variables
Create `frontend/.env`:
```
# For development with custom backend
REACT_APP_API_URL=http://192.168.1.100:5000/api

# Or specify just the host
REACT_APP_BACKEND_HOST=192.168.1.100
REACT_APP_BACKEND_PORT=5000
```

### Backend Environment Variables
```bash
export DB_HOST=localhost
export DB_USER=lxcloud
export DB_PASS=lxcloud123
export DB_NAME=lxcloud
export SECRET_KEY=your-production-secret-key
```

## Network Configuration for Local Access

### 1. Firewall Rules
```bash
# Allow HTTP traffic
sudo ufw allow 80/tcp

# Allow specific port for development
sudo ufw allow 5000/tcp

# Check status
sudo ufw status
```

### 2. Network Discovery
```bash
# Find your network range
ip route | grep 'scope link'

# Scan for devices (install nmap if needed)
nmap -sn 192.168.1.0/24
```

### 3. Test from Another Device
```bash
# Install curl on the client device, then:
curl http://[SERVER_IP]/api/health
curl http://[SERVER_IP]
```

## Data Management

### Clean All Data
```bash
cd /home/runner/work/LXCloud/LXCloud
python3 cleanup_data.py --years 0 --dry-run  # Preview
python3 cleanup_data.py --years 0             # Actually clean
```

### Backup Data
```bash
mysqldump -u lxcloud -plxcloud123 lxcloud > backup_$(date +%Y%m%d).sql
```

### Restore Data
```bash
mysql -u lxcloud -plxcloud123 lxcloud < backup_20231215.sql
```