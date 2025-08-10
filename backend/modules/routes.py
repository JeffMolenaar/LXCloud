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
            'message': 'User registered successfully',
            'user': user
        }), 201
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

@screens_bp.route('/screens/<int:screen_id>', methods=['PUT'])
@require_auth()
def update_screen(screen_id):
    """Update screen details"""
    data = request.get_json()
    custom_name = data.get('custom_name', '')
    
    user = get_current_user()
    
    try:
        # Verify screen access - admin can update any screen, regular users only their own
        if user['is_admin'] or user['is_administrator']:
            screen = execute_query(
                "SELECT id FROM screens WHERE id = %s",
                (screen_id,),
                fetch_one=True
            )
        else:
            screen = execute_query(
                "SELECT id FROM screens WHERE id = %s AND user_id = %s",
                (screen_id, session['user_id']),
                fetch_one=True
            )
        
        if not screen:
            return jsonify({'error': 'Screen not found or access denied'}), 404
        
        # Update screen
        execute_query(
            "UPDATE screens SET custom_name = %s WHERE id = %s",
            (custom_name, screen_id)
        )
        
        return jsonify({'message': 'Screen updated successfully'})
        
    except Exception as e:
        print(f"Error updating screen: {e}")
        return jsonify({'error': 'Failed to update screen'}), 500

@screens_bp.route('/screens/<int:screen_id>', methods=['DELETE'])
@require_auth()
def delete_screen(screen_id):
    """Delete a screen"""
    user = get_current_user()
    
    try:
        # Verify screen access - admin can delete any screen, regular users only their own
        if user['is_admin'] or user['is_administrator']:
            screen = execute_query(
                "SELECT id FROM screens WHERE id = %s",
                (screen_id,),
                fetch_one=True
            )
        else:
            screen = execute_query(
                "SELECT id FROM screens WHERE id = %s AND user_id = %s",
                (screen_id, session['user_id']),
                fetch_one=True
            )
        
        if not screen:
            return jsonify({'error': 'Screen not found or access denied'}), 404
        
        # Delete screen (cascade will delete related data)
        execute_query("DELETE FROM screens WHERE id = %s", (screen_id,))
        
        return jsonify({'message': 'Screen deleted successfully'})
        
    except Exception as e:
        print(f"Error deleting screen: {e}")
        return jsonify({'error': 'Failed to delete screen'}), 500

@screens_bp.route('/screens/<int:screen_id>/data', methods=['GET'])
@require_auth()
def get_screen_data(screen_id):
    """Get data for a specific screen"""
    user = get_current_user()
    
    try:
        # Verify screen access - admin can access any screen, regular users only their own
        if user['is_admin'] or user['is_administrator']:
            screen = execute_query(
                "SELECT id FROM screens WHERE id = %s",
                (screen_id,),
                fetch_one=True
            )
        else:
            screen = execute_query(
                "SELECT id FROM screens WHERE id = %s AND user_id = %s",
                (screen_id, session['user_id']),
                fetch_one=True
            )
        
        if not screen:
            return jsonify({'error': 'Screen not found or access denied'}), 404
        
        # Get screen data for current year
        current_year = datetime.now().year
        data = execute_query(
            """SELECT information, timestamp
               FROM screen_data
               WHERE screen_id = %s AND year = %s
               ORDER BY timestamp DESC
               LIMIT 100""",
            (screen_id, current_year),
            fetch_all=True
        )
        
        # Format data for response
        formatted_data = []
        for row in data:
            formatted_data.append({
                'information': row['information'],
                'timestamp': row['timestamp'].isoformat() if row['timestamp'] else None
            })
        
        return jsonify({'data': formatted_data})
        
    except Exception as e:
        print(f"Error getting screen data: {e}")
        return jsonify({'error': 'Failed to get screen data'}), 500

