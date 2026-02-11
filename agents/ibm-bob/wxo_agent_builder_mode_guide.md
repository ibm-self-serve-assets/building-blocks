# watsonx Orchestrate Agent Builder Mode - User Guide

## Overview

The **wxO Agent Builder** mode is an expert-level custom mode for IBM Bob designed specifically for building and managing watsonx Orchestrate agents, tools, and workflows. This mode provides comprehensive guidance, best practices, and patterns for production-grade agent development.

## Target Audience

This mode is designed for expert developers who:
- Have experience with watsonx Orchestrate and the ADK
- Understand LLM concepts and agent architectures
- Are comfortable with Python development
- Need to build production-ready agents and tools

## Prerequisites

Before using this mode, ensure you have:

1. **watsonx Orchestrate ADK installed**
   ```bash
   pip install ibm-watsonx-orchestrate
   ```

2. **MCP Servers configured** (see `mcp_watsonx_orchestrate.json`)
   - wxo-docs: Documentation query tool
   - orchestrate-adk: Direct ADK CLI access

3. **Active watsonx Orchestrate environment**
   ```bash
   orchestrate env list
   orchestrate env activate --name your_env_name
   ```

4. **Working directory configured** in MCP server settings
   - Update `WXO_MCP_WORKING_DIRECTORY` in `mcp_watsonx_orchestrate.json`

## Installation

### Project-Level Installation (Recommended)

1. Copy the contents of `wxo_agent_builder_mode.yml`
2. Create or edit `.bobmodes` file in your workspace root directory
3. Paste the content (or add to existing `customModes` list)
4. Reload IBM Bob: `Cmd/Ctrl + Shift + P` → "Reload Window"
5. Select "🤖 wxO Agent Builder" from the mode selector

### Global Installation

Copy `wxo_agent_builder_mode.yml` to:
- **Windows**: `%APPDATA%\IBM Bob\User\globalStorage\ibm.bob-code\settings\custom_modes.yaml`
- **macOS**: `~/Library/Application Support/IBM Bob/User/globalStorage/ibm.bob-code/settings/custom_modes.yaml`
- **Linux**: `~/.config/IBM Bob/User/globalStorage/ibm.bob-code/settings/custom_modes.yaml`

## Mode Capabilities

### What This Mode Excels At

1. **Native Agent Development**
   - Creating agent YAML specifications
   - Optimizing agent instructions for specific use cases
   - Selecting appropriate LLMs and agent styles
   - Configuring tool and collaborator relationships

2. **Python Tool Development**
   - Writing tools with `@tool` decorator
   - Implementing credential management
   - Building multi-function tool packages
   - Creating requirements.txt files

3. **MCP Toolkit Integration**
   - Importing local MCP toolkits
   - Configuring remote MCP connections
   - Managing toolkit credentials
   - Debugging MCP server issues

4. **Agentic Workflow Design**
   - Designing workflow architectures
   - Implementing control structures (if-then-else, loops, foreach)
   - Creating human-in-the-loop patterns
   - Optimizing long-running processes

5. **Multi-Agent Orchestration**
   - Designing supervisor-worker hierarchies
   - Implementing agent collaboration patterns
   - Optimizing agent routing strategies

## Key Features

### Expert-Level Guidance

The mode provides:
- Production-ready code patterns
- Performance optimization strategies
- Security best practices
- Cost-efficiency recommendations
- Scalability considerations

### Full Development Access

Tool groups enabled:
- **read**: File reading and analysis
- **edit**: Complete file editing capabilities
- **execute**: ADK CLI command execution
- **mcp**: Access to watsonx Orchestrate MCP tools
- **browser**: Testing deployed agents

### Comprehensive Instructions

Built-in guidance for:
- Agent description and instruction writing
- LLM selection strategies
- Agent style selection (default/react/planner)
- Tool vs collaborator decision-making
- Python tool development patterns
- MCP toolkit integration
- Agentic workflow design
- Multi-agent collaboration
- Error handling and validation
- Security and credential management

## Common Use Cases

### 1. Creating a Simple Agent with Tools

