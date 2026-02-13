#!/bin/bash

# Import Tools Script

set -e

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "Importing tools..."
echo ""

cd "$PROJECT_ROOT"

# Import patient tools
echo "1. Importing patient_tools.py..."
uvx --from ibm-watsonx-orchestrate orchestrate tools import -k python -f tools/patient_tools.py
echo "✓ Patient tools imported"
echo ""

# Import communication tools
echo "2. Importing communication_tools.py..."
uvx --from ibm-watsonx-orchestrate orchestrate tools import -k python -f tools/communication_tools.py
echo "✓ Communication tools imported"
echo ""

echo "=========================================="
echo "✓ All tools imported successfully!"
echo "=========================================="
