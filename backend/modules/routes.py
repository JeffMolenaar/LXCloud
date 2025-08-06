"""
API routes for LXCloud backend
"""
from flask import Blueprint, request, jsonify, session
from modules.auth import (
    require_auth, require_admin, require_super_admin,
    authenticate_user, create_user, get_current_user,
    generate_2fa_secret, generate_2fa_qr_code, verify_2fa_token,
    enable_2fa_for_user, disable_2fa_for_user, login_user, logout_user,
    change_user_password, is_first_user, verify_controller_auth,
    generate_registration_key, verify_password
)
from modules.database import execute_query
from modules.config import Config
import json
from datetime import datetime

# Create blueprints for different route groups
auth_bp = Blueprint('auth', __name__, url_prefix='/api')
screens_bp = Blueprint('screens', __name__, url_prefix='/api')
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
system_bp = Blueprint('system', __name__, url_prefix='/api')

# Authentication Routes
@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    try:
        existing_user = execute_query(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (username, email),
            fetch_one=True
        )
        if existing_user:
            return jsonify({'error': 'Username or email already exists'}), 400
    except:
        pass
    
    # Create user (first user becomes admin)
    is_admin = is_first_user()
    user = create_user(username, email, password, is_admin=is_admin, is_administrator=is_admin)
    
    if user:
        login_user(user)
        return jsonify({
            'user': user,
            'message': 'Registration successful'
        })
    else:
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    username_or_email = data.get('username')
    password = data.get('password')
    two_fa_token = data.get('two_fa_token')
    
    if not username_or_email or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    user = authenticate_user(username_or_email, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check 2FA if enabled
    if user['two_fa_enabled']:
        if not two_fa_token:
            return jsonify({
                'requires_2fa': True,
                'message': 'Two-factor authentication token required'
            }), 200
        
        if not verify_2fa_token(user['two_fa_secret'], two_fa_token):
            return jsonify({'error': 'Invalid 2FA token'}), 401
    
    # Login successful
    login_user(user)
    
    # Return user info without sensitive data
    user_info = {
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'is_admin': user['is_admin'],
        'is_administrator': user['is_administrator'],
        'two_fa_enabled': user['two_fa_enabled']
    }
    
    return jsonify({
        'user': user_info,
        'message': 'Login successful'
    })

@auth_bp.route('/logout', methods=['POST'])
@require_auth()
def logout():
    """Logout user"""
    logout_user()
    return jsonify({'message': 'Logout successful'})

@auth_bp.route('/user', methods=['GET'])
@require_auth()
def get_user():
    """Get current user info"""
    user = get_current_user()
    if user:
        return jsonify({'user': user})
    return jsonify({'error': 'User not found'}), 404

@auth_bp.route('/user/change-password', methods=['POST'])
@require_auth()
def change_password():
    """Change user password"""
    data = request.get_json()
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current and new password required'}), 400
    
    # Verify current password
    user = execute_query(
        "SELECT password_hash FROM users WHERE id = %s",
        (session['user_id'],),
        fetch_one=True
    )
    
    if not user or not verify_password(user['password_hash'], current_password):
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    if change_user_password(session['user_id'], new_password):
        return jsonify({'message': 'Password changed successfully'})
    else:
        return jsonify({'error': 'Failed to change password'}), 500

@auth_bp.route('/user/2fa/setup', methods=['POST'])
@require_auth()
def setup_2fa():
    """Setup 2FA for user"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    secret = generate_2fa_secret()
    qr_code = generate_2fa_qr_code(user['username'], secret)
    
    if qr_code:
        # Store temporary secret in session for verification
        session['temp_2fa_secret'] = secret
        
        return jsonify({
            'secret': secret,
            'qr_code': qr_code,
            'message': 'Scan QR code with your authenticator app'
        })
    else:
        return jsonify({'error': 'Failed to generate QR code'}), 500

@auth_bp.route('/user/2fa/verify', methods=['POST'])
@require_auth()
def verify_2fa():
    """Verify and enable 2FA"""
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({'error': 'Token required'}), 400
    
    secret = session.get('temp_2fa_secret')
    if not secret:
        return jsonify({'error': 'No 2FA setup in progress'}), 400
    
    if verify_2fa_token(secret, token):
        if enable_2fa_for_user(session['user_id'], secret):
            session.pop('temp_2fa_secret', None)
            return jsonify({'message': '2FA enabled successfully'})
        else:
            return jsonify({'error': 'Failed to enable 2FA'}), 500
    else:
        return jsonify({'error': 'Invalid token'}), 400

@auth_bp.route('/user/2fa/disable', methods=['POST'])
@require_auth()
def disable_2fa():
    """Disable 2FA"""
    data = request.get_json()
    password = data.get('password')
    
    if not password:
        return jsonify({'error': 'Password required'}), 400
    
    # Verify password before disabling 2FA
    user = execute_query(
        "SELECT password_hash FROM users WHERE id = %s",
        (session['user_id'],),
        fetch_one=True
    )
    
    if not user or not verify_password(user['password_hash'], password):
        return jsonify({'error': 'Invalid password'}), 400
    
    if disable_2fa_for_user(session['user_id']):
        return jsonify({'message': '2FA disabled successfully'})
    else:
        return jsonify({'error': 'Failed to disable 2FA'}), 500

# Screen Management Routes
@screens_bp.route('/screens', methods=['GET'])
@require_auth()
def get_screens():
    """Get user's screens"""
    user = get_current_user()
    
    # Admins can see all screens, regular users only their own
    if user['is_admin'] or user['is_administrator']:
        screens = execute_query(
            """SELECT s.*, u.username as owner_username 
               FROM screens s 
               LEFT JOIN users u ON s.user_id = u.id 
               ORDER BY s.created_at DESC""",
            fetch_all=True
        )
    else:
        screens = execute_query(
            "SELECT * FROM screens WHERE user_id = %s ORDER BY created_at DESC",
            (session['user_id'],),
            fetch_all=True
        )
    
    return jsonify({'screens': screens or []})

@screens_bp.route('/screens', methods=['POST'])
@require_auth()
def add_screen():
    """Assign screen to user"""
    data = request.get_json()
    serial_number = data.get('serial_number')
    custom_name = data.get('custom_name', '')
    
    if not serial_number:
        return jsonify({'error': 'Serial number required'}), 400
    
    try:
        # Check if controller exists and is unassigned
        controller = execute_query(
            "SELECT * FROM controllers WHERE serial_number = %s AND assigned = FALSE",
            (serial_number,),
            fetch_one=True
        )
        
        if not controller:
            return jsonify({'error': 'Controller not found or already assigned'}), 404
        
        # Create screen assignment
        execute_query(
            """INSERT INTO screens (serial_number, user_id, custom_name, latitude, longitude, online_status, last_seen) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (serial_number, session['user_id'], custom_name, 
             controller['latitude'], controller['longitude'], 
             controller['online_status'], controller['last_seen'])
        )
        
        # Mark controller as assigned
        execute_query(
            "UPDATE controllers SET assigned = TRUE WHERE serial_number = %s",
            (serial_number,)
        )
        
        return jsonify({'message': 'Screen assigned successfully'})
        
    except Exception as e:
        print(f"Error adding screen: {e}")
        return jsonify({'error': 'Failed to assign screen'}), 500

# Additional routes would continue here...
# For brevity, I'll create separate files for different route groups

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(screens_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(system_bp)