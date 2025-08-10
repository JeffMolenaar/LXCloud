from flask import Flask, request, jsonify, session, make_response, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import os
from datetime import datetime, timedelta
import json
import secrets
import hashlib
import pyotp
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'lxcloud-secret-key-change-in-production')

# Configure session for better security and local network access
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# CORS configuration for local network access
def configure_cors():
    """Configure CORS origins dynamically"""
    allowed_origins = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost',
        'http://127.0.0.1'
    ]
    
    # Add local network IPs if available
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        if local_ip and local_ip != '127.0.0.1':
            allowed_origins.extend([
                f'http://{local_ip}',
                f'http://{local_ip}:3000'
            ])
            
        # Add common local network ranges for better compatibility
        import netifaces
        for interface in netifaces.interfaces():
            try:
                addrs = netifaces.ifaddresses(interface)
                for addr_family in addrs:
                    for addr_info in addrs[addr_family]:
                        if 'addr' in addr_info:
                            ip = addr_info['addr']
                            # Add common private network ranges
                            if (ip.startswith('192.168.') or 
                                ip.startswith('10.') or 
                                ip.startswith('172.')):
                                allowed_origins.extend([
                                    f'http://{ip}',
                                    f'http://{ip}:3000',
                                    f'http://{ip}:80'
                                ])
            except:
                pass
    except ImportError:
        # netifaces not available, use basic method
        pass
    except:
        pass
    
    return allowed_origins

# For local network compatibility, allow all origins in development
# In production, this should be more restrictive
CORS(app, 
     supports_credentials=True,
     origins="*",  # Allow all origins for local network testing
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   async_mode='threading')

# Database configuration with environment variable support
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'lxcloud'),
    'password': os.environ.get('DB_PASS', 'lxcloud123'),
    'database': os.environ.get('DB_NAME', 'lxcloud'),
    'charset': 'utf8mb4'
}

def get_db_connection():
    """Get database connection with error handling"""
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Please ensure MariaDB/MySQL is running and credentials are correct")
        raise

def require_auth():
    """Check if user is authenticated"""
    if 'user_id' not in session:
        return False, jsonify({'error': 'Not authenticated'}), 401
    return True, None, None

def require_admin():
    """Check if user is admin or administrator"""
    if 'user_id' not in session:
        return False, jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT is_admin, is_administrator FROM users WHERE id = %s",
        (session['user_id'],)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not user or (not user[0] and not user[1]):
        return False, jsonify({'error': 'Admin access required'}), 403
    
    return True, None, None

def generate_registration_key():
    """Generate a secure registration key for controllers"""
    return secrets.token_urlsafe(32)

# Application version
APP_VERSION = "1.1.3.0"
DATABASE_VERSION = 4

