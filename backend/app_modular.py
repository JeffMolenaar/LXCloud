#!/usr/bin/env python3
"""
LXCloud Backend - Modular Version
A complete cloud platform for managing LED screens with Android controllers.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import os
import sys

# Add the current directory to Python path so we can import modules
sys.path.append(os.path.dirname(__file__))

from modules.config import config, Config
from modules.database import init_database, check_database_connection
from modules.routes import register_blueprints

def create_app(config_name=None):
    """Create and configure the Flask application"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config.get(config_name, config['default']))
    
    # Configure CORS
    cors_origins = Config.get_cors_origins()
    CORS(app, origins=cors_origins, supports_credentials=True)
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins=cors_origins)
    
    # Initialize database
    database_available = init_database()
    
    # Register blueprints
    register_blueprints(app)
    
    # Health check endpoint
    @app.route('/api/health')
    def health():
        db_status = check_database_connection()
        return jsonify({
            'status': 'ok',
            'database': 'connected' if db_status else 'disconnected',
            'version': Config.APP_VERSION
        })
    
    # Version endpoint
    @app.route('/api/version')
    def version():
        return jsonify({
            'version': Config.APP_VERSION,
            'database_version': Config.DATABASE_VERSION,
            'environment': config_name
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Store database availability in app context
    app.database_available = database_available
    
    return app, socketio

def main():
    """Main entry point"""
    print("=" * 60)
    print("LXCloud Backend Starting (Modular Version)")
    print("=" * 60)
    
    # Create app
    app, socketio = create_app()
    
    if not app.database_available:
        print("Database initialization failed: Database features will not work")
        print("To fix this issue:")
        print("1. Install and start MariaDB/MySQL")
        print("2. Create database and user as described in README.md")
        print("3. Or use the install.sh script for automatic setup")
        print()
    
    print("Starting Flask application on:")
    print("  - http://localhost:5000 (API)")
    print("  - All interfaces (0.0.0.0:5000)")
    print()
    print("Make sure the frontend is built and served separately")
    print("or use nginx configuration as described in README.md")
    print("=" * 60)
    
    # Run the application
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=app.config.get('DEBUG', False),
        allow_unsafe_werkzeug=True
    )

if __name__ == '__main__':
    main()