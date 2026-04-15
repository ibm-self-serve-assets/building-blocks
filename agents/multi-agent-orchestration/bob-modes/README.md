# 🚀 Multi-Agent Orchestration Bob Modes - Setup Guide

This directory contains custom Bob modes for building multi-agent orchestration systems with watsonx Orchestrate and MCP (Model Context Protocol) servers. Follow the instructions below to import and use these modes in your Bob projects.

## 📦 Available Modes

### Base Mode
- **[multi-agent-orchestration-base-mode](./bob-modes/base-modes/multiagent-orchestration-bob-modes/base-modes/multi-agent-orchestration-base-mode.zip)** - Foundation mode for building production-grade AI agents, MCP servers, and multi-agent workflows

### Custom Modes
- **[agent-model-gateway-bob-mode](./bob-modes/base-modes/multiagent-orchestration-bob-modes/custom-modes/agent-model-gateway-bob-mode.zip)** - Comprehensive mode for integrating third-party LLM models into watsonx Orchestrate via the AI Gateway

---

## 🆕 For New Projects

When working with a **new project**, there are no existing custom modes. You can directly add the multi-agent orchestration mode.

### 📁 Add Mode Configuration

1. **Download and extract** the mode's `.zip` file from the `base-modes/` folder
2. **Open your project** in Bob UI
3. **Navigate** to the project workspace (file explorer)
4. **Copy the `.bob` folder** from the extracted mode:

```
.bob/
├── custom_modes.yaml
└── rules/
    └── multi-agent-orchestration/
        └── [mode rules files]
```

5. **Paste** the `.bob/` directory into your project root
6. The structure should look like:

```
your-project/
├── .bob/
│   ├── custom_modes.yaml
│   └── rules/
│       └── multi-agent-orchestration/
└── [your project files]
```

---

### ▶️ Start Using the Mode

- Refresh or reload the Bob UI (if required)
- Navigate to **Modes / Custom Modes section**
- Select the multi-agent orchestration mode you installed
- Start using it in your workflows

---

## 🔁 For Existing Projects

If your project already has custom modes configured, follow these steps carefully to avoid breaking existing setups.

---

### ⚠️ Do Not Overwrite Existing Configuration

- Do **not replace** the existing `.bob/custom_modes.yaml`
- This file may already contain active modes used by your project

---

### ✏️ Append New Mode Configuration

1. **Download and extract** the mode's `.zip` file
2. **Open** `.bob/custom_modes.yaml` in the Bob UI editor
3. **Add** the multi-agent orchestration mode at the end of the file

#### Example:

```yaml
# Existing custom modes
- slug: existing-mode-1
  name: Existing Mode 1
  # ... existing configuration ...

- slug: existing-mode-2
  name: Existing Mode 2
  # ... existing configuration ...

# Add multi-agent orchestration mode
- slug: multi-agent-orchestration
  name: 🤖 Multi-Agent Orchestration
  # ... new mode configuration ...
```

---

### 📂 Maintain Rules Folder Structure

1. **Navigate** to `.bob/rules/`
2. **Add** the new rules folder from the extracted mode
3. **Ensure** the final structure looks like:

```
.bob/
├── custom_modes.yaml
└── rules/
    ├── existing-mode-1/
    ├── existing-mode-2/
    └── multi-agent-orchestration/
```

👉 Do **not modify or delete existing rule folders**

---

### ✅ Verify in Bob UI

After completing the setup:

- Go to **Modes / Custom Modes**
- Confirm:
  - Existing modes are still available
  - Multi-agent orchestration mode appears
- Open the mode and ensure no configuration errors are shown

---

## 🧠 Best Practices

- Always **append**, never overwrite `custom_modes.yaml`
- Keep each mode isolated under its own rules folder
- Validate YAML formatting carefully (indentation matters)
- Reload the UI if changes are not reflected immediately
- Review the mode-specific README for prerequisites and usage instructions

---

## 📚 Mode-Specific Documentation

The base mode has detailed documentation:

- **Multi-Agent Orchestration Base Mode**: See `multiagent-orchestration-bob-modes/base-modes/multi-agent-orchestration-base-mode/README.md`
  - Prerequisites: watsonx Orchestrate ADK, Python 3.10+, MCP SDK
  - Builds production-grade AI agents and MCP servers
  - Supports watsonx Orchestrate agent development
  - Includes MCP server development capabilities

---

## 🔧 Prerequisites

Before using this mode, ensure you have:

### Required
- **IBM Bob** - Latest version
- **watsonx Orchestrate ADK**: `pip install ibm-watsonx-orchestrate`
- **Python 3.10+**
- **watsonx Orchestrate environment** with API access

### For MCP Server Development
- **MCP SDK**: `pip install mcp` (Python) or `npm install @modelcontextprotocol/sdk` (TypeScript)
- **Node.js 18+** (for TypeScript/Node.js MCP servers)

### MCP Servers Configuration
Follow the MCP server installation instructions in the base mode README to configure:
1. **watsonx Orchestrate ADK Documentation Server** - Queries ADK documentation
2. **watsonx Orchestrate ADK Execution Server** - Direct access to ADK commands

---

## 🎯 What You Can Build

With this mode, you can:

### watsonx Orchestrate Agents
- Build production-grade AI agents
- Create custom tools and integrations
- Configure knowledge bases and RAG capabilities
- Set up voice configurations and channels
- Deploy and manage agents in watsonx Orchestrate

### MCP Servers
- Build Python MCP servers
- Build TypeScript/Node.js MCP servers
- Implement file system operations
- Create API integrations (GitHub, databases, etc.)
- Convert between stdio and SSE transports
- Add resource support for documentation

### Multi-Agent Systems
- Orchestrate multiple agents working together
- Design agent communication patterns
- Implement workflow coordination
- Build complex agent hierarchies

---

## 💡 Quick Start Tips

1. **Install prerequisites first** - Ensure ADK and MCP SDK are installed
2. **Configure MCP servers** - Follow the base mode README for MCP setup
3. **Start with simple agents** - Build basic agents before complex orchestration
4. **Use ADK documentation** - The mode has access to full ADK documentation
5. **Enable auto-approve** - In Bob UI for smoother workflows (except for questions)

---

## 📖 Usage Examples

### Building watsonx Orchestrate Agents
```
"Create a customer service agent with order tracking tools"
"Build an agent with RAG capabilities for product documentation"
"Add a voice configuration for phone channel integration"
```

### Building MCP Servers
```
"Create a Python MCP server for file system operations"
"Build a TypeScript MCP server that integrates with GitHub API"
"Add a tool to query PostgreSQL database with proper security"
"Convert my stdio server to use SSE transport for remote access"
```

### Multi-Agent Orchestration
```
"Design a multi-agent system for customer support workflow"
"Create an orchestration pattern for research and analysis agents"
"Build a supervisor agent that coordinates specialist agents"
```

---

## 🎯 Outcome

After completing these steps:

- Multi-agent orchestration mode will be available in Bob UI
- Existing modes (if any) will continue to function without disruption
- You can start building agents, MCP servers, and orchestration systems
- Bob will have access to watsonx Orchestrate ADK documentation and commands

---

## 🆘 Need Help?

- Check the base mode README for detailed instructions and MCP server setup
- Review the ADK documentation at https://developer.watson-orchestrate.ibm.com/
- Ensure all prerequisites are installed before starting
- Verify your watsonx Orchestrate API credentials are correctly configured
- Test MCP server connections in Bob's MCP settings