def get_database_version():
    """Get current database version"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else 0
    except:
        return 0

def set_database_version(version):
    """Set database version"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO schema_version (version, updated_at) VALUES (%s, CURRENT_TIMESTAMP)",
            (version,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Database version updated to {version}")
    except Exception as e:
        print(f"Failed to update database version: {e}")

def run_database_migrations():
    """Run database migrations"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        current_version = get_database_version()
        print(f"Current database version: {current_version}")
        print(f"Target database version: {DATABASE_VERSION}")
        
        if current_version < DATABASE_VERSION:
            print("Running database migrations...")
            
            # Migration from version 0 to 1 (initial schema)
            if current_version < 1:
                print("Creating initial database schema...")
                
                # Schema version table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS schema_version (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        version INT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        is_admin BOOLEAN DEFAULT FALSE,
                        is_administrator BOOLEAN DEFAULT FALSE,
                        two_fa_enabled BOOLEAN DEFAULT FALSE,
                        two_fa_secret VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Controllers registration table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS controllers (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        serial_number VARCHAR(100) UNIQUE NOT NULL,
                        registration_key VARCHAR(255) NOT NULL,
                        latitude DECIMAL(10, 8),
                        longitude DECIMAL(11, 8),
                        online_status BOOLEAN DEFAULT FALSE,
                        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        assigned BOOLEAN DEFAULT FALSE
                    )
                """)
                
                # Screens table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS screens (
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
                    )
                """)
                
                # Screen data table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS screen_data (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        screen_id INT,
                        information TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        year INT,
                        FOREIGN KEY (screen_id) REFERENCES screens(id) ON DELETE CASCADE,
                        INDEX idx_year (year),
                        INDEX idx_timestamp (timestamp)
                    )
                """)
                
                set_database_version(1)
                print("Migration to version 1 completed")
            
            # Migration from version 1 to 2 (add app_info table for tracking installs/updates)
            if current_version < 2:
                print("Adding application info tracking...")
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS app_info (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        app_version VARCHAR(20) NOT NULL,
                        install_type ENUM('fresh', 'update') NOT NULL,
                        previous_version VARCHAR(20),
                        installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        notes TEXT
                    )
                """)
                
                # Record this migration
                cursor.execute("""
                    INSERT INTO app_info (app_version, install_type, notes)
                    VALUES (%s, 'update', 'Database migration to add version tracking')
                """, (APP_VERSION,))
                
                set_database_version(2)
                print("Migration to version 2 completed")
            
            # Migration from version 2 to 3 (add admin_settings table)
            if current_version < 3:
                print("Adding admin settings table...")
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS admin_settings (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        setting_key VARCHAR(100) UNIQUE NOT NULL,
                        setting_value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_setting_key (setting_key)
                    )
                """)
                
                # Insert default settings
                default_settings = [
                    ('logoText', 'LXCloud'),
                    ('siteName', 'LXCloud - LED Screen Management Platform')
                ]
                
                for key, value in default_settings:
                    cursor.execute("""
                        INSERT IGNORE INTO admin_settings (setting_key, setting_value)
                        VALUES (%s, %s)
                    """, (key, value))
                
                set_database_version(3)
                print("Migration to version 3 completed")
            
            # Migration from version 3 to 4 (add ui_settings table for UI customization)
            if current_version < 4:
                print("Adding UI settings table...")
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ui_settings (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        setting_key VARCHAR(100) UNIQUE NOT NULL,
                        setting_value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_setting_key (setting_key)
                    )
                """)
                
                # Insert default UI settings
                default_ui_settings = [
                    ('app_name', 'LXCloud'),
                    ('primary_color', '#667eea'),
                    ('secondary_color', '#f093fb'),
                    ('header_color', '#667eea'),
                    ('button_color', '#667eea'),
                    ('button_hover_color', '#5a6fd8'),
                    ('logo_url', ''),
                    ('favicon_url', ''),
                    ('background_image_url', ''),
                    ('custom_button_images', '{}'),
                    
                    # Screen management button icons
                    ('screen_view_data_icon', ''),
                    ('screen_edit_icon', ''),
                    ('screen_unbind_icon', ''),
                ]
                
                for key, value in default_ui_settings:
                    cursor.execute("""
                        INSERT IGNORE INTO ui_settings (setting_key, setting_value)
                        VALUES (%s, %s)
                    """, (key, value))
                
                set_database_version(4)
                print("Migration to version 4 completed")
            
            # Migration from version 4 to 5 (add extended UI customization for v1.3)
            if current_version < 5:
                print("Adding extended UI customization settings for version 1.3...")
                
                # Add new UI settings for v1.3
                extended_ui_settings = [
                    # Footer customization
                    ('footer_enabled', 'true'),
                    ('footer_text', 'Powered by LXCloud'),
                    ('footer_color', '#f8f9fa'),
                    ('footer_text_color', '#6c757d'),
                    ('footer_links', '{}'),  # JSON for custom footer links
                    
                    # Typography settings
                    ('font_family', 'system-ui, -apple-system, sans-serif'),
                    ('font_size_base', '16px'),
                    ('font_size_heading', '24px'),
                    ('line_height', '1.5'),
                    
                    # Navigation customization
                    ('nav_style', 'default'),  # default, pills, underline
                    ('nav_position', 'top'),   # top, side
                    ('nav_color', '#667eea'),
                    ('nav_hover_color', '#5a6fd8'),
                    ('header_text_color', '#ffffff'),  # header menu text color
                    
                    # Advanced button customization
                    ('button_style', 'default'),  # default, rounded, square, outline
                    ('button_size', 'medium'),     # small, medium, large
                    ('button_shadow', 'true'),
                    ('button_animation', 'true'),
                    
                    # Page-specific settings
                    ('dashboard_layout', 'grid'),     # grid, list, cards
                    ('dashboard_theme', 'default'),   # default, dark, light
                    ('login_background_url', ''),
                    ('login_style', 'default'),       # default, centered, split
                    
                    # Custom text overrides (JSON)
                    ('custom_text_labels', '{}'),     # Custom text for UI labels
                    ('page_titles', '{}'),            # Custom page titles
                    
                    # Advanced customization
                    ('custom_css', ''),               # Custom CSS injection
                    ('theme_mode', 'light'),          # light, dark, auto
                    ('border_radius', '8px'),         # Global border radius
                    ('spacing_unit', '16px'),         # Base spacing unit
                    
                    # Accessibility settings
                    ('high_contrast', 'false'),
                    ('large_text', 'false'),
                    ('reduced_motion', 'false'),
                    
                    # Advanced header settings
                    ('header_height', '60px'),
                    ('header_shadow', 'true'),
                    ('header_sticky', 'true'),
                    
                    # Card and component styling
                    ('card_shadow', 'true'),
                    ('card_border', 'true'),
                    ('card_hover_effect', 'true'),
                ]
                
                for key, value in extended_ui_settings:
                    cursor.execute("""
                        INSERT IGNORE INTO ui_settings (setting_key, setting_value)
                        VALUES (%s, %s)
                    """, (key, value))
                
                set_database_version(5)
                print("Migration to version 5 completed")
            
            # Migration from version 5 to 6 (add header button customization)
            if current_version < 6:
                print("Adding header button customization settings...")
                
                # Add new header button customization settings
                header_button_settings = [
                    # Header button positioning and styling
                    ('header_button_alignment', 'default'),
                    ('header_button_vertical_alignment', 'center'),
                    ('header_button_spacing', '15px'),
                    ('header_button_individual_positions', '{}'),
                    ('header_button_individual_colors', '{}'),
                    ('header_custom_css', ''),
                ]
                
                for key, value in header_button_settings:
                    cursor.execute("""
                        INSERT IGNORE INTO ui_settings (setting_key, setting_value)
                        VALUES (%s, %s)
                    """, (key, value))
                
                set_database_version(6)
                print("Migration to version 6 completed")
            
            conn.commit()
            print("All database migrations completed successfully")
        else:
            print("Database is up to date")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database migration failed: {e}")
        raise

def init_database():
    """Initialize database with required tables and run migrations"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, create schema_version table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                id INT AUTO_INCREMENT PRIMARY KEY,
                version INT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        
        # Run migrations
        run_database_migrations()
        
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
        print("The application will run but database features will not work")
        print("To fix this issue:")
        print("1. Install and start MariaDB/MySQL")
        print("2. Create database and user as described in README.md")
        print("3. Or use the install.sh script for automatic setup")

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        db_status = 'connected'
    except Exception as e:
        db_status = f'disconnected ({str(e)})'
        
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'timestamp': datetime.now().isoformat(),
        'version': APP_VERSION
    }), 200

