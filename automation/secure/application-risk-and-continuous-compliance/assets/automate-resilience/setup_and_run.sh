#!/bin/bash

# IBM Concert Insights Dashboard - Setup and Run Script (Unix/macOS/Linux)

echo "=========================================="
echo "IBM Concert Insights Dashboard Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Please edit the .env file with your IBM Concert credentials:"
    echo "  - CONCERT_BASE_URL"
    echo "  - C_API_KEY"
    echo "  - INSTANCE_ID"
    echo ""
    read -p "Press Enter after you've configured the .env file..."
fi

# Validate .env configuration
echo "Validating configuration..."
if grep -q "your_api_key_here" .env || grep -q "your-concert-instance" .env; then
    echo ""
    echo "ERROR: .env file still contains placeholder values!"
    echo "Please edit .env with your actual IBM Concert credentials."
    exit 1
fi
echo "Configuration looks good."
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs

echo "=========================================="
echo "Starting IBM Concert Insights Dashboard"
echo "=========================================="
echo ""
echo "The dashboard will be available at: http://127.0.0.1:8050"
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
python3 app.py

# Made with Bob
