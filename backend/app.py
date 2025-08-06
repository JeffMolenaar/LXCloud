from flask import Flask, request, jsonify, session, make_response, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import os
from datetime import datetime, timedelta
import json

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

def init_database():
    """Initialize database with required tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        
        conn.commit()
        cursor.close()
        conn.close()
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
        'version': '1.0.0'
    }), 200

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
    """User login endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not all([username, password]):
            return jsonify({'error': 'Username and password are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, username, email, password_hash FROM users WHERE username = %s OR email = %s",
            (username, username)
        )
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user or not check_password_hash(user[3], password):
            return jsonify({'error': 'Invalid username/email or password'}), 401
        
        # Set session
        session.permanent = True
        session['user_id'] = user[0]
        session['username'] = user[1]
        
        return jsonify({
            'message': 'Login successful',
            'user': {'id': user[0], 'username': user[1], 'email': user[2]}
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
            "SELECT id, username, email FROM users WHERE id = %s",
            (session['user_id'],)
        )
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user:
            session.clear()  # Clear invalid session
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {'id': user[0], 'username': user[1], 'email': user[2]}
        }), 200
        
    except pymysql.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Failed to get user: {str(e)}'}), 500

# Screen management routes
@app.route('/api/screens', methods=['GET'])
def get_screens():
    """Get all screens for current user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
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
            'created_at': row[7].isoformat() if row[7] else None
        })
    
    cursor.close()
    conn.close()
    
    return jsonify({'screens': screens}), 200

@app.route('/api/screens', methods=['POST'])
def add_screen():
    """Add a new screen"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    serial_number = data.get('serial_number')
    custom_name = data.get('custom_name', '')
    
    if not serial_number:
        return jsonify({'error': 'Serial number is required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if screen already exists
    cursor.execute("SELECT id FROM screens WHERE serial_number = %s", (serial_number,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Screen with this serial number already exists'}), 400
    
    # Add screen
    cursor.execute("""
        INSERT INTO screens (serial_number, user_id, custom_name)
        VALUES (%s, %s, %s)
    """, (serial_number, session['user_id'], custom_name))
    
    screen_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({
        'message': 'Screen added successfully',
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
    
    # Verify screen belongs to user
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
    
    # Verify screen belongs to user
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

@app.route('/api/screens/<int:screen_id>/data', methods=['GET'])
def get_screen_data(screen_id):
    """Get data for a specific screen"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify screen belongs to user
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
    
    # Find screen by serial number
    cursor.execute("SELECT id FROM screens WHERE serial_number = %s", (serial_number,))
    screen = cursor.fetchone()
    
    if not screen:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Screen not found'}), 404
    
    screen_id = screen[0]
    current_year = datetime.now().year
    
    # Update screen location and status
    cursor.execute("""
        UPDATE screens
        SET latitude = %s, longitude = %s, online_status = TRUE, last_seen = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (latitude, longitude, screen_id))
    
    # Add data entry if information provided
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