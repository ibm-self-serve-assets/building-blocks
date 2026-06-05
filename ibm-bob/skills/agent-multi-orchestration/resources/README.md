# Multi-Agent Orchestration Resources

This folder contains reusable code examples and deployment scripts for multi-agent systems.

## Code Examples

### Agent Examples
- **`customer_support_agents.py`** - Multi-agent customer support system with supervisor-worker pattern
  - Demonstrates agent collaboration and routing
  - Shows how to create specialized agents
  - Illustrates supervisor agent pattern

### Workflow Examples
- **`data_processing_workflow.py`** - Sequential workflow with validation and branching
  - Shows @flow decorator usage
  - Demonstrates conditional branching
  - Illustrates data validation patterns

- **`approval_workflow.py`** - Human-in-the-loop approval workflow
  - Shows user form integration
  - Demonstrates approval/rejection branching
  - Illustrates human approval patterns

### Deployment Scripts
- **`deploy_orchestration.sh`** - Complete bash deployment automation
  - Backs up current environment
  - Deploys connections, models, MCP toolkits, agents, and workflows
  - Includes rollback capability
  - Provides verification checks

## Dependencies

These examples rely on the **agent-builder** skill for:
- Agent creation and configuration
- Tool and knowledge base setup
- MCP server integration
- Connection management

For A2A protocol and AI Gateway integration, refer to the respective sections in the workflow markdown files.

## Usage

### Deploy Customer Support System
```bash
python resources/customer_support_agents.py
```

### Import Workflows
```bash
# Data processing workflow
orchestrate tools import -k flow -f resources/data_processing_workflow.py

# Approval workflow
orchestrate tools import -k flow -f resources/approval_workflow.py
```

### Run Deployment Script
```bash
chmod +x resources/deploy_orchestration.sh
./resources/deploy_orchestration.sh
```

## Skill Relationships

- **agent-builder**: Use for creating individual agents, tools, and knowledge bases
- **agent-integrate**: Use for REST API integration with watsonx Orchestrate
- **multi-agent-orchestration**: Use for coordinating multiple agents, workflows, and systems

## Notes

- All Python examples require the ADK (Agent Development Kit) to be installed
- Bash scripts require the `orchestrate` CLI to be configured
- Examples are templates - customize for your specific use case
- Always test in draft environment before deploying to live