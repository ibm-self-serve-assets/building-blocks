#!/bin/bash
# Backend Startup Script
# Starts the Flask API server

set -e

echo "🚀 Starting Backend..."

# Navigate to backend directory
cd "$(dirname "$0")/../../../secret_scanner_app/backend" || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file"
    else
        echo "❌ No .env.example found. Please create .env manually."
    fi
fi

# Install/update dependencies
echo "📦 Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Start Flask server
echo "🌐 Starting Flask server on port 3001..."
echo "📍 API available at: http://localhost:3001"
echo ""
python api.py

# Made with Bob
