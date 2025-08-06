#!/usr/bin/env python3

# Simple test backend for demonstrating Cloud UI Customization
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.security import check_password_hash
import sqlite3
import os
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'

# Configure CORS for local development
CORS(app, 
     supports_credentials=True,
     origins=["http://localhost:3000", "http://127.0.0.1:3000"],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

def get_db_connection():
    conn = sqlite3.connect('test_lxcloud.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Test backend running'}), 200

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ? OR email = ?',
        (username, username)
    ).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'is_admin': bool(user['is_admin']),
                'is_administrator': bool(user['is_administrator']),
                'two_fa_enabled': bool(user['two_fa_enabled'])
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/user', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'is_admin': bool(user['is_admin']),
            'is_administrator': bool(user['is_administrator']),
            'two_fa_enabled': bool(user['two_fa_enabled'])
        }
    }), 200

@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db_connection()
    current_user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not current_user or (not current_user['is_admin'] and not current_user['is_administrator']):
        conn.close()
        return jsonify({'error': 'Admin access required'}), 403
    
    users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    
    users_list = []
    for user in users:
        users_list.append({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'is_admin': bool(user['is_admin']),
            'is_administrator': bool(user['is_administrator']),
            'two_fa_enabled': bool(user['two_fa_enabled']),
            'created_at': user['created_at']
        })
    
    return jsonify({'users': users_list}), 200

@app.route('/api/screens', methods=['GET'])
def get_screens():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db_connection()
    screens = conn.execute('SELECT * FROM screens').fetchall()
    conn.close()
    
    screens_list = []
    for screen in screens:
        screens_list.append({
            'id': screen['id'],
            'serial_number': screen['serial_number'],
            'custom_name': screen['custom_name'],
            'assigned_user': None,  # Simplified for demo
            'latitude': screen['latitude'],
            'longitude': screen['longitude'],
            'online_status': bool(screen['online_status']),
            'last_seen': screen['last_seen']
        })
    
    return jsonify({'screens': screens_list, 'unassigned_controllers': []}), 200

@app.route('/api/admin/ui-settings', methods=['GET'])
def get_ui_settings():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db_connection()
    current_user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not current_user or (not current_user['is_admin'] and not current_user['is_administrator']):
        conn.close()
        return jsonify({'error': 'Admin access required'}), 403
    
    settings_rows = conn.execute('SELECT setting_key, setting_value FROM ui_settings').fetchall()
    conn.close()
    
    settings = {}
    for row in settings_rows:
        settings[row['setting_key']] = row['setting_value']
    
    # Default values
    default_settings = {
        'app_name': 'LXCloud',
        'primary_color': '#667eea',
        'secondary_color': '#f093fb',
        'logo_url': '',
        'favicon_url': '',
        'background_image_url': ''
    }
    
    final_settings = {**default_settings, **settings}
    return jsonify({'settings': final_settings}), 200

@app.route('/api/admin/ui-settings', methods=['POST'])
def update_ui_settings():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db_connection()
    current_user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not current_user or (not current_user['is_admin'] and not current_user['is_administrator']):
        conn.close()
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    if not data:
        conn.close()
        return jsonify({'error': 'No data provided'}), 400
    
    allowed_settings = ['app_name', 'primary_color', 'secondary_color', 'logo_url', 'favicon_url', 'background_image_url']
    
    for key, value in data.items():
        if key in allowed_settings:
            conn.execute('''
                INSERT OR REPLACE INTO ui_settings (setting_key, setting_value, updated_at) 
                VALUES (?, ?, datetime('now'))
            ''', (key, value))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'UI settings updated successfully'}), 200

@app.route('/api/admin/upload-ui-asset', methods=['POST'])
def upload_ui_asset():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db_connection()
    current_user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not current_user or (not current_user['is_admin'] and not current_user['is_administrator']):
        conn.close()
        return jsonify({'error': 'Admin access required'}), 403
    
    if 'file' not in request.files:
        conn.close()
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    asset_type = request.form.get('type', 'logo')
    
    if file.filename == '':
        conn.close()
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    allowed_mimes = {'image/png', 'image/jpeg', 'image/gif', 'image/svg+xml'}
    
    if file.content_type not in allowed_mimes:
        conn.close()
        return jsonify({'error': 'Invalid file type. Only PNG, JPEG, GIF, and SVG are allowed.'}), 400
    
    # Create uploads directory
    upload_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'ui')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{asset_type}_{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    file.save(file_path)
    
    # Generate URL for the uploaded file
    file_url = f"/api/static/uploads/ui/{unique_filename}"
    
    conn.close()
    
    return jsonify({
        'message': f'{asset_type.capitalize()} uploaded successfully',
        'url': file_url,
        'filename': unique_filename
    }), 200

@app.route('/api/static/uploads/ui/<filename>')
def serve_ui_upload(filename):
    upload_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'ui')
    return send_from_directory(upload_dir, filename)

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

if __name__ == '__main__':
    print("=" * 50)
    print("LXCloud Test Backend")
    print("=" * 50)
    print("Running on http://localhost:5000")
    print("Test admin user: admin / admin123")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)