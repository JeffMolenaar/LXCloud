#!/usr/bin/env python3
"""
Simple test application to serve the LXCloud frontend and provide basic API endpoints
for testing the blank page issue without requiring full database setup.
"""

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'

# Enable CORS for all origins to support local network access
CORS(app, origins="*", supports_credentials=True)

# Path to the built frontend
FRONTEND_DIST_PATH = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')

# Serve the React frontend
@app.route('/')
def serve_frontend():
    """Serve the main React application"""
    return send_from_directory(FRONTEND_DIST_PATH, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    """Serve static files or fall back to index.html for React Router"""
    try:
        return send_from_directory(FRONTEND_DIST_PATH, path)
    except:
        # For React Router, serve index.html for any route that doesn't match a file
        return send_from_directory(FRONTEND_DIST_PATH, 'index.html')

# Basic API endpoints for testing
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Test API is running',
        'database': 'not configured (test mode)'
    }), 200

@app.route('/api/user', methods=['GET'])
def get_user():
    """Mock user endpoint"""
    return jsonify({
        'error': 'Not authenticated (test mode - no database)'
    }), 401

@app.route('/api/register', methods=['POST'])
def register():
    """Mock register endpoint"""
    return jsonify({
        'error': 'Registration not available in test mode'
    }), 503

@app.route('/api/login', methods=['POST'])
def login():
    """Mock login endpoint"""
    return jsonify({
        'error': 'Login not available in test mode'
    }), 503

@app.after_request
def after_request(response):
    """Add CORS headers to all responses"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    return response

if __name__ == '__main__':
    print(f"Starting test server...")
    print(f"Frontend path: {FRONTEND_DIST_PATH}")
    print(f"Frontend exists: {os.path.exists(FRONTEND_DIST_PATH)}")
    print(f"Index.html exists: {os.path.exists(os.path.join(FRONTEND_DIST_PATH, 'index.html'))}")
    print("")
    print("Test the application by visiting:")
    print("  - http://localhost:3000")
    print("  - http://127.0.0.1:3000")  
    print("  - http://[your-local-ip]:3000")
    print("")
    
    app.run(host='0.0.0.0', port=3000, debug=True)