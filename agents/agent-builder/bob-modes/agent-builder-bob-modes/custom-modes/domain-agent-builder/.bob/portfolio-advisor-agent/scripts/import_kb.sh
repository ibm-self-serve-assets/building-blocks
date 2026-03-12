#!/bin/bash
set -e

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "Importing knowledge base..."
cd "$PROJECT_ROOT"

uvx --from ibm-watsonx-orchestrate orchestrate knowledge-bases import -f knowledge_bases/finance_portfolio_kb.yaml

echo "=========================================="
echo "✓ Knowledge base imported successfully!"
echo "=========================================="

# Made with Bob
