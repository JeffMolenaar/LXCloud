from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lxcloud-secret-key-change-in-production'
CORS(app, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*")

# Database configuration with environment variable support
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'lxcloud'),
    'password': os.environ.get('DB_PASS', 'lxcloud123'),
    'database': os.environ.get('DB_NAME', 'lxcloud'),
    'charset': 'utf8mb4'
}

def get_db_connection():
    """Get database connection"""
    return pymysql.connect(**DB_CONFIG)

def init_database():
    """Initialize database with required tables"""
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

# Authentication routes
@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'User already exists'}), 400
    
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
    
    session['user_id'] = user_id
    session['username'] = username
    
    return jsonify({
        'message': 'User registered successfully',
        'user': {'id': user_id, 'username': username, 'email': email}
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        return jsonify({'error': 'Missing username or password'}), 400
    
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
        return jsonify({'error': 'Invalid credentials'}), 401
    
    session['user_id'] = user[0]
    session['username'] = user[1]
    
    return jsonify({
        'message': 'Login successful',
        'user': {'id': user[0], 'username': user[1], 'email': user[2]}
    }), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/user', methods=['GET'])
def get_current_user():
    """Get current logged in user"""
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
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': {'id': user[0], 'username': user[1], 'email': user[2]}
    }), 200

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
    init_database()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)