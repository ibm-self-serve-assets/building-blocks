# 🤖 Multi-Agent Orchestration Mode

A specialized Bob mode for designing, managing, and optimizing distributed AI agent ecosystems using **IBM watsonx Orchestrate ADK**.

## 📋 Overview

This mode provides comprehensive support for building multi-agent systems with:
- **Native and External Agents** (A2A, LangGraph, Salesforce, watsonx AI)
- **MCP Server Integration** (local stdio and remote SSE)
- **Agent-to-Agent Communication** (A2A Protocol v0.3.0)
- **Agentic Workflows** (10+ node types with control structures)
- **Deployment Automation** (Bash and Python scripts)

## 🎯 When to Use This Mode

Use this mode when working with:
- ✅ Multi-agent system design and implementation
- ✅ MCP server integrations (local or remote)
- ✅ Agent-to-Agent (A2A) communication protocols
- ✅ Complex agentic workflows with multiple agents and tools
- ✅ Agent coordination and orchestration issues
- ✅ Security and access control for distributed agents
- ✅ Agent swarms or event-driven architectures
- ✅ Deployment to watsonx Orchestrate environments

## 🚀 Quick Start

### 1. Activate the Mode
```
Switch to "🤖 Multi-Agent Orchestration" mode in Bob
```

### 2. Start a New Project
The mode will automatically:
1. **Ask about existing codebase** - Detect watsonx Orchestrate projects
2. **Run discovery questionnaire** - Gather requirements (10+ questions)
3. **Search ADK documentation** - Fetch relevant patterns from MCP docs
4. **Offer planning phase** - Create detailed `plan.md` if desired
5. **Implement solution** - Build agents, workflows, and integrations
6. **Generate deployment scripts** - Create automated deployment procedures

## 💡 How to Use This Mode

### Getting Started

1. **Switch to the mode** in Bob's mode selector
2. **Describe your goal** - The mode will guide you through the process
3. **Answer the questionnaire** - Provide details about your requirements
4. **Review the plan** - Approve or request changes
5. **Let the mode implement** - Watch as agents and workflows are created
6. **Deploy** - Use generated scripts to deploy to watsonx Orchestrate

### Sample Prompts by Use Case

#### 🆕 Starting a New Multi-Agent Project

**Basic Project Setup:**
```
"I need to build a multi-agent system for customer support with ticket routing and sentiment analysis"
```

**Complex Orchestration:**
```
"Create a multi-agent workflow that processes insurance claims:
- Document extraction agent
- Fraud detection agent
- Risk assessment agent
- Human approval for high-value claims
- Automated payout for low-risk claims"
```

**Agent Swarm:**
```
"Design an agent swarm for market research that can:
- Scrape competitor websites
- Analyze pricing trends
- Generate reports
- Coordinate findings between 5+ agents"
```

#### 🔌 MCP Server Integration

**Local MCP Setup:**
```
"Connect my agents to a local MCP server that provides database access tools"
```

**Remote MCP with Authentication:**
```
"Set up remote MCP server integration with OAuth authentication for our production API"
```

**Multiple MCP Servers:**
```
"I need to connect agents to three MCP servers:
1. Database server (local stdio)
2. External API server (remote SSE with API key)
3. Vector store server (remote with OAuth)"
```

#### 🤝 Agent-to-Agent Communication

**A2A Protocol Setup:**
```
"Implement A2A protocol between my Python agent and an external LangGraph agent"
```

**Multi-Agent Collaboration:**
```
"Create a supervisor agent that coordinates 3 worker agents using A2A protocol:
- Data collection agent
- Analysis agent
- Reporting agent"
```

**Agent Chain:**
```
"Build a sequential agent chain where each agent passes context to the next via A2A"
```

#### 🔄 Workflow Design

**Simple Workflow:**
```
"Create an agentic workflow with:
- Agent node to process input
- Branch node for routing
- Two tool nodes for different actions
- Final agent node to summarize"
```

**Complex Workflow with Loops:**
```
"Design a workflow that:
- Iterates over a list of documents (foreach)
- Processes each with an agent
- Loops until quality threshold is met
- Includes human approval for edge cases"
```

**Event-Driven Workflow:**
```
"Build an event-driven workflow triggered by Kafka messages that orchestrates multiple agents in parallel"
```

#### 🔧 Troubleshooting & Optimization

**Debug Connection Issues:**
```
"My agent can't connect to the remote MCP server - help me debug the authentication"
```

**Performance Optimization:**
```
"My multi-agent workflow is too slow - optimize the agent communication and MCP calls"
```

**Error Handling:**
```
"Add comprehensive error handling to my workflow with retry logic and fallback agents"
```

#### 🚀 Deployment

**Generate Deployment Scripts:**
```
"Create deployment scripts for my multi-agent system with environment setup and health checks"
```

**Production Deployment:**
```
"Generate a production-ready deployment script that:
- Sets up environment variables
- Imports all agents
- Configures MCP servers
- Runs health checks
- Includes rollback procedures"
```

