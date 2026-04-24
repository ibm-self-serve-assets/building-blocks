#!/bin/bash

# IBM Turbonomic Dashboard - Start Script
# This script creates a virtual environment, installs dependencies, and starts the application

set -e  # Exit on error

echo "=========================================="
echo "IBM Turbonomic Dashboard - Starting..."
echo "=========================================="

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Display Python version
PYTHON_VERSION=$(python3 --version)
echo "✓ Found $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    echo "✓ Dependencies installed"
else
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found"
    exit 1
fi

# Start the application
echo ""
echo "=========================================="
echo "Starting Turbonomic Dashboard..."
echo "=========================================="
echo ""
echo "🚀 Dashboard will be available at:"
echo "   http://localhost:8050"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