# Version endpoint
@app.route('/api/version', methods=['GET'])
def get_version():
    """Get application and database version information"""
    try:
        db_version = get_database_version()
        
        # Get installation history
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT app_version, install_type, previous_version, installed_at, notes
            FROM app_info
            ORDER BY installed_at DESC
            LIMIT 5
        """)
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'app_version': row[0],
                'install_type': row[1],
                'previous_version': row[2],
                'installed_at': row[3].isoformat() if row[3] else None,
                'notes': row[4]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'app_version': APP_VERSION,
            'database_version': db_version,
            'target_database_version': DATABASE_VERSION,
            'installation_history': history
        }), 200
        
    except Exception as e:
        return jsonify({
            'app_version': APP_VERSION,
            'database_version': 'unknown',
            'error': f'Could not retrieve full version info: {str(e)}'
        }), 200

# Controller registration endpoint (secured API for controllers)
@app.route('/api/controller/register', methods=['POST'])
def controller_register():
    """Secure controller registration endpoint for devices to register themselves"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        serial_number = data.get('serial_number', '').strip()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        auth_key = data.get('auth_key', '').strip()
        
        if not serial_number:
            return jsonify({'error': 'Serial number is required'}), 400
        
        # Simple authentication for controllers
        # In production, you would use proper JWT tokens or API keys
        expected_auth_key = hashlib.sha256(f"lxcloud-controller-{serial_number}".encode()).hexdigest()[:16]
        if auth_key and auth_key != expected_auth_key:
            return jsonify({'error': 'Invalid authentication key'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if controller already exists
        cursor.execute("SELECT id, assigned FROM controllers WHERE serial_number = %s", (serial_number,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing controller location and status
            cursor.execute("""
                UPDATE controllers 
                SET latitude = %s, longitude = %s, online_status = TRUE, last_seen = CURRENT_TIMESTAMP
                WHERE serial_number = %s
            """, (latitude, longitude, serial_number))
            
            # Get registration key for response
            cursor.execute("SELECT registration_key FROM controllers WHERE serial_number = %s", (serial_number,))
            reg_key_result = cursor.fetchone()
            registration_key = reg_key_result[0] if reg_key_result else None
        else:
            # Create new controller with registration key
            registration_key = generate_registration_key()
            cursor.execute("""
                INSERT INTO controllers (serial_number, registration_key, latitude, longitude, online_status, assigned)
                VALUES (%s, %s, %s, %s, TRUE, FALSE)
            """, (serial_number, registration_key, latitude, longitude))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': 'Controller registered successfully',
            'serial_number': serial_number,
            'registration_key': registration_key,
            'expected_auth_key': expected_auth_key,
            'status': 'awaiting_assignment'
        }), 200
        
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

# Optional: Serve frontend if no nginx is configured
@app.route('/')
def serve_frontend_fallback():
    """Serve frontend as fallback if no nginx configured"""
    try:
        frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
        return send_from_directory(frontend_path, 'index.html')
    except Exception as e:
        return jsonify({
            'message': 'LXCloud Backend API',
            'status': 'running',
            'note': 'Frontend not found. Please build frontend and configure nginx, or access API directly.',
            'frontend_build': 'Run: cd frontend && npm run build',
            'nginx_setup': 'See README.md for nginx configuration'
        }), 200

@app.route('/<path:path>')
def serve_frontend_static(path):
    """Serve frontend static files as fallback"""
    try:
        frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
        return send_from_directory(frontend_path, path)
    except:
        # Return JSON for API-like requests, fallback for others
        if path.startswith('api/'):
            return jsonify({'error': 'API endpoint not found'}), 404
        else:
            # For frontend routes, serve index.html (React Router)
            try:
                frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
                return send_from_directory(frontend_path, 'index.html')
            except:
                return jsonify({
                    'error': 'Frontend not found',
                    'note': 'Please build frontend: cd frontend && npm run build'
                }), 404

# Handle preflight requests for CORS
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        origin = request.headers.get('Origin')
        
        # Allow requests from common development and local network origins
        allowed_origins = configure_cors()
        
        if origin in allowed_origins or origin is None:
            response.headers.add("Access-Control-Allow-Origin", origin or "*")
        else:
            response.headers.add("Access-Control-Allow-Origin", "*")
            
        response.headers.add('Access-Control-Allow-Headers', "Content-Type, Authorization, X-Requested-With")
        response.headers.add('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE, OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', "true")
        response.headers.add('Access-Control-Max-Age', "3600")
        return response

@app.after_request
def after_request(response):
    """Add CORS headers to all responses"""
    origin = request.headers.get('Origin')
    
    # Set CORS headers for all responses
    if origin:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Origin', '*')
        
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    
    return response

# Authentication routes
@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not all([username, email, password]):
            return jsonify({'error': 'Username, email, and password are required'}), 400
        
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
            
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Please provide a valid email address'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Username or email already exists'}), 400
        
        # Create user
        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, password_hash)
        )
        
        user_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        # Set session
        session.permanent = True
        session['user_id'] = user_id
        session['username'] = username
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {'id': user_id, 'username': username, 'email': email}
        }), 201
        
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint with 2FA support"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        username = data.get('username', '').strip()
        password = data.get('password', '')
        two_fa_token = data.get('two_fa_token', '').strip()
        
        if not all([username, password]):
            return jsonify({'error': 'Username and password are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, username, email, password_hash, two_fa_enabled, two_fa_secret, is_admin, is_administrator FROM users WHERE username = %s OR email = %s",
            (username, username)
        )
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user or not check_password_hash(user[3], password):
            return jsonify({'error': 'Invalid username/email or password'}), 401
        
        # Check if 2FA is enabled for this user
        if user[4]:  # two_fa_enabled
            if not two_fa_token:
                # 2FA is enabled but no token provided - request 2FA token
                return jsonify({
                    'requires_2fa': True,
                    'message': 'Two-factor authentication required'
                }), 200
            
            # Verify 2FA token
            if not user[5]:  # two_fa_secret
                return jsonify({'error': '2FA is enabled but secret is missing. Please contact administrator.'}), 500
            
            totp = pyotp.TOTP(user[5])
            if not totp.verify(two_fa_token):
                return jsonify({'error': 'Invalid 2FA token'}), 401
        
        # Set session
        session.permanent = True
        session['user_id'] = user[0]
        session['username'] = user[1]
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user[0], 
                'username': user[1], 
                'email': user[2],
                'is_admin': bool(user[6]),
                'is_administrator': bool(user[7]),
                'two_fa_enabled': bool(user[4])
            }
        }), 200
        
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    try:
        session.clear()
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500