#### 📊 Analysis & Enhancement

**Analyze Existing Project:**
```
"Analyze my existing watsonx Orchestrate project and suggest improvements for agent coordination"
```

**Add New Capabilities:**
```
"Add a new fraud detection agent to my existing customer support workflow"
```

**Refactor for Scale:**
```
"Refactor my single-agent system into a multi-agent architecture that can handle 10x traffic"
```

### 🎯 Pro Tips

#### Be Specific About Requirements
❌ **Vague:** "I need some agents"
✅ **Specific:** "I need 3 agents: one for data extraction, one for validation, and one for storage, coordinated by a supervisor agent"

#### Mention Integration Points
❌ **Missing context:** "Connect to MCP server"
✅ **Clear context:** "Connect to local MCP server at stdio with database tools, and remote MCP at https://api.example.com with OAuth"

#### Describe Data Flow
❌ **Unclear:** "Agents should work together"
✅ **Clear:** "Agent A processes input and passes results to Agent B via A2A protocol, which then triggers Agent C in parallel"

#### Specify Security Needs
❌ **Overlooked:** "Deploy the agents"
✅ **Comprehensive:** "Deploy with RBAC, OBO flow for user identity, and TLS for remote MCP connections"

### 🔄 Iterative Development

The mode supports iterative development:

1. **Start simple:** "Create a basic agent with one tool"
2. **Add complexity:** "Add MCP integration to the agent"
3. **Expand:** "Create a workflow that uses this agent"
4. **Enhance:** "Add error handling and retry logic"
5. **Scale:** "Convert to multi-agent with A2A communication"

### 📝 Planning Phase

When the mode offers to create a `plan.md`:
- ✅ **Say yes** for complex projects (3+ agents, multiple MCP servers)
- ✅ **Say yes** if you want to review architecture before implementation
- ⚠️ **Skip** for simple single-agent projects or quick prototypes

### 🎓 Learning Mode

Use the mode to learn ADK concepts:
```
"Explain the difference between native agents and A2A agents with examples"
"Show me how to implement a foreach loop in an agentic workflow"
"What are the best practices for MCP server authentication?"
```

The mode will search ADK documentation and provide detailed explanations!


## 📚 Mode Structure

### Instruction Files

| File | Purpose |
|------|---------|
| `1_discovery.xml` | Initial questionnaire, codebase analysis, and MCP docs search |
| `2_workflow.xml` | Agentic workflow patterns with 10+ node types |
| `3_best_practices.xml` | Multi-agent orchestration best practices |
| `4_mcp_integration.xml` | MCP server integration (local stdio, remote SSE) |
| `5_agent_communication.xml` | A2A Protocol v0.3.0 and agent communication |
| `6_examples.xml` | Complete orchestration examples and templates |
| `7_deployment.xml` | Deployment scripts (Bash & Python) and procedures |
| `8_troubleshooting.xml` | Common issues and debugging strategies |

## 🔧 Core Capabilities

### 🔍 Discovery & Analysis
- Detect existing watsonx Orchestrate projects
- Run comprehensive requirements questionnaire
- **Automatically search ADK MCP documentation** for relevant patterns
- Analyze agent configurations and dependencies
- Map existing workflows and communication patterns

### 🏗️ Architecture & Design
- Design multi-agent architectures (supervisor-worker, peer-to-peer, swarms)
- Create agentic workflows with control structures
- Plan MCP server integrations (local and remote)
- Design A2A communication patterns
- Generate detailed planning documentation

### 💻 Implementation

#### Agent Types
- **Native Agents**: Python-based agents with custom tools
- **External Agents**: 
  - A2A Protocol agents
  - LangGraph agents
  - Salesforce agents
  - watsonx AI agents
  - External chat agents

#### Workflow Node Types
- **Agent**: Execute agent tasks
- **Tool**: Call MCP or custom tools
- **Flow**: Reusable subworkflows
- **Branch**: Conditional routing
- **Foreach**: Parallel iteration
- **Loop**: Iterative processing
- **Decisions**: Human-in-the-loop
- **Prompt**: LLM interactions
- **DocProc**: Document processing
- **Webhook**: External integrations

#### MCP Integration
- **Local MCP Servers**: Stdio-based connections
- **Remote MCP Servers**: SSE over HTTP/HTTPS
- **Authentication**: API keys, OAuth, custom auth
- **Tool Registration**: Connect MCP tools to agents
- **Resource Access**: Vector stores, documents, databases

#### A2A Communication
- **Protocol**: JSON-RPC 2.0 over HTTP
- **Chat API**: `/v1/chat/completions` endpoint
- **Completion API**: `/v1/completions` endpoint
- **Context Sharing**: Pass state between agents
- **Message Patterns**: Direct, broadcast, request-response

### 🚀 Deployment
- Generate Bash deployment scripts (Linux/macOS)
- Generate Python deployment scripts (cross-platform)
- Automated environment setup
- Agent import and registration
- Health checks and validation
- Post-deployment verification

