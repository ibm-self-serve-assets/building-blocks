---
name: agent-builder
description: Build and deploy multi-agent systems with tools (MCP servers) using watsonx Orchestrate's Agent Development Kit (ADK), CLI and REST API. MANDATORY FIRST STEP - Verify MCP ADK docs connection and search for current specifications before creating ANY agents, tools, or configurations.
---

## 🛑 STOP - MANDATORY FIRST STEPS (DO NOT SKIP)

**Before creating ANY agents, tools, or configurations, you MUST complete these steps in order:**

### Step 1: Verify MCP Connection (REQUIRED)
Test the watsonx-orchestrate-adk-docs MCP server connection:

```xml
<use_mcp_tool>
<server_name>watsonx-orchestrate-adk-docs</server_name>
<tool_name>SearchIbmWatsonxOrchestrateAdk</tool_name>
<arguments>
{
  "query": "agent YAML specification"
}
</arguments>
</use_mcp_tool>
```

**If connection fails:** Stop and fix MCP configuration before proceeding.

### Step 2: Search Current Specifications (REQUIRED)
Before creating agents, search for:
- "agent YAML specification" - Get current structure
- "agent model selection" - Verify model names
- "agent collaborators" - Check collaborator syntax

**Why this cannot be skipped:**
- Agent specifications change frequently
- Model names and formats may be different
- Field names and requirements may have changed
- Using outdated syntax will cause deployment failures

### Step 3: Verify Findings (REQUIRED)
Confirm you have:
- ✅ Current agent YAML structure
- ✅ Valid model names and formats
- ✅ Correct field names (name, description, instructions, model, etc.)
- ✅ Proper collaborator syntax

**Only after completing Steps 1-3 should you proceed with creating agent files.**

---

## IBM watsonx Orchestrate
IBM watsonx Orchestrate (WxO) supports building, orchestrating, deploying and governing AI agents. The watsonx Orchestrate [Agent Development Kit (ADK)](https://developer.watson-orchestrate.ibm.com) gives developers a pro-code path for creating agents, tools, knowledge bases, and integrations using a Python library, CLI and REST APIs. Together, watsonx Orchestrate and the ADK let teams move from local development and testing to deployment in watsonx Orchestrate, while also connecting external agents, APIs, and frameworks into a governed enterprise agent ecosystem.

## ⚠️ CRITICAL: First Steps After Skill Activation

**Before starting ANY agent development work, you MUST:**

### 1. Verify MCP ADK Documentation Connection

Test that the watsonx-orchestrate-adk-docs MCP server is accessible:

```xml
<use_mcp_tool>
<server_name>watsonx-orchestrate-adk-docs</server_name>
<tool_name>SearchIbmWatsonxOrchestrateAdk</tool_name>
<arguments>
{
  "query": "agent development"
}
</arguments>
</use_mcp_tool>
```

**If the connection fails:**
- Check MCP server configuration in `.bob/mcp.json`
- Verify server is running and accessible
- Confirm authentication credentials are valid
- Do NOT proceed with implementation until connection is working

### 2. Search MCP Docs Before ANY Implementation

**MANDATORY AND UNBYPASSABLE:** Before creating agents, tools, or configurations, you MUST search the MCP documentation for:
- Latest specifications and syntax
- Current parameters and field names
- Best practices and patterns
- Working code examples

**This requirement applies even when:**
- User says "don't use tools" (they mean agent tools, not MCP search)
- User says "keep it simple" (simple still requires correct syntax)
- User says "just create the files" (files must match current specs)
- Time is limited (incorrect files waste more time than searching)

**Why this cannot be skipped:**
- ADK specifications change frequently
- Static examples may be outdated
- Documentation contains required fields not in examples
- Ensures generated code matches current ADK requirements

## Getting Started
Even if you'll connect to Orchestrate via the REST API, you'll need to use the ADK when building, deploying, and testing your agents. Start by installing the `ibm-watsonx-orchestrate` Python library, which also installs the `orchestrate` executable.

Execute the following script to install `ibm-watsonx-orchestrate` into a virtual python environment called `ai-agent-builder`

```bash
# Make the script executable (first time only)
chmod +x run-adk.sh
bash run-adk.sh
```

### Using the orchestrate CLI executable
The best way to learn about the `orchestrate` executable's latest capabilities is to run the help command:

```bash
orchestrate --help
```

### Activate your Orchestrate environment
To work with agents, tools and connections, your Orchestrate environment must first be activated.  Check your local .env for the required variables.

```bash
# always ensure an environment is active
orchestrate env list 

# Create a new environment if needed.  
orchestrate env add --name WO_ADK_ENVIRONMENT_NAME --url WO_INSTANCE_URL

# Activate environment if needed. Always pass the WXO_API_KEY to ensure non-blocking activation.
orchestrate env activate ORCHESTRATE_ENVIRONMENT_NAME -a WXO_API_KEY
```

## Workflow Guidance

The following workflow files guide you through the agent development process step-by-step:

- [Getting Started](getting-started.md)
  Discovery questionnaire, project structure setup, planning workflow, and transition to implementation.

- [MCP Documentation Guide](mcp-documentation-guide.md) ⚠️ **READ THIS FIRST**
  MANDATORY: How to search and use the watsonx-orchestrate-adk-docs MCP server for up-to-date technical information. This is REQUIRED before any implementation work.

- [Best Practices](best-practices.md)
  Critical naming conventions, model selection, security essentials, and performance guidelines.

- [Deployment Safety](deployment-safety.md)
  Safe deployment automation practices, CLI command patterns, path resolution, and error prevention.

- [Quality Checklist](checklist.md)
  Comprehensive checklist for verifying agent development quality and completeness.

## API Reference

The following documents provide detailed, task-focused guidance for designing, building, deploying, and integrating watsonx Orchestrate agents and their supporting assets.

- [Building and deploying agents](agents.md)  
  Defines native and external agent patterns, YAML structure, agent styles, collaborator routing, deployment order, draft/live promotion, REST API access, and agent runtime debugging.

- [Building and deploying tools and toolkits](tools_and_toolkits.md)  
  Covers Python tools, OpenAPI tools, MCP toolkits, Python toolkits, import/update/remove commands, naming conventions, packaging structure, and how tools are attached to agents.

- [Building and deploying knowledge bases](knowledgebases.md)  
  Explains built-in and external knowledge bases, document ingestion, vector index configuration, external search provider patterns, import/status/export/remove commands, and how agents reference knowledge bases.

- [Configuring connections](connections.md)  
  Covers app IDs, draft/live credentials, connection configuration, credential binding, and how connections are associated with tools, toolkits, knowledge bases, and external agents.

- [Embedding chat in applications](embedded_chat.md)  
  Explains how to expose deployed agents through embedded web chat, generate embed code, use context variables, handle events, secure backend-issued tokens, customize the UI, and decide when to use embedded chat versus REST APIs.
