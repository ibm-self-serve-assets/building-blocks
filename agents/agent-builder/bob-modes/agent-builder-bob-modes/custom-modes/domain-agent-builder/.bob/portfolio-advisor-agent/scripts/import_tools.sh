#!/bin/bash
set -e

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "Importing tools..."
cd "$PROJECT_ROOT"

echo "1. Importing account_holder_tools.py..."
uvx --from ibm-watsonx-orchestrate orchestrate tools import -k python -f tools/account_holder_tools.py
echo "✓ Account holder tools imported"

echo "2. Importing communication_tools.py..."
uvx --from ibm-watsonx-orchestrate orchestrate tools import -k python -f tools/communication_tools.py
echo "✓ Communication tools imported"

echo "=========================================="
echo "✓ All tools imported successfully!"
echo "=========================================="

# Made with Bob