### 🔍 Troubleshooting
- Debug MCP connection issues
- Resolve A2A communication failures
- Analyze workflow execution errors
- Fix authentication problems
- Optimize performance and timeouts

## 🛠️ MCP Integration

### ADK Documentation Server
The mode automatically connects to the **watsonx-orchestrate-adk-docs** MCP server to:
- Search ADK documentation for relevant patterns
- Retrieve agent type specifications
- Find workflow examples
- Locate MCP integration guides
- Research A2A protocol details

### MCP Tools Used
1. **`search_ibm_watsonx_orchestrate_adk`** - Search documentation
2. **`query_docs_filesystem_ibm_watsonx_orchestrate_adk`** - Retrieve full pages

### Configuration
Ensure your `mcp.json` includes:
```json
{
  "mcpServers": {
    "watsonx-orchestrate-adk-docs": {
      "command": "npx",
      "args": ["-y", "@ibm/watsonx-orchestrate-adk-docs-mcp-server"],
      "transport": "streamable-http"
    }
  }
}
```

## 📖 Workflow Example

### Typical Session Flow

```
1. User: "I need to build a multi-agent system for customer support"

2. Mode: Asks about existing codebase
   → Detects no existing project

3. Mode: Runs discovery questionnaire
   → Agent types needed?
   → Workflow complexity?
   → MCP servers required?
   → Security requirements?
   → Deployment target?

4. Mode: Searches ADK documentation
   → Finds relevant agent patterns
   → Locates workflow examples
   → Retrieves A2A protocol specs

5. Mode: Offers to create plan.md
   → User confirms
   → Generates detailed plan with architecture

6. Mode: Implements solution
   → Creates agent configurations
   → Builds agentic workflows
   → Sets up MCP integrations
   → Implements A2A communication

7. Mode: Generates deployment scripts
   → Creates deploy.sh with health checks
   → Includes environment setup
   → Adds agent import commands
```

## 🎨 Best Practices

### Agent Design
- ✅ Use clear, descriptive agent names
- ✅ Define stable agent contracts (inputs/outputs)
- ✅ Implement comprehensive error handling
- ✅ Add logging and observability
- ✅ Version agents for compatibility

### Workflow Design
- ✅ Keep workflows modular and reusable
- ✅ Use Flow nodes for common patterns
- ✅ Implement proper error handling at each node
- ✅ Add human-in-the-loop for critical decisions
- ✅ Document workflow purpose and data flow

### MCP Integration
- ✅ Use local MCP for development, remote for production
- ✅ Implement proper authentication and authorization
- ✅ Handle MCP server failures gracefully
- ✅ Cache MCP responses when appropriate
- ✅ Monitor MCP server health

### Security
- ✅ Implement RBAC with context variables
- ✅ Use OBO (on-behalf-of) flow for user identity
- ✅ Add agent guardrails for input/output validation
- ✅ Secure remote MCP with TLS/SSL
- ✅ Rotate credentials regularly

## 📁 File Patterns

The mode can edit files matching these patterns:
- `agents/**/*` - Agent configurations
- `orchestration/**/*` - Orchestration files
- `workflows/**/*` - Workflow definitions
- `mcp/**/*` - MCP configurations
- `*agent*.(ts|js|py|yaml|yml|json)` - Agent files
- `*flow*.(ts|js|py|yaml|yml|json)` - Flow files
- `*.mcp.json` - MCP configuration files
- `deploy*.(sh|bash|py)` - Deployment scripts
- `plan.md` - Planning documents

## 🔗 Resources

### Official Documentation
- [IBM watsonx Orchestrate ADK](https://www.ibm.com/docs/en/watsonx/watson-orchestrate)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Agent-to-Agent Protocol](https://github.com/IBM/agent-to-agent-protocol)

### Related Modes
- **💻 Code Mode**: General code editing
- **🛠️ Advanced Mode**: MCP server operations
- **✍️ Mode Writer**: Creating custom modes

## 🤝 Contributing

This mode is part of the Bob custom modes system. To modify:
1. Edit `.bob/custom_modes.yaml` for mode configuration
2. Update instruction files in `.bob/rules-multi-agent-orchestration/`
3. Test with real watsonx Orchestrate projects
4. Document changes in this README

## 📝 Version History

- **v1.0.0** (2026-04-15)
  - Initial release
  - 8 instruction files covering full lifecycle
  - MCP ADK docs integration
  - Discovery-first workflow
  - Deployment automation
  - Comprehensive troubleshooting guide

## 📧 Support

For issues or questions:
1. Check the troubleshooting guide (`8_troubleshooting.xml`)
2. Review ADK documentation via MCP search
3. Consult the examples file (`6_examples.xml`)
4. Ask the mode for specific guidance

---

**Mode Slug**: `multi-agent-orchestration`  
**Mode Name**: 🤖 Multi-Agent Orchestration  
**Source**: Project Custom Mode  
**Last Updated**: 2026-04-15