@app.route('/api/user', methods=['GET'])
def get_current_user():
    """Get current logged in user"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, username, email, is_admin, is_administrator, two_fa_enabled FROM users WHERE id = %s",
            (session['user_id'],)
        )
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user:
            session.clear()  # Clear invalid session
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user[0], 
                'username': user[1], 
                'email': user[2],
                'is_admin': bool(user[3]),
                'is_administrator': bool(user[4]),
                'two_fa_enabled': bool(user[5])
            }
        }), 200
        
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Failed to get user: {str(e)}'}), 500

@app.route('/api/user/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    auth_check, auth_response, auth_status = require_auth()
    if not auth_check:
        return auth_response, auth_status
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not all([current_password, new_password]):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters long'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify current password
        cursor.execute(
            "SELECT password_hash FROM users WHERE id = %s",
            (session['user_id'],)
        )
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user[0], current_password):
            cursor.close()
            conn.close()
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Update password
        new_password_hash = generate_password_hash(new_password)
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (new_password_hash, session['user_id'])
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Password change failed: {str(e)}'}), 500

@app.route('/api/user/2fa/setup', methods=['POST'])
def setup_2fa():
    """Setup 2FA for user"""
    auth_check, auth_response, auth_status = require_auth()
    if not auth_check:
        return auth_response, auth_status
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate secret
        secret = pyotp.random_base32()
        
        # Get user info for QR code
        cursor.execute(
            "SELECT username, email FROM users WHERE id = %s",
            (session['user_id'],)
        )
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Generate QR code
        totp = pyotp.TOTP(secret)
        qr_url = totp.provisioning_uri(
            name=user[1],  # email
            issuer_name="LXCloud"
        )
        
        # Generate QR code image
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_image_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Store secret (but don't enable yet)
        cursor.execute(
            "UPDATE users SET two_fa_secret = %s WHERE id = %s",
            (secret, session['user_id'])
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'secret': secret,
            'qr_code': f"data:image/png;base64,{qr_image_b64}",
            'qr_url': qr_url
        }), 200
        
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'2FA setup failed: {str(e)}'}), 500

@app.route('/api/user/2fa/verify', methods=['POST'])
def verify_2fa():
    """Verify and enable 2FA for user"""
    auth_check, auth_response, auth_status = require_auth()
    if not auth_check:
        return auth_response, auth_status
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        token = data.get('token', '').strip()
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user's 2FA secret
        cursor.execute(
            "SELECT two_fa_secret FROM users WHERE id = %s",
            (session['user_id'],)
        )
        user = cursor.fetchone()
        
        if not user or not user[0]:
            cursor.close()
            conn.close()
            return jsonify({'error': '2FA not set up'}), 400
        
        # Verify token
        totp = pyotp.TOTP(user[0])
        if not totp.verify(token):
            cursor.close()
            conn.close()
            return jsonify({'error': 'Invalid token'}), 400
        
        # Enable 2FA
        cursor.execute(
            "UPDATE users SET two_fa_enabled = TRUE WHERE id = %s",
            (session['user_id'],)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': '2FA enabled successfully'}), 200
        
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'2FA verification failed: {str(e)}'}), 500

@app.route('/api/user/2fa/disable', methods=['POST'])
def disable_2fa():
    """Disable 2FA for user"""
    auth_check, auth_response, auth_status = require_auth()
    if not auth_check:
        return auth_response, auth_status
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        token = data.get('token', '').strip()
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user's 2FA secret
        cursor.execute(
            "SELECT two_fa_secret FROM users WHERE id = %s",
            (session['user_id'],)
        )
        user = cursor.fetchone()
        
        if not user or not user[0]:
            cursor.close()
            conn.close()
            return jsonify({'error': '2FA not enabled'}), 400
        
        # Verify token
        totp = pyotp.TOTP(user[0])
        if not totp.verify(token):
            cursor.close()
            conn.close()
            return jsonify({'error': 'Invalid token'}), 400
        
        # Disable 2FA
        cursor.execute(
            "UPDATE users SET two_fa_enabled = FALSE, two_fa_secret = NULL WHERE id = %s",
            (session['user_id'],)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': '2FA disabled successfully'}), 200
        
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'2FA disable failed: {str(e)}'}), 500
@app.route('/api/screens', methods=['GET'])
def get_screens():
    """Get all screens for current user or all screens for admin"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user is admin
    cursor.execute(
        "SELECT is_admin, is_administrator FROM users WHERE id = %s",
        (session['user_id'],)
    )
    user_roles = cursor.fetchone()
    is_admin_user = user_roles and (user_roles[0] or user_roles[1])
    
    if is_admin_user:
        # Admin can see all screens and unassigned controllers
        cursor.execute("""
            SELECT s.id, s.serial_number, s.custom_name, s.latitude, s.longitude, 
                   s.online_status, s.last_seen, s.created_at, u.username as assigned_user
            FROM screens s
            LEFT JOIN users u ON s.user_id = u.id
            ORDER BY s.created_at DESC
        """)
        
        screens = []
        for row in cursor.fetchall():
            screens.append({
                'id': row[0],
                'serial_number': row[1],
                'custom_name': row[2],
                'latitude': float(row[3]) if row[3] else None,
                'longitude': float(row[4]) if row[4] else None,
                'online_status': bool(row[5]),
                'last_seen': row[6].isoformat() if row[6] else None,
                'created_at': row[7].isoformat() if row[7] else None,
                'assigned_user': row[8],
                'assigned': bool(row[8])
            })
        
        # Also get unassigned controllers
        cursor.execute("""
            SELECT id, serial_number, latitude, longitude, online_status, last_seen, created_at
            FROM controllers
            WHERE assigned = FALSE
            ORDER BY created_at DESC
        """)
        
        unassigned_controllers = []
        for row in cursor.fetchall():
            unassigned_controllers.append({
                'id': row[0],
                'serial_number': row[1],
                'custom_name': None,
                'latitude': float(row[2]) if row[2] else None,
                'longitude': float(row[3]) if row[3] else None,
                'online_status': bool(row[4]),
                'last_seen': row[5].isoformat() if row[5] else None,
                'created_at': row[6].isoformat() if row[6] else None,
                'assigned_user': None,
                'assigned': False,
                'is_controller': True
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'screens': screens,
            'unassigned_controllers': unassigned_controllers
        }), 200
    else:
        # Regular user sees only their assigned screens
        cursor.execute("""
            SELECT s.id, s.serial_number, s.custom_name, s.latitude, s.longitude, 
                   s.online_status, s.last_seen, s.created_at
            FROM screens s
            WHERE s.user_id = %s
            ORDER BY s.created_at DESC
        """, (session['user_id'],))
        
        screens = []
        for row in cursor.fetchall():
            screens.append({
                'id': row[0],
                'serial_number': row[1],
                'custom_name': row[2],
                'latitude': float(row[3]) if row[3] else None,
                'longitude': float(row[4]) if row[4] else None,
                'online_status': bool(row[5]),
                'last_seen': row[6].isoformat() if row[6] else None,
                'created_at': row[7].isoformat() if row[7] else None,
                'assigned': True
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({'screens': screens}), 200

@app.route('/api/screens', methods=['POST'])
def add_screen():
    """Add a new screen by serial number (assign controller to user)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    serial_number = data.get('serial_number')
    custom_name = data.get('custom_name', '')
    
    if not serial_number:
        return jsonify({'error': 'Serial number is required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if screen already exists (already assigned)
    cursor.execute("SELECT id, user_id FROM screens WHERE serial_number = %s", (serial_number,))
    existing_screen = cursor.fetchone()
    if existing_screen:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Screen with this serial number is already assigned to a user'}), 400
    
    # Check if controller exists in controllers table
    cursor.execute("SELECT id, latitude, longitude, online_status FROM controllers WHERE serial_number = %s AND assigned = FALSE", (serial_number,))
    controller = cursor.fetchone()
    
    if controller:
        # Move controller to screens table and mark as assigned
        cursor.execute("""
            INSERT INTO screens (serial_number, user_id, custom_name, latitude, longitude, online_status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (serial_number, session['user_id'], custom_name, controller[1], controller[2], controller[3]))
        
        screen_id = cursor.lastrowid
        
        # Mark controller as assigned
        cursor.execute("UPDATE controllers SET assigned = TRUE WHERE id = %s", (controller[0],))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': 'Controller assigned successfully',
            'screen': {
                'id': screen_id,
                'serial_number': serial_number,
                'custom_name': custom_name
            }
        }), 201
    else:
        # Create new screen (old behavior for backwards compatibility)
        cursor.execute("""
            INSERT INTO screens (serial_number, user_id, custom_name)
            VALUES (%s, %s, %s)
        """, (serial_number, session['user_id'], custom_name))
        
        screen_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': 'Screen added successfully (controller will be available when it registers)',
            'screen': {
                'id': screen_id,
                'serial_number': serial_number,
                'custom_name': custom_name
            }
        }), 201

