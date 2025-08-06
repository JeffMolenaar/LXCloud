# LXCloud - LED Screen Management Platform

A complete cloud platform for managing LED screens with Android controllers. Features real-time monitoring, map-based visualization, user management, and data analytics.

## Features

### 🎯 Core Functionality
- **Secure Controller Registration**: Controllers register via encrypted API with authentication keys
- **User Authentication**: Secure login/register system with 2FA support
- **Map Dashboard**: Interactive map showing all screen locations with real-time status
- **Screen Management**: Add, edit, delete, and monitor LED screens
- **Real-time Updates**: WebSocket-based live updates for screen status and data
- **Data Analytics**: View and export screen data in JSON format
- **Custom Naming**: Assign custom names to screens linked to serial numbers

### 🔐 Security & Access Control
- **Super Admin Account**: Master admin account with full system access
- **Administrator Flags**: Regular users can be granted administrator privileges
- **Controller Assignment**: Controllers can only be assigned to one user at a time
- **Data Privacy**: Controllers only store data when assigned to a user
- **API Authentication**: Secure authentication keys for controller registration

### 🖥️ User Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Interactive Map**: Click on screen markers to view detailed information
- **User Dropdown**: Access password change and 2FA settings from header
- **Admin Panel**: Comprehensive user and controller management
- **Bulk Operations**: Select multiple screens for batch operations
- **Real-time Status**: Live online/offline status indicators
- **Data Export**: Download screen data as JSON files

### 🔧 Technical Stack
- **Backend**: Python Flask with WebSocket support and secure API endpoints
- **Frontend**: React.js with Leaflet maps
- **Database**: MariaDB with automatic migrations and yearly data retention
- **Real-time**: Socket.io for live updates
- **Authentication**: Session-based with password hashing and 2FA support

### 📱 Controller Integration
- **API Registration**: `/api/controller/register` for secure device registration
- **Authentication**: SHA256-based authentication keys for controllers
- **Background Operation**: Controllers work in background until assigned
- **Assignment Workflow**: Users assign controllers by entering serial numbers
- **Data Collection**: Location, serial number, status, and custom information
- **Conditional Storage**: Data only stored when controllers are assigned to users
- **Real-time Sync**: Immediate updates to dashboard when devices send data

## Quick Installation (Ubuntu Server 22.04)

### Fresh Installation

Run the automated installation script:

```bash
git clone https://github.com/JeffMolenaar/LXCloud.git
cd LXCloud
chmod +x install.sh
./install.sh
```

### Complete Clean Installation

To perform a completely fresh installation that removes all existing data:

```bash
cd LXCloud
git pull origin main
./install.sh --clean-data
```

This will:
- Drop and recreate the entire database
- Remove all user accounts, controllers, and screen data
- Perform a fresh installation from scratch

### Database Reset

For resetting just the database while keeping the application:

```bash
cd LXCloud
./reset_database.sh
```

### Updating Existing Installation

To update an existing LXCloud installation to the latest version:

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

### Update Options

- **Standard Update**: Preserves all data and runs database migrations
- **Clean Update**: Removes all data and performs fresh installation (`--clean-data`)
- **Force Update**: Reinstalls even if versions match (`--force-update`)
- **Non-Interactive**: Runs without prompts (`--non-interactive`)
- **Skip Backup**: Skips database backup during update (`--skip-backup`)

### Version Management

The install script automatically:
- Detects existing installations
- Checks current vs target version
- Creates database backups before updates
- Runs database schema migrations
- Records installation/update history

Check your current version:
```bash
curl http://localhost:5000/api/version
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

### 1. Initial Setup

#### Create Admin Account
After installation, create the initial admin account:

**Option 1: Via API**
```bash
curl -X POST http://your-server:5000/api/admin/create-admin \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "your-secure-password",
    "admin_key": "lxcloud-admin-setup-2024"
  }'
