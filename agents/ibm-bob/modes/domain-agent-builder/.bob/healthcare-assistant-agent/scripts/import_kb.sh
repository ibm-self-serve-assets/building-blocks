#!/bin/bash

# Import Knowledge Base Script

set -e

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "Importing knowledge base..."
echo ""

cd "$PROJECT_ROOT"

uvx --from ibm-watsonx-orchestrate orchestrate knowledge-bases import -f knowledge_bases/healthcare_patient_kb.yaml

echo ""
echo "=========================================="
echo "✓ Knowledge base imported successfully!"
echo "=========================================="