**Task**: "Create a customer support agent that can look up orders and process returns"

The mode will:
1. Design the agent architecture
2. Select appropriate LLM (likely Granite 3-8B for speed)
3. Write clear agent instructions
4. Create or identify required tools
5. Generate agent YAML specification
6. Import using ADK CLI
7. Export for version control

### 2. Building a Python Tool

**Task**: "Create a Python tool that fetches customer data from our CRM API"

The mode will:
1. Create Python file with `@tool` decorator
2. Add proper type hints and docstrings
3. Implement credential management via connections
4. Add error handling and validation
5. Create requirements.txt if needed
6. Import tool using ADK CLI
7. Test tool functionality

### 3. Designing a Multi-Agent System

**Task**: "Design a supervisor agent that routes to sales, support, and operations agents"

The mode will:
1. Design supervisor-worker architecture
2. Create supervisor agent with collaborators
3. Define clear routing logic in instructions
4. Create specialized worker agents with tools
5. Optimize agent descriptions for routing
6. Test collaboration flows
7. Export all agents for version control

### 4. Integrating an MCP Toolkit

**Task**: "Import the Slack MCP toolkit for our agents to use"

The mode will:
1. Determine toolkit source (npm, PyPI, local, remote)
2. Configure connection for credentials
3. Generate import command with appropriate flags
4. Execute import via ADK CLI
5. Verify toolkit tools are available
6. Document toolkit usage

### 5. Creating an Agentic Workflow

**Task**: "Create a workflow for employee onboarding with approvals"

The mode will:
1. Design workflow architecture with nodes and edges
2. Identify required agents, tools, and human interactions
3. Implement control structures (conditionals, loops)
4. Add human-in-the-loop approval steps
5. Configure async execution
6. Test workflow execution
7. Export workflow definition

## Best Practices When Using This Mode

### 1. Start with Clear Requirements

Provide specific details about:
- What the agent/tool should do
- What data sources it needs access to
- What actions it should perform
- Performance and cost constraints
- Security requirements

### 2. Iterate Incrementally

- Build and test tools independently first
- Create simple agents before complex ones
- Test individual components before integration
- Add collaborators one at a time
- Validate each step before proceeding

### 3. Leverage MCP Tools

The mode has access to:
- **SearchIbmWatsonxOrchestrateAdk**: Query documentation
- **list_agents**, **export_agent**: Manage agents
- **list_tools**, **import_tool**: Manage tools
- **list_toolkits**: View available toolkits
- **list_connections**: Manage credentials
- **list_models**: View available LLMs

### 4. Version Control Everything

- Export agents, tools, and workflows to files
- Store in Git repository
- Use semantic versioning
- Document changes in commits
- Maintain separate branches for draft/live

### 5. Optimize for Production

- Choose smallest LLM that meets requirements
- Write efficient agent instructions
- Implement proper error handling
- Use connections for credentials
- Test with vulnerability testing
- Monitor costs and performance

## Example Workflows

### Workflow 1: Creating a New Agent from Scratch

```
User: "Create a sales agent that can search products, check inventory, and create quotes"

Mode Actions:
1. Analyzes requirements
2. Selects LLM (Granite 3-8B for speed)
3. Chooses agent style (default for simple routing)
4. Writes agent instructions with tool usage guidance
5. Identifies/creates required tools:
   - search_products
   - check_inventory
   - create_quote
6. Generates agent YAML specification
7. Uses execute_command to import agent
8. Exports agent for version control
9. Provides testing recommendations
```

### Workflow 2: Building a Python Tool with Credentials

```
User: "Create a tool to send Slack messages using our workspace token"

Mode Actions:
1. Creates Python file with @tool decorator
2. Implements function with proper type hints
3. Adds credential retrieval from environment variables
4. Implements error handling for API failures
5. Creates comprehensive docstring
6. Generates requirements.txt with slack-sdk
7. Creates connection for Slack token
8. Imports tool with --app-id flag
9. Tests tool functionality
10. Exports tool for version control
```

### Workflow 3: Designing a Multi-Agent System

