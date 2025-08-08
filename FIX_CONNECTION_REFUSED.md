# Fix for ERR_CONNECTION_REFUSED

If you're getting **ERR_CONNECTION_REFUSED** when trying to access LXCloud on your network IP (like 192.168.2.171), follow these steps:

## Quick Start (Recommended)

1. **Start LXCloud**:
   ```bash
   ./start.sh
   ```

2. **Configure Network Access**:
   ```bash
   ./configure-network.sh
   ```

## Manual Steps

### 1. Ensure LXCloud is Running

Make sure the backend server is running:
```bash
cd backend
source venv/bin/activate
python app.py
```

You should see output like:
```
Starting Flask application on:
  - http://localhost:5000 (API)
  - All interfaces (0.0.0.0:5000)
```

### 2. Configure Firewall

**Ubuntu/Debian with UFW:**
```bash
sudo ufw allow 5000/tcp
sudo ufw enable
```

**CentOS/RHEL with firewalld:**
```bash
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

**Generic iptables:**
```bash
sudo iptables -I INPUT -p tcp --dport 5000 -j ACCEPT
```

### 3. Check Your IP Address

Find your server's IP address:
```bash
hostname -I
```

### 4. Test Connection

From another device on the same network, try:
```bash
curl http://YOUR_SERVER_IP:5000/api/health
```

Replace `YOUR_SERVER_IP` with your actual server IP.

## Access URLs

Once running, LXCloud will be available at:
- **Local**: http://localhost:5000
- **Network**: http://YOUR_SERVER_IP:5000 (e.g., http://192.168.2.171:5000)

## Troubleshooting

### Still getting ERR_CONNECTION_REFUSED?

1. **Check if service is running**:
   ```bash
   netstat -tlnp | grep :5000
   ```

2. **Check firewall status**:
   ```bash
   sudo ufw status    # Ubuntu/Debian
   sudo firewall-cmd --list-all    # CentOS/RHEL
   ```

3. **Check router/network settings**:
   - Some routers block inter-device communication
   - Check if "AP Isolation" is disabled
   - Verify devices are on the same subnet

4. **Check antivirus/security software**:
   - Windows Defender Firewall
   - Third-party antivirus programs
   - VPN software

### Common Network Issues

- **Wrong IP**: Make sure you're using the correct server IP
- **Port conflicts**: Another service might be using port 5000
- **Network isolation**: Some networks isolate devices for security
- **Router settings**: Check router firewall and access control settings

## Modern UI Features

LXCloud includes a beautiful, modern UI with:
- **Responsive design** that works on desktop, tablet, and mobile
- **Interactive maps** for screen location visualization
- **Real-time updates** via WebSocket connections
- **Clean, modern styling** with gradient headers and card layouts
- **User-friendly navigation** with intuitive controls
- **Professional dashboard** with statistics and quick actions

## Production Deployment

For production use, consider:
1. Using nginx as a reverse proxy
2. Running with a production WSGI server (gunicorn)
3. Enabling HTTPS with SSL certificates
4. Setting up proper database backups
5. Configuring log rotation

See the main README.md for detailed production setup instructions.