@app.route('/api/screens/<int:screen_id>', methods=['PUT'])
def update_screen(screen_id):
    """Update screen details"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    custom_name = data.get('custom_name', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if current user is admin
    cursor.execute(
        "SELECT is_admin, is_administrator FROM users WHERE id = %s",
        (session['user_id'],)
    )
    current_user = cursor.fetchone()
    if not current_user:
        cursor.close()
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    is_current_user_admin = current_user[0] or current_user[1]
    
    # Verify screen access - admin can update any screen, regular users only their own
    if is_current_user_admin:
        # Admin can update any screen
        cursor.execute(
            "SELECT id FROM screens WHERE id = %s",
            (screen_id,)
        )
    else:
        # Regular user can only update their own screens
        cursor.execute(
            "SELECT id FROM screens WHERE id = %s AND user_id = %s",
            (screen_id, session['user_id'])
        )
    
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Screen not found or access denied'}), 404
    
    # Update screen
    cursor.execute(
        "UPDATE screens SET custom_name = %s WHERE id = %s",
        (custom_name, screen_id)
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'Screen updated successfully'}), 200

@app.route('/api/screens/<int:screen_id>', methods=['DELETE'])
def delete_screen(screen_id):
    """Delete a screen"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if current user is admin
    cursor.execute(
        "SELECT is_admin, is_administrator FROM users WHERE id = %s",
        (session['user_id'],)
    )
    current_user = cursor.fetchone()
    if not current_user:
        cursor.close()
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    is_current_user_admin = current_user[0] or current_user[1]
    
    # Verify screen access - admin can delete any screen, regular users only their own
    if is_current_user_admin:
        # Admin can delete any screen
        cursor.execute(
            "SELECT id FROM screens WHERE id = %s",
            (screen_id,)
        )
    else:
        # Regular user can only delete their own screens
        cursor.execute(
            "SELECT id FROM screens WHERE id = %s AND user_id = %s",
            (screen_id, session['user_id'])
        )
    
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Screen not found or access denied'}), 404
    
    # Delete screen (cascade will delete related data)
    cursor.execute("DELETE FROM screens WHERE id = %s", (screen_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'Screen deleted successfully'}), 200

@app.route('/api/screens/<int:screen_id>/unbind', methods=['POST'])
def unbind_screen(screen_id):
    """Unbind a single screen from current user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First check if current user is admin
        cursor.execute(
            "SELECT is_admin, is_administrator FROM users WHERE id = %s",
            (session['user_id'],)
        )
        current_user = cursor.fetchone()
        if not current_user:
            cursor.close()
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        is_current_user_admin = current_user[0] or current_user[1]
        
        # Get screen data and verify access
        if is_current_user_admin:
            # Admin can unbind any screen
            cursor.execute("""
                SELECT s.serial_number, s.latitude, s.longitude, s.online_status, s.last_seen,
                       u.username
                FROM screens s
                JOIN users u ON s.user_id = u.id
                WHERE s.id = %s
            """, (screen_id,))
        else:
            # Regular user can only unbind their own screens
            cursor.execute("""
                SELECT s.serial_number, s.latitude, s.longitude, s.online_status, s.last_seen,
                       u.username
                FROM screens s
                JOIN users u ON s.user_id = u.id
                WHERE s.id = %s AND s.user_id = %s
            """, (screen_id, session['user_id']))
        
        screen_data = cursor.fetchone()
        if not screen_data:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Screen not found or access denied'}), 404
        
        serial_number, latitude, longitude, online_status, last_seen, owner_username = screen_data
        
        # Move screen back to controllers table as unassigned
        # Use ON DUPLICATE KEY UPDATE to handle case where controller already exists
        cursor.execute("""
            INSERT INTO controllers (serial_number, registration_key, latitude, longitude, online_status, last_seen, assigned)
            VALUES (%s, %s, %s, %s, %s, %s, FALSE)
            ON DUPLICATE KEY UPDATE
                registration_key = VALUES(registration_key),
                latitude = VALUES(latitude),
                longitude = VALUES(longitude),
                online_status = VALUES(online_status),
                last_seen = VALUES(last_seen),
                assigned = FALSE
        """, (
            serial_number,
            f'regenerated-{secrets.token_hex(8)}',
            latitude,
            longitude,
            online_status,
            last_seen
        ))
        
        # Remove from screens table
        cursor.execute("DELETE FROM screens WHERE id = %s", (screen_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': f'Screen {serial_number} has been unbound and is now an unassigned controller'
        }), 200
        
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Failed to unbind screen: {str(e)}'}), 500

@app.route('/api/screens/<int:screen_id>/data', methods=['GET'])
def get_screen_data(screen_id):
    """Get data for a specific screen"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if current user is admin
    cursor.execute(
        "SELECT is_admin, is_administrator FROM users WHERE id = %s",
        (session['user_id'],)
    )
    current_user = cursor.fetchone()
    if not current_user:
        cursor.close()
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    is_current_user_admin = current_user[0] or current_user[1]
    
    # Verify screen access - admin can access any screen, regular users only their own
    if is_current_user_admin:
        # Admin can access any screen
        cursor.execute(
            "SELECT id FROM screens WHERE id = %s",
            (screen_id,)
        )
    else:
        # Regular user can only access their own screens
        cursor.execute(
            "SELECT id FROM screens WHERE id = %s AND user_id = %s",
            (screen_id, session['user_id'])
        )
    
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Screen not found or access denied'}), 404
    
    # Get screen data for current year
    current_year = datetime.now().year
    cursor.execute("""
        SELECT information, timestamp
        FROM screen_data
        WHERE screen_id = %s AND year = %s
        ORDER BY timestamp DESC
        LIMIT 100
    """, (screen_id, current_year))
    
    data = []
    for row in cursor.fetchall():
        data.append({
            'information': row[0],
            'timestamp': row[1].isoformat() if row[1] else None
        })
    
    cursor.close()
    conn.close()
    
    return jsonify({'data': data}), 200

