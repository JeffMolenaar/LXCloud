# LXCloud - LED Screen Management Platform

A complete cloud platform for managing LED screens with Android controllers. Features real-time monitoring, map-based visualization, user management, and data analytics.

## Features

### 🎯 Core Functionality
- **User Authentication**: Secure login/register system with 2FA support
- **Admin System**: Two-tier administration (Super Admin + Administrator)
- **Controller Management**: Self-registering controllers with assignment workflow
- **Map Dashboard**: Interactive map showing all screen locations with real-time status
- **Screen Management**: Add, edit, delete, and monitor LED screens
- **Real-time Updates**: WebSocket-based live updates for screen status and data
- **Data Analytics**: View and export screen data in JSON format
- **Custom Naming**: Assign custom names to screens linked to serial numbers

### 🔐 Security & Admin Features
- **Role-Based Access**: Super Admin and Administrator roles
- **2FA Authentication**: TOTP-based two-factor authentication
- **Password Management**: Secure password change functionality
- **Data Isolation**: Controllers only store data when assigned to users
- **Admin Panel**: Comprehensive admin dashboard for user and controller management

### 🖥️ User Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Interactive Map**: Click on screen markers to view detailed information
- **Bulk Operations**: Select multiple screens for batch operations
- **Real-time Status**: Live online/offline status indicators
- **Data Export**: Download screen data as JSON files

### 🔧 Technical Stack
- **Backend**: Python Flask with WebSocket support
- **Frontend**: React.js with Leaflet maps
- **Database**: MariaDB with yearly data retention
- **Real-time**: Socket.io for live updates
- **Authentication**: Session-based with password hashing

### 📱 Android Integration
- **Controller Registration**: Automatic self-registration via encrypted API
- **API Endpoint**: `/api/controller/register` for device registration
- **Data Collection**: Location, serial number, status, and custom information
- **Assignment Workflow**: Controllers register automatically, users assign by serial number
- **Real-time Sync**: Immediate updates to dashboard when devices send data
- **Data Security**: Only assigned controllers store data in database

## Quick Installation (Ubuntu Server 22.04)

Run the automated installation script:

```bash
git clone https://github.com/JeffMolenaar/LXCloud.git
cd LXCloud
chmod +x install.sh
./install.sh
```

The script will:
- Install all dependencies (Node.js, Python, MariaDB, Nginx)
- Set up the database
- Configure services
- Set up firewall rules
- Start the application

After installation, visit `http://your-server-ip` to access the platform.

## Manual Installation

### Prerequisites
- Ubuntu Server 22.04 LTS
- Root or sudo access
- Internet connection

### 1. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Python and MariaDB
sudo apt install -y python3 python3-pip python3-venv mariadb-server nginx
```

### 2. Database Setup

```bash
# Secure MariaDB
sudo mysql_secure_installation

# Create database
sudo mysql -u root -p
```

```sql
CREATE DATABASE lxcloud;
CREATE USER 'lxcloud'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON lxcloud.* TO 'lxcloud'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Application Setup

```bash
# Clone repository
git clone https://github.com/JeffMolenaar/LXCloud.git
cd LXCloud

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
npm run build
```

### 4. Service Configuration

Create systemd service:

```bash
sudo nano /etc/systemd/system/lxcloud-backend.service
```

