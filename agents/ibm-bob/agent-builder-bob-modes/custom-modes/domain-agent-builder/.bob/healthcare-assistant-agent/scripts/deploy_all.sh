#!/bin/bash

# Healthcare Assistant Agent - Complete Deployment Script
# This script deploys the entire agent including tools, knowledge base, and agent configuration

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "=========================================="
echo "Healthcare Assistant Agent Deployment"
echo "=========================================="
echo ""
echo "Project directory: $PROJECT_DIR"
echo ""

# Step 1: Import Tools
echo "=========================================="
echo "Step 1: Importing Patient Management Tools"
echo "=========================================="
cd "$PROJECT_DIR"
uvx --from ibm-watsonx-orchestrate orchestrate tools import -k python -f tools/patient_tools.py
echo "✓ Patient tools imported successfully"
echo ""

echo "=========================================="
echo "Step 2: Importing Communication Tools"
echo "=========================================="
uvx --from ibm-watsonx-orchestrate orchestrate tools import -k python -f tools/communication_tools.py
echo "✓ Communication tools imported successfully"
echo ""

# Step 2: Import Knowledge Base
echo "=========================================="
echo "Step 3: Importing Healthcare Patient Knowledge Base"
echo "=========================================="
uvx --from ibm-watsonx-orchestrate orchestrate knowledge-bases import -f knowledge_bases/healthcare_patient_kb.yaml
echo "✓ Knowledge base imported successfully"
echo ""

# Step 3: Deploy Agent
echo "=========================================="
echo "Step 4: Deploying Healthcare Assistant Agent"
echo "=========================================="
uvx --from ibm-watsonx-orchestrate orchestrate agents import -f agent_config.yaml
echo "✓ Agent configuration imported successfully"
echo ""

uvx --from ibm-watsonx-orchestrate orchestrate agents deploy -n healthcare_assistant_agent
echo "✓ Agent deployed successfully"
echo ""

# Success message
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "Healthcare Assistant Agent is now live and ready to use!"
echo ""
echo "Test the agent with these sample queries:"
echo "  • 'Show me all ICU patients'"
echo "  • 'Get patient data for PAT001'"
echo "  • 'Generate an appointment confirmation for PAT005'"
echo "  • 'What patients are in critical condition?'"
echo "  • 'Send a medication reminder to PAT001'"
echo ""
