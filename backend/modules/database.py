"""
Database connection and utility module for LXCloud
"""
import pymysql
from modules.config import Config

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            database=Config.DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
        return connection
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Please ensure MariaDB/MySQL is running and credentials are correct")
        raise

def init_database():
    """Initialize database schema"""
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
                is_admin BOOLEAN DEFAULT FALSE,
                is_administrator BOOLEAN DEFAULT FALSE,
                two_fa_enabled BOOLEAN DEFAULT FALSE,
                two_fa_secret VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Controllers table (unassigned devices)
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
        
        # Screens table (assigned to users)
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
        
        # Screen data table (only for assigned screens)
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
        
        # Schema version table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                id INT AUTO_INCREMENT PRIMARY KEY,
                version INT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # App info table
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
        
        # UI settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ui_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                setting_key VARCHAR(100) UNIQUE NOT NULL,
                setting_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Database schema initialized successfully")
        return True
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
        print("The application will run but database features will not work")
        print("To fix this issue:")
        print("1. Install and start MariaDB/MySQL")
        print("2. Create database and user as described in README.md")
        print("3. Or use the install.sh script for automatic setup")
        return False

def get_database_version():
    """Get current database version"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result['version'] if result else 0
    except:
        return 0

def update_database_version(version):
    """Update database version"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO schema_version (version) VALUES (%s)", (version,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Failed to update database version: {e}")
        return False

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Execute a database query with proper error handling"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(query, params or ())
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = cursor.rowcount
            
        conn.commit()
        cursor.close()
        conn.close()
        
        return result
    except Exception as e:
        print(f"Database query failed: {e}")
        raise

def check_database_connection():
    """Check if database connection is working"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return True
    except:
        return False