```
User: "Design an enterprise assistant with specialized agents for different departments"

Mode Actions:
1. Designs supervisor-worker architecture
2. Creates supervisor agent:
   - LLM: Llama 3.3 70B (complex routing)
   - Style: react (reasoning required)
   - Collaborators: dept_agents
3. Creates department agents:
   - Sales agent with CRM tools
   - Support agent with ticketing tools
   - Operations agent with logistics tools
4. Optimizes agent descriptions for routing
5. Writes clear handoff protocols
6. Imports all agents in correct order
7. Tests routing logic
8. Exports complete system
```

## Troubleshooting

### Agent Not Using Tools Correctly

**Solution**: The mode will:
- Review agent instructions for clarity
- Check tool descriptions are comprehensive
- Verify tools are properly attached to agent
- Test tool functionality independently
- Adjust instructions to be more explicit about tool usage

### MCP Toolkit Import Failing

**Solution**: The mode will:
- Verify toolkit package/path is correct
- Check language flag matches toolkit type
- Validate connection credentials if required
- Review toolkit requirements are installed
- Test toolkit command manually
- Check MCP server logs for errors

### Agent Routing to Wrong Collaborator

**Solution**: The mode will:
- Review collaborator descriptions for clarity
- Make descriptions more specific and distinct
- Adjust supervisor instructions for routing logic
- Test with various input scenarios
- Consider using different LLM for supervisor

### Tool Credentials Not Working

**Solution**: The mode will:
- Verify connection is created and configured
- Check credentials are set correctly
- Confirm app-id is associated with tool
- Test environment variables are accessible
- Review connection type (key_value required)

## Advanced Patterns

### Pattern 1: Dynamic Tool Selection

Create agents that intelligently select from many tools based on context.

**Key Elements**:
- Comprehensive tool descriptions
- Clear tool usage guidelines in instructions
- React agent style for reasoning
- Tool categorization in instructions

### Pattern 2: Human-in-the-Loop Workflows

Design workflows that pause for human approval or input.

**Key Elements**:
- Agentic workflow with user interaction nodes
- Clear approval criteria
- Timeout handling
- Notification mechanisms

### Pattern 3: Multi-Stage Agent Pipelines

Chain multiple agents for complex processing.

**Key Elements**:
- Clear data passing between agents
- Error handling at each stage
- Progress tracking
- Rollback mechanisms

### Pattern 4: Knowledge-Enhanced Agents

Combine agents with knowledge bases for RAG.

**Key Elements**:
- Knowledge base creation and indexing
- Agent configuration with knowledge sources
- Query optimization
- Relevance tuning

## Performance Optimization Tips

1. **LLM Selection**
   - Start with Granite 3-8B, upgrade only if needed
   - Use Llama 3.3 70B for complex reasoning only
   - Consider latency vs accuracy tradeoffs

2. **Instruction Optimization**
   - Be specific to reduce unnecessary tool calls
   - Provide examples of expected behavior
   - Use structured formats for consistency

3. **Tool Design**
   - Keep tools focused and single-purpose
   - Batch operations where possible
   - Cache frequently accessed data
   - Implement timeouts for external calls

4. **Agent Architecture**
   - Avoid deep agent hierarchies (3 levels max)
   - Use tools instead of collaborators when possible
   - Minimize agent-to-agent communication

## Security Considerations

1. **Credential Management**
   - Always use connections for credentials
   - Never hardcode API keys or tokens
   - Use environment variables in tools
   - Rotate credentials regularly

2. **Input Validation**
   - Validate all tool inputs
   - Sanitize user-provided data
   - Implement rate limiting
   - Check for injection attacks

3. **Agent Instructions**
   - Test for prompt injection vulnerabilities
   - Use vulnerability testing feature
   - Implement guardrails for sensitive operations
   - Review instructions for security issues

4. **Tool Permissions**
   - Use least privilege principle
   - Limit tool access to required resources
   - Audit tool usage regularly
   - Implement approval workflows for sensitive actions

## Getting Help

### Within the Mode

Ask Bob to:
- "Explain the difference between agent styles"
- "Show me an example of a Python tool with credentials"
