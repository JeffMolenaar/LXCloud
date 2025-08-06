#!/bin/bash

# Simple startup script for testing LXCloud without full server setup

cd "$(dirname "$0")"

echo "Starting LXCloud in standalone mode (no database required)..."
echo ""

# Check if frontend is built
if [ ! -d "frontend/dist" ]; then
    echo "Frontend not built. Building..."
    cd frontend
    npm install
    npm run build
    cd ..
fi

# Check if backend virtual env exists
if [ ! -d "backend/venv" ]; then
    echo "Backend virtual environment not found. Creating..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Start the standalone application
echo "Starting application on port 80..."
echo "You can access it at:"
echo "  - http://localhost"
echo "  - http://127.0.0.1"
echo "  - http://[your-local-ip]"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd backend
source venv/bin/activate
python app_standalone.py