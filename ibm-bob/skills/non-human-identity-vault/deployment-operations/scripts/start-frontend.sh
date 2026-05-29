#!/bin/bash
# Frontend Startup Script
# Starts the React development server

set -e

echo "🚀 Starting Frontend..."

# Navigate to frontend directory
cd "$(dirname "$0")/../../../secret_scanner_app/frontend" || exit 1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file"
    else
        echo "❌ No .env.example found. Please create .env manually."
        exit 1
    fi
fi

# Start development server
echo "🌐 Starting React development server on port 3000..."
echo "📍 Access the application at: http://localhost:3000"
echo ""
npm start

# Made with Bob
