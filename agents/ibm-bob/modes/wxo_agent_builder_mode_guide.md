# watsonx Orchestrate Agent Builder Mode - Guide

## Why Use This Custom Mode?

The **wxO Agent Builder** mode transforms IBM Bob from a general-purpose coding assistant into an expert watsonx Orchestrate architect. Instead of asking Bob generic questions and getting generic answers, this mode gives Bob deep, contextual knowledge about watsonx Orchestrate best practices, patterns, and pitfalls.

### The Problem with Default Code Mode

When using Bob's default Code mode for watsonx Orchestrate development:
- ❌ Bob doesn't know watsonx Orchestrate-specific patterns and conventions
- ❌ You have to repeatedly explain concepts like agent styles, tool decorators, and MCP integration
- ❌ Bob might suggest approaches that work generally but aren't optimal for watsonx Orchestrate
- ❌ You spend time correcting Bob's suggestions to align with ADK best practices
- ❌ No built-in knowledge of when to use agents vs tools vs workflows

### What This Mode Provides

With the wxO Agent Builder mode:
- ✅ **Expert Context**: Bob understands watsonx Orchestrate architecture, ADK patterns, and best practices
- ✅ **Optimized Decisions**: Automatically selects appropriate LLMs, agent styles, and architectures
- ✅ **Production-Ready Code**: Generates code following watsonx Orchestrate conventions and security practices
- ✅ **Integrated Workflow**: Direct access to ADK CLI commands and documentation via MCP servers
- ✅ **Time Savings**: No need to explain watsonx Orchestrate concepts repeatedly


## Key Advantages

### 1. Built-in Best Practices

The mode includes expert knowledge about:
- When to use Granite vs Llama models
- How to write effective agent instructions
- Tool vs collaborator decision-making
- Security patterns for credentials
- Performance optimization strategies

### 2. Integrated Development Workflow

With MCP servers configured, Bob can:
- Query watsonx Orchestrate documentation in real-time
- Execute ADK CLI commands directly
- List existing agents, tools, and connections
- Export and import artifacts
- Test and validate configurations

### 3. Production-Ready Output

Every suggestion follows:
- watsonx Orchestrate naming conventions
- Proper error handling patterns
- Security best practices
- Type safety and validation
- Documentation standards

### 4. Context Retention

Bob remembers:
- Your project's agent architecture
- Previously created tools and agents
- Credential management patterns
- Your team's conventions

## Installation

### Prerequisites

1. **Install watsonx Orchestrate ADK:**
   ```bash
   pip install ibm-watsonx-orchestrate
   ```

2. **Configure MCP Servers:**
   - Copy `base-mode/mcp_watsonx_orchestrate.json` configuration
   - Update `WXO_MCP_WORKING_DIRECTORY` to your project path
   - Add MCP servers to IBM Bob (Project level recommended)

3. **Activate Environment:**
   ```bash
   orchestrate env activate --name your_env_name
   ```

### Setup Steps

1. Copy contents of `wxo_agent_builder_mode.yml`
2. Create/edit `.bobmodes` in your workspace root
3. Paste the mode configuration
4. Reload IBM Bob (`Cmd/Ctrl + Shift + P` → "Reload Window")
5. Select "🤖 wxO Agent Builder" from mode selector

## Usage Patterns

### Pattern 1: Rapid Agent Development

```
"Create a sales agent that can search products, check inventory, and create quotes"
```

Bob will:
- Design the agent architecture
- Select optimal LLM and style
- Write comprehensive instructions
- Create or identify required tools
- Generate complete YAML specification
- Provide import commands

### Pattern 2: Tool Creation

```
"Build a Python tool that fetches customer data from our CRM API"
```

Bob will:
- Create tool with @tool decorator
- Add proper type hints and schema
- Implement credential management
- Add error handling
- Create requirements.txt
- Provide import and testing commands

### Pattern 3: Multi-Agent Systems

```
"Design a supervisor agent that routes to sales, support, and operations agents"
```

Bob will:
- Design supervisor-worker architecture
- Create supervisor with routing logic
- Define specialized worker agents
- Optimize descriptions for routing
- Generate all agent specifications
- Provide integration testing approach

### Pattern 4: Workflow Design

```
"Create an agentic workflow for employee onboarding with approvals"
```

Bob will:
- Design workflow architecture
- Identify required nodes and edges
- Implement control structures
- Add human-in-the-loop steps
- Configure async execution
- Provide testing strategy

## When to Use This Mode

**Use wxO Agent Builder Mode when:**
- Building or modifying watsonx Orchestrate agents
- Creating Python tools with @tool decorator
- Integrating MCP toolkits
- Designing agentic workflows
- Architecting multi-agent systems
- Optimizing agent performance
- Implementing security patterns

**Use Default Code Mode when:**
- Writing general Python/JavaScript code
- Working on non-watsonx Orchestrate projects
- Debugging unrelated issues
- General programming tasks

## Learning Resources

This mode complements (not replaces) official documentation:

- **[watsonx Orchestrate ADK Documentation](https://developer.watson-orchestrate.ibm.com/)**: Complete API reference and guides
- **[Agent Development Guide](https://developer.watson-orchestrate.ibm.com/agents/overview)**: Agent concepts and patterns
- **[Tool Development Guide](https://developer.watson-orchestrate.ibm.com/tools/overview)**: Tool creation and management
- **[MCP Integration Guide](https://developer.watson-orchestrate.ibm.com/tools/toolkits/overview)**: MCP toolkit integration

The mode uses this documentation via MCP servers to provide contextual, up-to-date guidance.

## Tips for Maximum Effectiveness

1. **Be Specific**: Provide clear requirements about what the agent/tool should do
2. **Iterate**: Start simple, then ask Bob to enhance with additional features
3. **Leverage MCP**: Ask Bob to check existing agents/tools before creating new ones
4. **Test Incrementally**: Build and test tools before integrating into agents
5. **Version Control**: Ask Bob to export artifacts for Git after creation

## Troubleshooting

### Mode Not Appearing
- Verify `.bobmodes` file is in workspace root
- Check YAML syntax is valid
- Reload IBM Bob window

### MCP Servers Not Working
- Verify ADK is installed: `pip show ibm-watsonx-orchestrate`
- Check `WXO_MCP_WORKING_DIRECTORY` is set correctly
- Ensure environment is activated: `orchestrate env list`
- Review MCP server logs in Bob's output panel

### Bob Doesn't Seem to Know watsonx Orchestrate
- Verify you've selected "🤖 wxO Agent Builder" mode
- Check MCP servers are enabled and connected
- Try asking Bob to query the documentation: "What are agent styles?"

## Getting Help

- **Within the mode**: Ask Bob specific questions about watsonx Orchestrate concepts
- **Official docs**: Refer to [developer.watson-orchestrate.ibm.com](https://developer.watson-orchestrate.ibm.com/)
- **MCP servers**: Use the documentation query tool for real-time answers

## Summary

The wxO Agent Builder mode is your expert pair programmer for watsonx Orchestrate development. It saves time, reduces errors, and ensures you're following best practices without having to constantly reference documentation or explain concepts. Think of it as having a watsonx Orchestrate expert sitting next to you, ready to help with every aspect of agent development.
