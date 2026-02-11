# Custom Modes for IBM Bob - watsonx Orchestrate & MCP Development

This repository contains expert-level [custom modes for IBM Bob](https://internal.bob.ibm.com/docs/ide/features/custom-modes) designed for building production-grade AI agents and MCP servers. These modes transform IBM Bob into a specialized development assistant with comprehensive guidance and best practices.

**Prerequisites:**
- watsonx Orchestrate ADK installed: `pip install ibm-watsonx-orchestrate`
- Active watsonx Orchestrate environment
- Python 3.10+
- For MCP server mode:
  - MCP SDK: `pip install mcp` or `npm install @modelcontextprotocol/sdk`
  - Node.js 18+ 

## Available Custom Modes
Build and manage watsonx Orchestrate agents, tools, and workflows.
- [`mcp_builder_mode.yml`](mcp_builder_mode.yml) - Mode configuration
- [`mcp_builder_mode_guide.md`](mcp_builder_mode_guide.md) - Comprehensive user guide

Building production-grade Model Context Protocol (MCP) servers in Python and TypeScript/Node.js.
- [`wxo_agent_builder_mode.yml`](wxo_agent_builder_mode.yml) - Mode configuration
- [`wxo_agent_builder_mode_guide.md`](wxo_agent_builder_mode_guide.md) - Comprehensive user guide

**Capabilities:**
- Python and TypeScript/Node.js MCP server development
- Tool, Resource, and Prompt implementation
- Transport protocol configuration (stdio, SSE, HTTP)
- Security best practices and credential management
- Performance optimization and caching strategies
- Integration with AI platforms (watsonx Orchestrate, Claude Desktop, etc.)

## Installation

### Quick Start

1. **Copy the mode configuration:**
   - For watsonx Orchestrate development: Copy contents of `wxo_agent_builder_mode.yml` or `wxo_agent_builder_mode.yml`
   - For MCP server development: Copy contents of `mcp_builder_mode.yml`

2. **Add to your workspace:**
   - Create or edit `.bobmodes` file in your workspace root directory
   - Paste the mode configuration (or add to existing `customModes` list)

3. **Reload IBM Bob:**
   - Press `Cmd/Ctrl + Shift + P`
   - Select "Reload Window"

4. **Select the mode:**
   - Click the mode selector in IBM Bob
   - Choose "🤖 wxO Agent Builder" or "🔌 MCP Builder"

### Global Installation (Optional)

For system-wide access, copy the YAML file to:
- **Windows**: `%APPDATA%\IBM Bob\User\globalStorage\ibm.bob-code\settings\custom_modes.yaml`
- **macOS**: `~/Library/Application Support/IBM Bob/User/globalStorage/ibm.bob-code/settings/custom_modes.yaml`
- **Linux**: `~/.config/IBM Bob/User/globalStorage/ibm.bob-code/settings/custom_modes.yaml`

## Setting up the watsonx Orchestrate MCP Servers

The watsonx Orchestrate Agent Builder mode requires two MCP servers configured in [`mcp_watsonx_orchestrate.json`](mcp_watsonx_orchestrate.json). If you haven't added MCP servers to IBM Bob yet, read about [MCP servers in IBM Bob](https://internal.bob.ibm.com/docs/ide/features/mcp/using-mcp-in-bob).

### 1. watsonx Orchestrate ADK Documentation Server

**Purpose:** Provides a tool that queries the [watsonx Orchestrate Agent Developer's Kit (ADK)](https://developer.watson-orchestrate.ibm.com/) developer documentation.

**What it does:** Gives Bob the context needed to understand how all watsonx Orchestrate ADK features work, including agents, tools, workflows, and best practices.

**Configuration:**
```json
"wxo-docs": {
    "command": "uvx",
    "args": [
        "mcp-proxy",
        "--transport",
        "streamablehttp",
        "https://developer.watson-orchestrate.ibm.com/mcp"
    ],
    "alwaysAllow": ["SearchIbmWatsonxOrchestrateAdk"],
    "disabled": false
}
```

**No additional setup required** - this server connects to IBM's hosted documentation service.

### 2. watsonx Orchestrate ADK Execution Server

**Purpose:** Gives Bob direct access to all commands in the watsonx Orchestrate ADK.

**What it does:** Allows Bob to create, import, or list agents, tools, MCP toolkits, knowledge bases, and connections. Bob can also export agents and Python tools into your workspace.

**Configuration:**
```json
"orchestrate-adk": {
    "command": "uvx",
    "args": [
        "--with",
        "ibm-watsonx-orchestrate==1.14.1",
        "ibm-watsonx-orchestrate-mcp-server==1.14.1"
    ],
    "env": {
        "WXO_MCP_WORKING_DIRECTORY": "<full path to your code project directory>"
    },
    "alwaysAllow": [
        "list_agents",
        "export_agent",
        "get_tool_template",
        "list_tools",
        "list_toolkits",
        "list_knowledge_bases",
        "check_knowledge_base_status",
        "list_connections",
        "list_voice_configs",
        "list_models",
        "check_version"
    ],
    "disabled": false
}
```

**Setup Required:**
1. Install the [watsonx Orchestrate ADK](https://developer.watson-orchestrate.ibm.com/):
   ```bash
   pip install ibm-watsonx-orchestrate
   ```

2. Update the `WXO_MCP_WORKING_DIRECTORY` environment variable in [`mcp_watsonx_orchestrate.json`](mcp_watsonx_orchestrate.json) with the full path to your code project directory.

3. **Important:** Since this value changes across different projects, add the MCP server at the **Project level** rather than Global level in IBM Bob's MCP settings.

## Usage Examples

### Using watsonx Orchestrate Agent Builder Mode

```
# Example tasks you can ask Bob to do:

"Create a customer support agent with CRM and order management tools"
"Build a Python tool that queries our PostgreSQL database"
"Design a supervisor agent that routes to sales, support, and operations agents"
"Import the Slack MCP toolkit for our agents"
"Create an agentic workflow for employee onboarding with approvals"
```

### Using MCP Builder Mode

```
# Example tasks you can ask Bob to do:

"Create a Python MCP server for file system operations"
"Build a TypeScript MCP server that integrates with GitHub API"
"Add a tool to query PostgreSQL database with proper security"
"Convert my stdio server to use SSE transport for remote access"
"Implement resource support for accessing documentation files"
```

