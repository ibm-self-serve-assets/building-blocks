#!/bin/bash

# Start script for Secret Scanner Application

echo "Starting Automated Hardcoded Secret Detection and Vault Migration..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and set VAULT_ADDR and VAULT_TOKEN"
    echo ""
    read -p "Press Enter to continue after editing .env file..."
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check Vault connection
echo "Checking Vault connection..."
if curl -s -o /dev/null -w "%{http_code}" "$VAULT_ADDR/v1/sys/health" | grep -q "200\|429\|472\|473"; then
    echo "✓ Vault is accessible at $VAULT_ADDR"
else
    echo "✗ Cannot connect to Vault at $VAULT_ADDR"
    echo "Please check VAULT_ADDR in .env file and ensure Vault is running"
    exit 1
fi

# Start the application
echo ""
echo "Starting application on port ${DASH_PORT:-8050}..."
echo "Access the application at: http://localhost:${DASH_PORT:-8050}"
echo ""
python app.py

# Made with Bob
