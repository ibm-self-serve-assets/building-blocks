#!/bin/bash

echo "=========================================="
echo "Instana Observability Dashboard Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check Python version is 3.8+
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python $PYTHON_VERSION is installed, but Python 3.8+ is required"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to create virtual environment"
    exit 1
fi

echo "✅ Virtual environment created"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your Instana credentials"
    echo "   Required settings:"
    echo "   - INSTANA_BASE_URL"
    echo "   - INSTANA_API_TOKEN"
    echo "   - INSTANA_APPLICATION_NAME (default: finvault)"
else
    echo ""
    echo "✅ .env file already exists"
fi

# Create logs directory
mkdir -p logs

echo ""
echo "=========================================="
echo "✅ Setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Instana credentials:"
echo "   nano .env"
echo ""
echo "2. Run the application:"
echo "   ./scripts/run.sh"
echo ""
echo "3. Access the dashboard at:"
echo "   http://localhost:8050"
echo ""

# Made with Bob