# API endpoint for Android devices to send data
@app.route('/api/device/update', methods=['POST'])
def device_update():
    """Endpoint for Android devices to send updates"""
    data = request.get_json()
    serial_number = data.get('serial_number')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    information = data.get('information', '')
    
    if not serial_number:
        return jsonify({'error': 'Serial number is required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # First check if this is an assigned screen
    cursor.execute("SELECT id, user_id FROM screens WHERE serial_number = %s", (serial_number,))
    screen = cursor.fetchone()
    
    if screen:
        # This is an assigned screen, store data
        screen_id = screen[0]
        current_year = datetime.now().year
        
        # Update screen location and status
        cursor.execute("""
            UPDATE screens
            SET latitude = %s, longitude = %s, online_status = TRUE, last_seen = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (latitude, longitude, screen_id))
        
        # Add data entry if information provided (only for assigned screens)
        if information:
            cursor.execute("""
                INSERT INTO screen_data (screen_id, information, year)
                VALUES (%s, %s, %s)
            """, (screen_id, information, current_year))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Emit real-time update to connected clients
        socketio.emit('screen_update', {
            'screen_id': screen_id,
            'serial_number': serial_number,
            'latitude': latitude,
            'longitude': longitude,
            'online_status': True,
            'information': information,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({'message': 'Update received successfully'}), 200
    else:
        # Check if this is an unassigned controller
        cursor.execute("SELECT id FROM controllers WHERE serial_number = %s", (serial_number,))
        controller = cursor.fetchone()
        
        if controller:
            # Update existing unassigned controller (don't store data)
            cursor.execute("""
                UPDATE controllers
                SET latitude = %s, longitude = %s, online_status = TRUE, last_seen = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (latitude, longitude, controller[0]))
        else:
            # Create new unassigned controller
            registration_key = generate_registration_key()
            cursor.execute("""
                INSERT INTO controllers (serial_number, registration_key, latitude, longitude, online_status)
                VALUES (%s, %s, %s, %s, TRUE)
            """, (serial_number, registration_key, latitude, longitude))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Controller update received (not assigned to user yet)'}), 200

# Admin management routes
@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    """Get all users (admin only)"""
    admin_check, admin_response, admin_status = require_admin()
    if not admin_check:
        return admin_response, admin_status
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, username, email, is_admin, is_administrator, two_fa_enabled, created_at
        FROM users
        ORDER BY created_at DESC
    """)
    
    users = []
    for row in cursor.fetchall():
        users.append({
            'id': row[0],
            'username': row[1],
            'email': row[2],
            'is_admin': bool(row[3]),
            'is_administrator': bool(row[4]),
            'two_fa_enabled': bool(row[5]),
            'created_at': row[6].isoformat() if row[6] else None
        })
    
    cursor.close()
    conn.close()
    
    return jsonify({'users': users}), 200

@app.route('/api/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
def admin_toggle_user_admin(user_id):
    """Toggle administrator flag for a user (admin only)"""
    admin_check, admin_response, admin_status = require_admin()
    if not admin_check:
        return admin_response, admin_status
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Don't allow modifying super admin
    cursor.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    if user[0]:  # is_admin
        cursor.close()
        conn.close()
        return jsonify({'error': 'Cannot modify super admin'}), 403
    
    # Toggle administrator flag
    cursor.execute("""
        UPDATE users 
        SET is_administrator = NOT is_administrator 
        WHERE id = %s
    """, (user_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'User administrator status toggled'}), 200

@app.route('/api/admin/create-admin', methods=['POST'])
def create_admin():
    """Create initial admin account (only works if no admin exists)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        admin_key = data.get('admin_key', '')
        
        # Validation
        if not all([username, email, password, admin_key]):
            return jsonify({'error': 'Username, email, password, and admin key are required'}), 400
        
        # Check admin key (simple security measure)
        if admin_key != 'lxcloud-admin-setup-2024':
            return jsonify({'error': 'Invalid admin key'}), 403
        
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
            
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Please provide a valid email address'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if any admin already exists
        cursor.execute("SELECT id FROM users WHERE is_admin = TRUE")
        existing_admin = cursor.fetchone()
        if existing_admin:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Admin account already exists'}), 400
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Username or email already exists'}), 400
        
        # Create admin user
        password_hash = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, is_admin)
            VALUES (%s, %s, %s, TRUE)
        """, (username, email, password_hash))
        
        user_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': 'Admin account created successfully',
            'user': {'id': user_id, 'username': username, 'email': email}
        }), 201
        
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Admin creation failed: {str(e)}'}), 500

@app.route('/api/admin/users/<int:user_id>/unbind-screens', methods=['POST'])
def admin_unbind_user_screens(user_id):
    """Unbind all screens from a user (admin only)"""
    admin_check, admin_response, admin_status = require_admin()
    if not admin_check:
        return admin_response, admin_status
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            cursor.close()
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Get count of screens to unbind
        cursor.execute("SELECT COUNT(*) FROM screens WHERE user_id = %s", (user_id,))
        screen_count = cursor.fetchone()[0]
        
        if screen_count == 0:
            cursor.close()
            conn.close()
            return jsonify({'message': 'User has no screens to unbind'}), 200
        
        # Move screens back to controllers table and mark as unassigned
        cursor.execute("""
            INSERT INTO controllers (serial_number, registration_key, latitude, longitude, online_status, last_seen, assigned)
            SELECT s.serial_number, 
                   CONCAT('regenerated-', SUBSTRING(MD5(RAND()), 1, 16)),
                   s.latitude, s.longitude, s.online_status, s.last_seen, FALSE
            FROM screens s 
            WHERE s.user_id = %s
        """, (user_id,))
        
        # Delete screens from screens table
        cursor.execute("DELETE FROM screens WHERE user_id = %s", (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': f'Successfully unbound {screen_count} screens from user {user[0]}'
        }), 200
        
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Failed to unbind screens: {str(e)}'}), 500

@app.route('/api/admin/users/<int:user_id>/reset-password', methods=['POST'])
def admin_reset_user_password(user_id):
    """Reset user password (admin only)"""
    admin_check, admin_response, admin_status = require_admin()
    if not admin_check:
        return admin_response, admin_status
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        new_password = data.get('new_password', '')
        
        if not new_password:
            return jsonify({'error': 'New password is required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters long'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists and is not super admin
        cursor.execute("SELECT username, is_admin FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            cursor.close()
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        if user[1]:  # is_admin
            cursor.close()
            conn.close()
            return jsonify({'error': 'Cannot reset super admin password'}), 403
        
        # Update password
        new_password_hash = generate_password_hash(new_password)
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (new_password_hash, user_id)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': f'Password reset successfully for user {user[0]}'
        }), 200
        
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Password reset failed: {str(e)}'}), 500

@app.route('/api/admin/users/<int:user_id>/disable-2fa', methods=['POST'])
def admin_disable_user_2fa(user_id):
    """Disable 2FA for a user (super admin only)"""
    # Check if current user is super admin (not just admin/administrator)
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if current user is super admin
        cursor.execute("SELECT is_admin FROM users WHERE id = %s", (session['user_id'],))
        current_user = cursor.fetchone()
        if not current_user or not current_user[0]:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Super admin access required'}), 403
        
        # Check if target user exists
        cursor.execute("SELECT username, two_fa_enabled FROM users WHERE id = %s", (user_id,))
        target_user = cursor.fetchone()
        if not target_user:
            cursor.close()
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        username, two_fa_enabled = target_user
        
        if not two_fa_enabled:
            cursor.close()
            conn.close()
            return jsonify({'message': f'2FA is already disabled for user {username}'}), 200
        
        # Disable 2FA for the user
        cursor.execute(
            "UPDATE users SET two_fa_enabled = FALSE, two_fa_secret = NULL WHERE id = %s",
            (user_id,)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': f'2FA has been disabled for user {username}'
        }), 200
        
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Failed to disable 2FA: {str(e)}'}), 500

@app.route('/api/admin/users/<int:user_id>/delete', methods=['DELETE'])
def admin_delete_user(user_id):
    """Delete user and their data (admin only)"""
    admin_check, admin_response, admin_status = require_admin()
    if not admin_check:
        return admin_response, admin_status
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists and is not super admin
        cursor.execute("SELECT username, is_admin FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            cursor.close()
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        if user[1]:  # is_admin
            cursor.close()
            conn.close()
            return jsonify({'error': 'Cannot delete super admin'}), 403
        
        # Get count of user's screens for info
        cursor.execute("SELECT COUNT(*) FROM screens WHERE user_id = %s", (user_id,))
        screen_count = cursor.fetchone()[0]
        
        # Move user's screens back to controllers (unassigned)
        if screen_count > 0:
            cursor.execute("""
                INSERT INTO controllers (serial_number, registration_key, latitude, longitude, online_status, last_seen, assigned)
                SELECT s.serial_number, 
                       CONCAT('regenerated-', SUBSTRING(MD5(RAND()), 1, 16)),
                       s.latitude, s.longitude, s.online_status, s.last_seen, FALSE
                FROM screens s 
                WHERE s.user_id = %s
            """, (user_id,))
        
        # Delete user (cascading foreign keys will handle screens and screen_data)
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': f'User {user[0]} deleted successfully. {screen_count} screens moved to unassigned controllers.'
        }), 200
        
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'User deletion failed: {str(e)}'}), 500

@app.route('/api/admin/settings', methods=['GET'])
def get_admin_settings():
    """Get admin settings (super admin only)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Check if user is super admin
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    
    if not user or not user[0]:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Super admin access required'}), 403
    
    try:
        # Get settings from database
        cursor.execute("SELECT setting_key, setting_value FROM admin_settings")
        settings_rows = cursor.fetchall()
        
        # Convert to dictionary
        settings = {}
        for key, value in settings_rows:
            settings[key] = value
        
        # Return default values if no settings exist
        default_settings = {
            'logoUrl': None,
            'logoText': 'LXCloud',
            'siteName': 'LXCloud - LED Screen Management Platform',
            'faviconUrl': None,
            'mapMarkerOnline': None,
            'mapMarkerOffline': None
        }
        
        # Merge defaults with saved settings
        final_settings = {**default_settings, **settings}
        
        cursor.close()
        conn.close()
        
        return jsonify({'settings': final_settings}), 200
        
    except pymysql.Error as e:
        cursor.close()
        conn.close()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/admin/settings', methods=['POST'])
def update_admin_settings():
    """Update admin settings (super admin only)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Check if user is super admin
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    
    if not user or not user[0]:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Super admin access required'}), 403
    
    data = request.get_json()
    if not data:
        cursor.close()
        conn.close()
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Update or insert each setting
        allowed_settings = ['logoUrl', 'logoText', 'siteName', 'faviconUrl', 'mapMarkerOnline', 'mapMarkerOffline']
        
        for key, value in data.items():
            if key in allowed_settings:
                cursor.execute("""
                    INSERT INTO admin_settings (setting_key, setting_value, updated_at) 
                    VALUES (%s, %s, NOW())
                    ON DUPLICATE KEY UPDATE 
                    setting_value = VALUES(setting_value), 
                    updated_at = NOW()
                """, (key, value))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Settings updated successfully'}), 200
        
    except pymysql.Error as e:
        cursor.close()
        conn.close()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/admin/ui-settings', methods=['GET'])
def get_ui_settings():
    """Get UI customization settings (admin only)"""
    is_authorized, error_response, status_code = require_admin()
    if not is_authorized:
        return error_response, status_code
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get UI settings from database
        cursor.execute("SELECT setting_key, setting_value FROM ui_settings")
        settings_rows = cursor.fetchall()
        
        # Convert to dictionary
        settings = {}
        for key, value in settings_rows:
            settings[key] = value
        
        # Return default values if no settings exist
        default_settings = {
            # Original settings
            'app_name': 'LXCloud',
            'primary_color': '#667eea',
            'secondary_color': '#f093fb',
            'header_color': '#667eea',
            'button_color': '#667eea',
            'button_hover_color': '#5a6fd8',
            'logo_url': '',
            'favicon_url': '',
            'background_image_url': '',
            'custom_button_images': '{}',
            
            # Screen management button icons
            'screen_view_data_icon': '',
            'screen_edit_icon': '',
            'screen_unbind_icon': '',
            
            # Footer customization
            'footer_enabled': 'true',
            'footer_text': 'Powered by LXCloud',
            'footer_color': '#f8f9fa',
            'footer_text_color': '#6c757d',
            'footer_links': '{}',
            
            # Typography settings
            'font_family': 'system-ui, -apple-system, sans-serif',
            'font_size_base': '16px',
            'font_size_heading': '24px',
            'line_height': '1.5',
            
            # Navigation customization
            'nav_style': 'default',
            'nav_position': 'top',
            'nav_color': '#667eea',
            'nav_hover_color': '#5a6fd8',
            'header_text_color': '#ffffff',
            
            # Advanced button customization
            'button_style': 'default',
            'button_size': 'medium',
            'button_shadow': 'true',
            'button_animation': 'true',
            
            # Page-specific settings
            'dashboard_layout': 'grid',
            'dashboard_theme': 'default',
            'login_background_url': '',
            'login_style': 'default',
            
            # Custom text overrides
            'custom_text_labels': '{}',
            'page_titles': '{}',
            
            # Advanced customization
            'custom_css': '',
            'theme_mode': 'light',
            'border_radius': '8px',
            'spacing_unit': '16px',
            
            # Per-page custom CSS
            'dashboard_custom_css': '',
            'manage_screens_custom_css': '',
            
            # Accessibility settings
            'high_contrast': 'false',
            'large_text': 'false',
            'reduced_motion': 'false',
            
            # Advanced header settings
            'header_height': '60px',
            'header_shadow': 'true',
            'header_sticky': 'true',
            
            # Header button customization
            'header_button_alignment': 'default',
            'header_button_vertical_alignment': 'center',
            'header_button_spacing': '15px',
            'header_button_individual_positions': '{}',
            'header_button_individual_colors': '{}',
            'header_custom_css': '',
            
            # Card and component styling
            'card_shadow': 'true',
            'card_border': 'true',
            'card_hover_effect': 'true'
        }
        
        # Merge defaults with saved settings
        final_settings = {**default_settings, **settings}
        
        cursor.close()
        conn.close()
        
        return jsonify({'settings': final_settings}), 200
        
    except pymysql.Error as e:
        cursor.close()
        conn.close()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/admin/ui-settings', methods=['POST'])
def update_ui_settings():
    """Update UI customization settings (admin only)"""
    is_authorized, error_response, status_code = require_admin()
    if not is_authorized:
        return error_response, status_code
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Update or insert each setting
        allowed_settings = [
            # Original settings
            'app_name', 'primary_color', 'secondary_color', 'header_color', 'button_color', 
            'button_hover_color', 'logo_url', 'favicon_url', 'background_image_url', 'custom_button_images',
            
            # Screen management button icons
            'screen_view_data_icon', 'screen_edit_icon', 'screen_unbind_icon',
            
            # Footer customization
            'footer_enabled', 'footer_text', 'footer_color', 'footer_text_color', 'footer_links',
            
            # Typography settings
            'font_family', 'font_size_base', 'font_size_heading', 'line_height',
            
            # Navigation customization
            'nav_style', 'nav_position', 'nav_color', 'nav_hover_color', 'header_text_color',
            
            # Advanced button customization
            'button_style', 'button_size', 'button_shadow', 'button_animation',
            
            # Page-specific settings
            'dashboard_layout', 'dashboard_theme', 'login_background_url', 'login_style',
            
            # Custom text overrides
            'custom_text_labels', 'page_titles',
            
            # Advanced customization
            'custom_css', 'theme_mode', 'border_radius', 'spacing_unit',
            
            # Per-page custom CSS
            'dashboard_custom_css', 'manage_screens_custom_css',
            
            # Accessibility settings
            'high_contrast', 'large_text', 'reduced_motion',
            
            # Advanced header settings
            'header_height', 'header_shadow', 'header_sticky',
            
            # Header button customization
            'header_button_alignment', 'header_button_vertical_alignment', 'header_button_spacing',
            'header_button_individual_positions', 'header_button_individual_colors', 'header_custom_css',
            
            # Card and component styling
            'card_shadow', 'card_border', 'card_hover_effect'
        ]
        
        for key, value in data.items():
            if key in allowed_settings:
                cursor.execute("""
                    INSERT INTO ui_settings (setting_key, setting_value, updated_at) 
                    VALUES (%s, %s, NOW())
                    ON DUPLICATE KEY UPDATE 
                    setting_value = VALUES(setting_value), 
                    updated_at = NOW()
                """, (key, value))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'UI settings updated successfully'}), 200
        
    except pymysql.Error as e:
        cursor.close()
        conn.close()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/admin/upload-ui-asset', methods=['POST'])
def upload_ui_asset():
    """Upload UI asset (logo, favicon, background) (admin only)"""
    is_authorized, error_response, status_code = require_admin()
    if not is_authorized:
        return error_response, status_code
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    asset_type = request.form.get('type', 'logo')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
    allowed_mimes = {'image/png', 'image/jpeg', 'image/gif', 'image/svg+xml'}
    
    if file.content_type not in allowed_mimes:
        return jsonify({'error': 'Invalid file type. Only PNG, JPEG, GIF, and SVG are allowed.'}), 400
    
    # Create uploads directory if it doesn't exist
    upload_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'ui')
    os.makedirs(upload_dir, exist_ok=True)
    
    try:
        # Generate unique filename
        import uuid
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{asset_type}_{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Generate URL for the uploaded file
        file_url = f"/api/static/uploads/ui/{unique_filename}"
        
        return jsonify({
            'message': f'{asset_type.capitalize()} uploaded successfully',
            'url': file_url,
            'filename': unique_filename
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/static/uploads/ui/<filename>')
def serve_ui_upload(filename):
    """Serve uploaded UI assets"""
    upload_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'ui')
    return send_from_directory(upload_dir, filename)

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    print("=" * 60)
    print("LXCloud Backend Starting")
    print("=" * 60)
    
    # Try to initialize database, but continue even if it fails
    try:
        init_database()
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        print("Application will start but some features may not work")
        print("See above for instructions to fix database issues")
    
    print("")
    print("Starting Flask application on:")
    print("  - http://localhost:5000 (API)")
    print("  - All interfaces (0.0.0.0:5000)")
    print("")
    print("Make sure the frontend is built and served separately")
    print("or use nginx configuration as described in README.md")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)