# System Routes
@system_bp.route('/controller/register', methods=['POST'])
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
        
        # Verify controller authentication
        if auth_key and not verify_controller_auth(serial_number, auth_key):
            return jsonify({'error': 'Invalid authentication key'}), 401
        
        # Check if controller already exists
        existing = execute_query(
            "SELECT id, assigned FROM controllers WHERE serial_number = %s",
            (serial_number,),
            fetch_one=True
        )
        
        if existing:
            # Update existing controller location and status
            execute_query(
                """UPDATE controllers 
                   SET latitude = %s, longitude = %s, online_status = TRUE, last_seen = CURRENT_TIMESTAMP
                   WHERE serial_number = %s""",
                (latitude, longitude, serial_number)
            )
            
            # Get registration key for response
            reg_key = execute_query(
                "SELECT registration_key FROM controllers WHERE serial_number = %s",
                (serial_number,),
                fetch_one=True
            )
            registration_key = reg_key['registration_key'] if reg_key else None
        else:
            # Create new controller with registration key
            registration_key = generate_registration_key()
            execute_query(
                """INSERT INTO controllers (serial_number, registration_key, latitude, longitude, online_status, assigned)
                   VALUES (%s, %s, %s, %s, TRUE, FALSE)""",
                (serial_number, registration_key, latitude, longitude)
            )
        
        return jsonify({
            'message': 'Controller registered successfully',
            'serial_number': serial_number,
            'registration_key': registration_key,
            'status': 'awaiting_assignment'
        }), 200
        
    except Exception as e:
        print(f"Controller registration error: {e}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@system_bp.route('/device/update', methods=['POST'])
def device_update():
    """Endpoint for Android devices to send updates"""
    try:
        data = request.get_json()
        serial_number = data.get('serial_number')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        information = data.get('information', '')
        
        if not serial_number:
            return jsonify({'error': 'Serial number is required'}), 400
        
        # First check if this is an assigned screen
        screen = execute_query(
            "SELECT id, user_id FROM screens WHERE serial_number = %s",
            (serial_number,),
            fetch_one=True
        )
        
        if screen:
            # This is an assigned screen, store data
            screen_id = screen['id']
            current_year = datetime.now().year
            
            # Update screen location and status
            execute_query(
                """UPDATE screens
                   SET latitude = %s, longitude = %s, online_status = TRUE, last_seen = CURRENT_TIMESTAMP
                   WHERE id = %s""",
                (latitude, longitude, screen_id)
            )
            
            # Add data entry if information provided (only for assigned screens)
            if information:
                execute_query(
                    """INSERT INTO screen_data (screen_id, information, year)
                       VALUES (%s, %s, %s)""",
                    (screen_id, information, current_year)
                )
            
            return jsonify({'message': 'Update received successfully'}), 200
        else:
            # Check if this is an unassigned controller
            controller = execute_query(
                "SELECT id FROM controllers WHERE serial_number = %s",
                (serial_number,),
                fetch_one=True
            )
            
            if controller:
                # Update existing unassigned controller (don't store data)
                execute_query(
                    """UPDATE controllers
                       SET latitude = %s, longitude = %s, online_status = TRUE, last_seen = CURRENT_TIMESTAMP
                       WHERE id = %s""",
                    (latitude, longitude, controller['id'])
                )
            else:
                # Create new unassigned controller
                registration_key = generate_registration_key()
                execute_query(
                    """INSERT INTO controllers (serial_number, registration_key, latitude, longitude, online_status)
                       VALUES (%s, %s, %s, %s, TRUE)""",
                    (serial_number, registration_key, latitude, longitude)
                )
            
            return jsonify({'message': 'Controller update received (not assigned to user yet)'}), 200
            
    except Exception as e:
        print(f"Device update error: {e}")
        return jsonify({'error': f'Update failed: {str(e)}'}), 500

# Admin Routes
@admin_bp.route('/users', methods=['GET'])
@require_admin()
def get_users():
    """Get all users (admin only)"""
    try:
        users = execute_query(
            """SELECT id, username, email, is_admin, is_administrator, two_fa_enabled, created_at
               FROM users
               ORDER BY created_at DESC""",
            fetch_all=True
        )
        
        # Format users for response
        formatted_users = []
        for user in users:
            formatted_users.append({
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'is_admin': bool(user['is_admin']),
                'is_administrator': bool(user['is_administrator']),
                'two_fa_enabled': bool(user['two_fa_enabled']),
                'created_at': user['created_at'].isoformat() if user['created_at'] else None
            })
        
        return jsonify({'users': formatted_users})
        
    except Exception as e:
        print(f"Error getting users: {e}")
        return jsonify({'error': 'Failed to get users'}), 500

@admin_bp.route('/create-admin', methods=['POST'])
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
        
        # Check admin key
        if admin_key != Config.ADMIN_SETUP_KEY:
            return jsonify({'error': 'Invalid admin key'}), 403
        
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
            
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Please provide a valid email address'}), 400
        
        # Check if any admin already exists
        existing_admin = execute_query(
            "SELECT id FROM users WHERE is_admin = TRUE",
            fetch_one=True
        )
        if existing_admin:
            return jsonify({'error': 'Admin account already exists'}), 400
        
        # Check if user exists
        existing_user = execute_query(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (username, email),
            fetch_one=True
        )
        if existing_user:
            return jsonify({'error': 'Username or email already exists'}), 400
        
        # Create admin user
        user = create_user(username, email, password, is_admin=True, is_administrator=True)
        
        if user:
            return jsonify({
                'message': 'Admin account created successfully',
                'user': {'id': user['id'], 'username': user['username'], 'email': user['email']}
            }), 201
        else:
            return jsonify({'error': 'Failed to create admin account'}), 500
        
    except Exception as e:
        print(f"Admin creation error: {e}")
        return jsonify({'error': f'Admin creation failed: {str(e)}'}), 500

# Additional routes would continue here...

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(screens_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(system_bp)