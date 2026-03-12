#!/bin/bash
set -e

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "Deploying agent..."
cd "$PROJECT_ROOT"

# Extract agent name from agent_config.yaml
AGENT_NAME=$(grep "^name:" agent_config.yaml | head -1 | awk '{print $2}')

if [ -z "$AGENT_NAME" ]; then
    echo "ERROR: Could not extract agent name from agent_config.yaml"
    exit 1
fi

uvx --from ibm-watsonx-orchestrate orchestrate agents import -f agent_config.yaml
uvx --from ibm-watsonx-orchestrate orchestrate agents deploy -n "$AGENT_NAME"

echo "=========================================="
echo "✓ Agent '$AGENT_NAME' deployed successfully!"
echo "=========================================="

# Made with Bob
