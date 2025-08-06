from flask import Flask, request, jsonify, session, make_response, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
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
                f'http://{local_ip}:3000',
                f'http://{local_ip}:8080'
            ])
    except:
        pass
    
    return allowed_origins

CORS(app, 
     supports_credentials=True,
     origins="*",  # Allow all origins for local network testing
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   async_mode='threading')

# In-memory storage for testing (no database required)
users_db = {}
screens_db = {}
screen_data_db = {}
user_counter = 1
screen_counter = 1

# Frontend serving
frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')

@app.route('/')
def serve_frontend():
    """Serve the main React application"""
    return send_from_directory(frontend_path, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    """Serve static files or fall back to index.html for React Router"""
    try:
        return send_from_directory(frontend_path, path)
    except:
        # For React Router, serve index.html for any route that doesn't match a file
        return send_from_directory(frontend_path, 'index.html')

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'database': 'in-memory (standalone mode)',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0-standalone'
    }), 200

# Handle preflight requests for CORS
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type, Authorization, X-Requested-With")
        response.headers.add('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE, OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', "true")
        response.headers.add('Access-Control-Max-Age', "3600")
        return response

@app.after_request
def after_request(response):
    """Add CORS headers to all responses"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    return response

# Authentication routes
@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint"""
    global user_counter
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
        
        # Check if user exists
        for user in users_db.values():
            if user['username'] == username or user['email'] == email:
                return jsonify({'error': 'Username or email already exists'}), 400
        
        # Create user
        password_hash = generate_password_hash(password)
        user_id = user_counter
        user_counter += 1
        
        users_db[user_id] = {
            'id': user_id,
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'created_at': datetime.now()
        }
        
        # Set session
        session.permanent = True
        session['user_id'] = user_id
        session['username'] = username
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {'id': user_id, 'username': username, 'email': email}
        }), 201
        
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
        
        # Find user
        user = None
        for u in users_db.values():
            if u['username'] == username or u['email'] == username:
                user = u
                break
        
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid username/email or password'}), 401
        
        # Set session
        session.permanent = True
        session['user_id'] = user['id']
        session['username'] = user['username']
        
        return jsonify({
            'message': 'Login successful',
            'user': {'id': user['id'], 'username': user['username'], 'email': user['email']}
        }), 200
        
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
        
        user_id = session['user_id']
        user = users_db.get(user_id)
        
        if not user:
            session.clear()  # Clear invalid session
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {'id': user['id'], 'username': user['username'], 'email': user['email']}
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get user: {str(e)}'}), 500

# Screen management routes
@app.route('/api/screens', methods=['GET'])
def get_screens():
    """Get all screens for current user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    user_screens = []
    
    for screen in screens_db.values():
        if screen['user_id'] == user_id:
            user_screens.append({
                'id': screen['id'],
                'serial_number': screen['serial_number'],
                'custom_name': screen['custom_name'],
                'latitude': screen['latitude'],
                'longitude': screen['longitude'],
                'online_status': screen['online_status'],
                'last_seen': screen['last_seen'].isoformat() if screen['last_seen'] else None,
                'created_at': screen['created_at'].isoformat() if screen['created_at'] else None
            })
    
    return jsonify({'screens': user_screens}), 200

@app.route('/api/screens', methods=['POST'])
def add_screen():
    """Add a new screen"""
    global screen_counter
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    serial_number = data.get('serial_number')
    custom_name = data.get('custom_name', '')
    
    if not serial_number:
        return jsonify({'error': 'Serial number is required'}), 400
    
    # Check if screen already exists
    for screen in screens_db.values():
        if screen['serial_number'] == serial_number:
            return jsonify({'error': 'Screen with this serial number already exists'}), 400
    
    # Add screen
    screen_id = screen_counter
    screen_counter += 1
    
    screens_db[screen_id] = {
        'id': screen_id,
        'serial_number': serial_number,
        'user_id': session['user_id'],
        'custom_name': custom_name,
        'latitude': None,
        'longitude': None,
        'online_status': False,
        'last_seen': None,
        'created_at': datetime.now()
    }
    
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
    
    screen = screens_db.get(screen_id)
    if not screen or screen['user_id'] != session['user_id']:
        return jsonify({'error': 'Screen not found or access denied'}), 404
    
    # Update screen
    screen['custom_name'] = custom_name
    
    return jsonify({'message': 'Screen updated successfully'}), 200

@app.route('/api/screens/<int:screen_id>', methods=['DELETE'])
def delete_screen(screen_id):
    """Delete a screen"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    screen = screens_db.get(screen_id)
    if not screen or screen['user_id'] != session['user_id']:
        return jsonify({'error': 'Screen not found or access denied'}), 404
    
    # Delete screen and related data
    del screens_db[screen_id]
    screen_data_db.pop(screen_id, None)
    
    return jsonify({'message': 'Screen deleted successfully'}), 200

@app.route('/api/screens/<int:screen_id>/data', methods=['GET'])
def get_screen_data(screen_id):
    """Get data for a specific screen"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    screen = screens_db.get(screen_id)
    if not screen or screen['user_id'] != session['user_id']:
        return jsonify({'error': 'Screen not found or access denied'}), 404
    
    # Get screen data
    data = screen_data_db.get(screen_id, [])
    
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
    
    # Find screen by serial number
    screen = None
    for s in screens_db.values():
        if s['serial_number'] == serial_number:
            screen = s
            break
    
    if not screen:
        return jsonify({'error': 'Screen not found'}), 404
    
    screen_id = screen['id']
    
    # Update screen location and status
    screen['latitude'] = latitude
    screen['longitude'] = longitude
    screen['online_status'] = True
    screen['last_seen'] = datetime.now()
    
    # Add data entry if information provided
    if information:
        if screen_id not in screen_data_db:
            screen_data_db[screen_id] = []
        
        screen_data_db[screen_id].append({
            'information': information,
            'timestamp': datetime.now().isoformat()
        })
    
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
    print("LXCloud Standalone Mode - No Database Required")
    print("=" * 60)
    print(f"Frontend path: {frontend_path}")
    print(f"Frontend exists: {os.path.exists(frontend_path)}")
    print(f"Index.html exists: {os.path.exists(os.path.join(frontend_path, 'index.html'))}")
    print("")
    print("Access the application at:")
    print("  - http://localhost:8080")
    print("  - http://127.0.0.1:8080")
    
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        if local_ip and local_ip != '127.0.0.1':
            print(f"  - http://{local_ip}:8080 (local network)")
    except:
        pass
    
    print("")
    print("API Health Check: /api/health")
    print("Note: This is a standalone version for testing without database")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=8080, debug=True, allow_unsafe_werkzeug=True)