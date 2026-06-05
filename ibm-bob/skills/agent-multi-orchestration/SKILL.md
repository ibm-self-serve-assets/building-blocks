---
name: multi-agent-orchestration
description: Build multi-agent systems with watsonx Orchestrate including agentic workflows, MCP integration, AI Gateway model routing, and agent communication patterns. MANDATORY - Search MCP ADK docs for current specifications before implementing any workflows, agents, or integrations.
---

# Multi-Agent Orchestration Skill

## 🛑 MANDATORY FIRST STEP

**Before implementing ANY multi-agent system, workflow, or integration:**

1. **Verify MCP ADK docs connection:**
```xml
<use_mcp_tool>
<server_name>watsonx-orchestrate-adk-docs</server_name>
<tool_name>SearchIbmWatsonxOrchestrateAdk</tool_name>
<arguments>
{
  "query": "agentic workflow @flow decorator"
}
</arguments>
</use_mcp_tool>
```

2. **Search for current specifications:**
   - "agentic workflow @flow decorator" - Get latest workflow API
   - "multi-agent patterns" - Check current architecture patterns
   - "MCP toolkit integration" - Verify MCP connection syntax

**This requirement applies even if user says "don't use tools" or "keep it simple"**

## What this skill does

Provides comprehensive guidance for building sophisticated multi-agent systems using IBM watsonx Orchestrate. Covers the complete lifecycle from discovery and planning through implementation, testing, and deployment. Includes:

- **Multi-agent architectures**: Supervisor-worker patterns, agent swarms, hierarchical systems
- **AI Gateway integration**: Connect third-party LLM models (OpenAI, Anthropic, Google, Azure, AWS Bedrock)
- **Agentic workflows**: Build complex workflows with conditional logic, loops, parallel execution
- **MCP server integration**: Connect local and remote MCP toolkits for extended capabilities
- **Agent communication**: Native collaboration, A2A protocol, external agent integration
- **Production deployment**: Scripts, monitoring, rollback procedures

## When to use it

Use this skill when you need to:

- **Design multi-agent systems** with multiple specialized agents working together
- **Integrate third-party LLM models** into watsonx Orchestrate via AI Gateway
- **Build agentic workflows** with complex orchestration logic
- **Connect MCP servers** for tools and resources
- **Enable agent-to-agent communication** using A2A protocol or native collaboration
- **Deploy multi-agent systems** to production environments
- **Troubleshoot** multi-agent or MCP integration issues

## How to work with this skill

<Steps>
<Step>
Start with discovery workflow in `discovery-workflow.md` to gather requirements and understand project scope.
</Step>
<Step>
For AI Gateway model integration, follow `ai-gateway-integration.md` for provider-specific setup and configuration.
</Step>
<Step>
Build agentic workflows using patterns from `workflow-patterns.md` with @flow decorator and node types.
</Step>
<Step>
Integrate MCP servers following `mcp-integration.md` for local or remote toolkit setup.
</Step>
<Step>
Configure agent communication using `agent-communication.md` for A2A protocol or native collaboration.
</Step>
<Step>
Apply best practices from `best-practices.md` throughout development.
</Step>
<Step>
Use complete examples from `examples.md` as templates for common patterns.
</Step>
<Step>
Deploy using scripts from `deployment.md` with proper testing and rollback procedures.
</Step>
<Step>
Troubleshoot issues using `troubleshooting.md` comprehensive guide.
</Step>
</Steps>

## Supporting files

### Core Workflows
- `discovery-workflow.md` - Requirements gathering and project planning
- `workflow-patterns.md` - Agentic workflow implementation with @flow decorator
- `agent-communication.md` - A2A protocol and native collaboration patterns
- `mcp-integration.md` - MCP server integration (local and remote)
- `ai-gateway-integration.md` - Third-party LLM model integration via AI Gateway

### Reference Materials
- `best-practices.md` - Design principles, security, performance optimization
- `examples.md` - Complete end-to-end implementation examples
- `deployment.md` - Production deployment scripts and procedures
- `troubleshooting.md` - Comprehensive troubleshooting guide

### Code Resources
- `resources/` - Reusable Python code examples and deployment scripts
  - `customer_support_agents.py` - Multi-agent supervisor-worker example
  - `data_processing_workflow.py` - Sequential workflow with validation
  - `approval_workflow.py` - Human-in-the-loop approval workflow
  - `deploy_orchestration.sh` - Complete deployment automation script
  - `README.md` - Usage instructions for all resources

## Source mode details

This skill combines content from two related modes:
- **🤖 Multi-Agent Orchestration** (multi-agent-orchestration) - Multi-agent systems, workflows, MCP
- **🌉 Agent Model Gateway** (agent-model-gateway) - Third-party LLM model integration

**Tool permissions:** read, edit, command, mcp, browser  
**MCP servers:** watsonx-orchestrate-adk-docs

## Critical principles

### Documentation-First Approach
**ALWAYS search watsonx Orchestrate ADK documentation before implementing:**
- Use `search_ibm_watsonx_orchestrate_adk` MCP tool
- Get latest syntax, examples, and best practices
- Never rely solely on static examples - verify against current docs

### API Version Awareness
- Current: ADK v1.15.0 uses `orchestrate toolkits import`
- Future: ADK v2.0 will use `orchestrate toolkits add`
- Always check version: `orchestrate --version`

### Key Patterns
- **@flow decorator**: Current workflow API (FlowBuilder is deprecated)
- **MCP tool naming**: Always use `toolkit:tool` format
- **A2A protocol**: Use version 0.3.0 (0.2.1 is deprecated)

## Skill relationships

This skill works in conjunction with other watsonx Orchestrate skills:

- **agent-builder**: Use for creating individual agents, tools, and knowledge bases
  - This skill builds on agent-builder concepts
  - Refer to agent-builder for agent creation fundamentals
  - Use agent-builder for MCP server setup and tool configuration

- **agent-integrate**: Use for REST API integration with watsonx Orchestrate
  - Complements this skill for external system integration
  - Use when building applications that consume watsonx agents

- **multi-agent-orchestration** (this skill): Use for coordinating multiple agents
  - Focuses on multi-agent patterns and workflows
  - Covers AI Gateway for third-party LLM integration
  - Handles A2A protocol for external agent communication

## Additional notes

This skill requires Advanced mode to access all necessary tools including MCP and browser capabilities. The skill emphasizes documentation-first approach - always search ADK docs before implementation to ensure current syntax and best practices.

For AI Gateway model integration, this skill covers 12+ providers including OpenAI, Anthropic, Google Gemini, Azure OpenAI, AWS Bedrock, Mistral, Groq, Ollama, and watsonx.ai.

**Code examples in `resources/` folder** demonstrate complete implementations that can be customized for your use case. All examples rely on agent-builder fundamentals for agent creation and configuration.