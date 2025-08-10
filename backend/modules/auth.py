"""
Authentication and authorization module for LXCloud
"""
from functools import wraps
from flask import session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
import qrcode
from io import BytesIO
import base64
import secrets
import hashlib

def require_auth():
    """Decorator to check if user is authenticated"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_admin():
    """Decorator to check if user is admin or administrator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            from modules.database import execute_query
            user = execute_query(
                "SELECT is_admin, is_administrator FROM users WHERE id = %s",
                (session['user_id'],),
                fetch_one=True
            )
            
            if not user or (not user['is_admin'] and not user['is_administrator']):
                return jsonify({'error': 'Admin access required'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_super_admin():
    """Decorator to check if user is super admin"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            from modules.database import execute_query
            user = execute_query(
                "SELECT is_admin FROM users WHERE id = %s",
                (session['user_id'],),
                fetch_one=True
            )
            
            if not user or not user['is_admin']:
                return jsonify({'error': 'Super admin access required'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def hash_password(password):
    """Hash a password for storing in database"""
    return generate_password_hash(password)

def verify_password(password_hash, password):
    """Verify a password against its hash"""
    return check_password_hash(password_hash, password)

def create_user(username, email, password, is_admin=False, is_administrator=False):
    """Create a new user"""
    try:
        from modules.database import execute_query
        password_hash = hash_password(password)
        
        user_id = execute_query(
            """INSERT INTO users (username, email, password_hash, is_admin, is_administrator) 
               VALUES (%s, %s, %s, %s, %s)""",
            (username, email, password_hash, is_admin, is_administrator)
        )
        
        return get_user_by_id(user_id)
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def get_user_by_id(user_id):
    """Get user by ID"""
    from modules.database import execute_query
    return execute_query(
        "SELECT id, username, email, is_admin, is_administrator, two_fa_enabled FROM users WHERE id = %s",
        (user_id,),
        fetch_one=True
    )

def get_user_by_username(username):
    """Get user by username"""
    from modules.database import execute_query
    return execute_query(
        "SELECT * FROM users WHERE username = %s",
        (username,),
        fetch_one=True
    )

def get_user_by_email(email):
    """Get user by email"""
    from modules.database import execute_query
    return execute_query(
        "SELECT * FROM users WHERE email = %s",
        (email,),
        fetch_one=True
    )

def authenticate_user(username_or_email, password):
    """Authenticate user with username/email and password"""
    # Try to find user by username or email
    user = get_user_by_username(username_or_email)
    if not user:
        user = get_user_by_email(username_or_email)
    
    if user and verify_password(user['password_hash'], password):
        return user
    
    return None

def generate_2fa_secret():
    """Generate a new 2FA secret"""
    return pyotp.random_base32()

def generate_2fa_qr_code(username, secret, app_name='LXCloud'):
    """Generate QR code for 2FA setup"""
    try:
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            username,
            issuer_name=app_name
        )
        
        img = qrcode.make(totp_uri)
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None

def verify_2fa_token(secret, token):
    """Verify 2FA token"""
    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    except Exception as e:
        print(f"Error verifying 2FA token: {e}")
        return False

def enable_2fa_for_user(user_id, secret):
    """Enable 2FA for a user"""
    try:
        from modules.database import execute_query
        execute_query(
            "UPDATE users SET two_fa_enabled = TRUE, two_fa_secret = %s WHERE id = %s",
            (secret, user_id)
        )
        return True
    except Exception as e:
        print(f"Error enabling 2FA: {e}")
        return False

def disable_2fa_for_user(user_id):
    """Disable 2FA for a user"""
    try:
        from modules.database import execute_query
        execute_query(
            "UPDATE users SET two_fa_enabled = FALSE, two_fa_secret = NULL WHERE id = %s",
            (user_id,)
        )
        return True
    except Exception as e:
        print(f"Error disabling 2FA: {e}")
        return False

def generate_registration_key():
    """Generate a secure registration key for controllers"""
    return secrets.token_urlsafe(32)

def generate_controller_auth_key(serial_number):
    """Generate authentication key for controller"""
    from modules.config import Config
    return hashlib.sha256(f"{Config.CONTROLLER_AUTH_PREFIX}{serial_number}".encode()).hexdigest()[:16]

def verify_controller_auth(serial_number, provided_key):
    """Verify controller authentication key"""
    expected_key = generate_controller_auth_key(serial_number)
    return provided_key == expected_key

def get_current_user():
    """Get current authenticated user"""
    if 'user_id' not in session:
        return None
    
    return get_user_by_id(session['user_id'])

def is_first_user():
    """Check if this is the first user (for admin setup)"""
    try:
        from modules.database import execute_query
        count = execute_query("SELECT COUNT(*) as count FROM users", fetch_one=True)
        return count['count'] == 0
    except:
        return True

def login_user(user):
    """Log in a user (set session)"""
    session['user_id'] = user['id']
    session.permanent = True

def logout_user():
    """Log out the current user"""
    session.pop('user_id', None)

def change_user_password(user_id, new_password):
    """Change user password"""
    try:
        from modules.database import execute_query
        password_hash = hash_password(new_password)
        execute_query(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (password_hash, user_id)
        )
        return True
    except Exception as e:
        print(f"Error changing password: {e}")
        return False