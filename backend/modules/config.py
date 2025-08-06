"""
Configuration module for LXCloud backend
"""
import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'lxcloud-secret-key-change-in-production')
    
    # Session configuration
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Database configuration
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'lxcloud')
    DB_PASS = os.environ.get('DB_PASS', 'lxcloud123')
    DB_NAME = os.environ.get('DB_NAME', 'lxcloud')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    
    # Application configuration
    APP_VERSION = "1.2.0"
    DATABASE_VERSION = 4
    
    # CORS configuration
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost',
        'http://127.0.0.1'
    ]
    
    # Controller configuration
    CONTROLLER_AUTH_PREFIX = 'lxcloud-controller-'
    ADMIN_SETUP_KEY = 'lxcloud-admin-setup-2024'
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    
    # Development configuration
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def get_database_url(cls):
        """Get database connection URL"""
        return f"mysql://{cls.DB_USER}:{cls.DB_PASS}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def get_cors_origins(cls):
        """Get CORS origins with dynamic network detection"""
        origins = cls.CORS_ORIGINS.copy()
        
        # Add local network IPs if available
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            if local_ip and local_ip != '127.0.0.1':
                origins.extend([
                    f'http://{local_ip}',
                    f'http://{local_ip}:3000'
                ])
                
            # Add common local network ranges for better compatibility
            import netifaces
            for interface in netifaces.interfaces():
                try:
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        for addr_info in addrs[netifaces.AF_INET]:
                            ip = addr_info.get('addr')
                            if ip and not ip.startswith('127.') and not ip.startswith('169.254.'):
                                origins.extend([
                                    f'http://{ip}',
                                    f'http://{ip}:3000'
                                ])
                except (ValueError, OSError):
                    continue
        except ImportError:
            pass  # netifaces not available
        except Exception as e:
            print(f"Warning: Could not detect network interfaces: {e}")
        
        return list(set(origins))  # Remove duplicates

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DB_NAME = 'lxcloud_test'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}