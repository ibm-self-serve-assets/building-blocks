#!/bin/bash

echo "=========================================="
echo "Starting Instana Observability Dashboard"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "Please run ./scripts/setup.sh first"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please copy .env.example to .env and configure it"
    echo ""
    echo "Quick setup:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Check if required environment variables are set
source .env

if [ -z "$INSTANA_BASE_URL" ] || [ -z "$INSTANA_API_TOKEN" ]; then
    echo "❌ Error: Missing required configuration"
    echo "Please configure the following in .env file:"
    echo "  - INSTANA_BASE_URL"
    echo "  - INSTANA_API_TOKEN"
    exit 1
fi

echo "✅ Configuration validated"
echo ""
echo "Application: ${INSTANA_APPLICATION_NAME:-finvault}"
echo "Instana URL: $INSTANA_BASE_URL"
echo "Server: http://${APP_HOST:-0.0.0.0}:${APP_PORT:-8050}"
echo ""
echo "=========================================="
echo "Starting server..."
echo "=========================================="
echo ""

# Run the application
python -m src.app

# Deactivate on exit
deactivate

# Made with Bob