```

**Option 2: Via Web Interface**
1. Visit your server IP in a web browser
2. Click "Register" to create an account
3. The first registered user will have admin privileges

### 2. Controller Registration & Assignment

#### Controller Registration (for device developers)
Controllers (LED screens with Android devices) can register themselves:

```bash
# Calculate authentication key for controller
SERIAL="SCREEN001"
AUTH_KEY=$(echo -n "lxcloud-controller-$SERIAL" | sha256sum | cut -c1-16)

# Register controller
curl -X POST http://your-server:5000/api/controller/register \
  -H 'Content-Type: application/json' \
  -d '{
    "serial_number": "'$SERIAL'",
    "latitude": 52.3676,
    "longitude": 4.9041,
    "auth_key": "'$AUTH_KEY'"
  }'
```

#### Assigning Controllers to Users
1. Log in to the web interface
2. Controllers register in the background and appear in admin panel
3. Users can assign controllers by entering the serial number in "Manage Screens"
4. Once assigned, controllers will start storing data

### 3. User Registration
1. Visit the web interface
2. Click "Register" to create a new account
3. Fill in username, email, and password
4. Admin can grant administrator privileges to users

### 4. Managing Screens
- **Dashboard**: View all assigned screens on an interactive map
- **Screen Management**: Bulk operations, editing, and deletion
- **Data View**: Click on screens to view detailed data and export JSON
- **Admin Panel**: View all controllers (assigned and unassigned)

## API Documentation

### Authentication Endpoints
- `POST /api/register` - Register new user
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `GET /api/user` - Get current user info
- `POST /api/user/change-password` - Change user password
- `POST /api/user/2fa/setup` - Setup 2FA
- `POST /api/user/2fa/verify` - Verify and enable 2FA
- `POST /api/user/2fa/disable` - Disable 2FA

### Screen Management
- `GET /api/screens` - Get user's screens (or all screens for admin)
- `POST /api/screens` - Add/assign new screen by serial number
- `PUT /api/screens/{id}` - Update screen
- `DELETE /api/screens/{id}` - Delete screen
- `GET /api/screens/{id}/data` - Get screen data

### Controller Integration
- `POST /api/controller/register` - Secure controller registration
  ```json
  {
    "serial_number": "DEVICE001",
    "latitude": 52.3676,
    "longitude": 4.9041,
    "auth_key": "calculated_auth_key"
  }
  ```
- `POST /api/device/update` - Device data update (stores data only if assigned)
  ```json
  {
    "serial_number": "DEVICE001",
    "latitude": 52.3676,
    "longitude": 4.9041,
    "information": "Status message"
  }
  ```

### Admin Endpoints
- `POST /api/admin/create-admin` - Create initial admin account
- `GET /api/admin/users` - Get all users (admin only)
- `POST /api/admin/users/{id}/toggle-admin` - Toggle administrator flag

### System Endpoints
- `GET /api/health` - Health check
- `GET /api/version` - Get version and installation info

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_administrator BOOLEAN DEFAULT FALSE,
    two_fa_enabled BOOLEAN DEFAULT FALSE,
    two_fa_secret VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Controllers Table (Unassigned Devices)
```sql
CREATE TABLE controllers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    serial_number VARCHAR(100) UNIQUE NOT NULL,
    registration_key VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    online_status BOOLEAN DEFAULT FALSE,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned BOOLEAN DEFAULT FALSE
);
```

### Screens Table (Assigned to Users)
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
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Screen Data Table (Only for Assigned Screens)
```sql
CREATE TABLE screen_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    screen_id INT,
    information TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    year INT,
    FOREIGN KEY (screen_id) REFERENCES screens(id) ON DELETE CASCADE,
    INDEX idx_year (year),
    INDEX idx_timestamp (timestamp)
);
```

### Schema Version Table
```sql
CREATE TABLE schema_version (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version INT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### App Info Table
```sql
CREATE TABLE app_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_version VARCHAR(20) NOT NULL,
    install_type ENUM('fresh', 'update') NOT NULL,
    previous_version VARCHAR(20),
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
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

---

**LXCloud** - Comprehensive LED Screen Management Platform