```ini
[Unit]
Description=LXCloud Backend
After=network.target mariadb.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/LXCloud/backend
Environment=PATH=/path/to/LXCloud/backend/venv/bin
ExecStart=/path/to/LXCloud/backend/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5. Nginx Configuration

```nginx
server {
    listen 80;
    server_name your_domain;

    location / {
        root /path/to/LXCloud/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /socket.io/ {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 6. Start Services

```bash
sudo systemctl enable lxcloud-backend
sudo systemctl start lxcloud-backend
sudo systemctl enable nginx
sudo systemctl restart nginx
```

## Usage

### 1. User Registration
1. Visit the web interface
2. Click "Register" to create a new account
3. Fill in username, email, and password

### 2. Adding Screens
1. Log in to the dashboard
2. Click the "+" button to add a new screen
3. Enter the serial number and optional custom name
4. The screen will appear on the map once it sends location data

### 3. Android Device Configuration
Configure your Android devices to send POST requests to:
```
http://your-server/api/device/update
```

With JSON payload:
```json
{
  "serial_number": "SCREEN001",
  "latitude": 52.3676,
  "longitude": 4.9041,
  "information": "Optional status message"
}
```

### 4. Managing Screens
- **Dashboard**: View all screens on an interactive map
- **Screen Management**: Bulk operations, editing, and deletion
- **Data View**: Click on screens to view detailed data and export JSON

## API Documentation

### Authentication Endpoints
- `POST /api/register` - Register new user
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `GET /api/user` - Get current user info

### Screen Management
- `GET /api/screens` - Get user's screens
- `POST /api/screens` - Add new screen
- `PUT /api/screens/{id}` - Update screen
- `DELETE /api/screens/{id}` - Delete screen
- `GET /api/screens/{id}/data` - Get screen data

### Device Integration
- `POST /api/device/update` - Android device data update
- `POST /api/controller/register` - Controller self-registration

### Admin Management
- `GET /api/admin/users` - List all users (admin only)
- `POST /api/admin/users/{id}/toggle-admin` - Toggle user admin status
- `POST /api/admin/create-admin` - Create initial admin account

### User Security
- `POST /api/user/change-password` - Change user password
- `POST /api/user/2fa/setup` - Setup two-factor authentication
- `POST /api/user/2fa/verify` - Verify and enable 2FA
- `POST /api/user/2fa/disable` - Disable 2FA

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Screens Table
```sql
CREATE TABLE screens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    serial_number VARCHAR(100) UNIQUE NOT NULL,
    user_id INT,
    custom_name VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    online_status BOOLEAN DEFAULT FALSE,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Screen Data Table
```sql
CREATE TABLE screen_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    screen_id INT,
    information TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    year INT,
    FOREIGN KEY (screen_id) REFERENCES screens(id),
    INDEX idx_year (year)
);
```

## Configuration

### Environment Variables
You can configure the application using environment variables:

- `DB_HOST` - Database host (default: localhost)
- `DB_USER` - Database user (default: lxcloud)
- `DB_PASS` - Database password (default: lxcloud123)
- `DB_NAME` - Database name (default: lxcloud)
- `SECRET_KEY` - Flask secret key (change in production)

### Data Retention
The system automatically stores data by year and provides mechanisms for yearly data cleanup. Old data can be removed by deleting records where `year < current_year`.

## Scaling Considerations

### For 500+ Screens
- **Database Indexing**: Proper indexes on timestamp and year columns
- **Connection Pooling**: Configure MariaDB connection pooling
- **Load Balancing**: Use multiple backend instances with nginx load balancing
- **Caching**: Implement Redis for session storage and caching
- **Data Archiving**: Automated yearly data archiving and cleanup

### Performance Optimizations
- **Database**: Regular maintenance and optimization
- **Frontend**: CDN for static assets
- **Backend**: Async processing for bulk operations
- **Monitoring**: Application performance monitoring

## Security

### Production Recommendations
1. **HTTPS**: Configure SSL certificates
2. **Database**: Change default passwords
3. **Firewall**: Restrict database access
4. **Updates**: Keep all dependencies updated
5. **Backup**: Regular database backups
6. **Monitoring**: Log monitoring and alerting

## Troubleshooting

### Service Status
```bash
sudo systemctl status lxcloud-backend
sudo systemctl status nginx
sudo systemctl status mariadb
```

### Logs
```bash
sudo journalctl -u lxcloud-backend -f
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Common Issues
1. **Database Connection**: Check MariaDB service and credentials
2. **Port Conflicts**: Ensure ports 80, 3000, 5000 are available
3. **Permissions**: Check file permissions in application directory
4. **Firewall**: Verify firewall rules allow HTTP traffic

## Development

### Local Development Setup
```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Building for Production
```bash
cd frontend
npm run build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the logs for error details

## New Features (Latest Update)

### Controller Self-Registration
Controllers can now register themselves automatically without manual setup. Users can then assign controllers by entering their serial number.

### Admin System
- **Super Admin**: Full system access, can create administrators
- **Administrator**: Can view all screens and manage users
- **Admin Panel**: Comprehensive dashboard for system management

### Enhanced Security
- **Two-Factor Authentication**: TOTP-based 2FA with QR code setup
- **Password Management**: Secure password change functionality
- **User Profile**: Dropdown menu with security options

### Data Protection
- **Assignment-Based Storage**: Controllers only store data when assigned to users
- **Data Isolation**: Prevents cross-user data access
- **Admin Visibility**: Admins can see all controllers including unassigned ones

For detailed documentation on new features, see [NEW_FEATURES.md](NEW_FEATURES.md).

---

**LXCloud** - Comprehensive LED Screen Management Platform
