# Discovery and Requirements Gathering

## Overview

Start every multi-agent orchestration project with this discovery workflow to gather comprehensive requirements before implementation. This ensures you understand the full scope and can design the optimal architecture.

## Phase 1: Initial Assessment

### Step 1: Understand Current State

Ask about existing codebase:
- Do you have an existing watsonx Orchestrate agent codebase?
- Are you enhancing existing agents or starting fresh?
- What's the current project structure?

If existing code exists, analyze:
- Agent configurations (*.yaml, *.json)
- Workflow definitions (flow*.py, *_flow.py)
- MCP server configurations (mcp.json)
- A2A protocol implementations
- Existing tools and connections

### Step 2: Search ADK Documentation

**MANDATORY**: Before proceeding, search ADK documentation for relevant patterns:

```
Use MCP tool: search_ibm_watsonx_orchestrate_adk
Query based on requirements (e.g., "MCP toolkit integration", "agentic workflow")
```

This ensures you have:
- Latest syntax and working examples
- Current API references
- Best practices for the specific implementation

### Step 3: Present Findings

Provide clear summary:
- Identified agents and their roles
- Existing workflows and patterns
- MCP integrations found
- Potential issues or improvements
- Recommendations for next steps

## Phase 2: Comprehensive Questionnaire

Ask questions one at a time or in logical groups. Provide 2-4 specific suggestions for each.

### Project Type
- New multi-agent system from scratch?
- Enhancing existing agents?
- Troubleshooting current implementation?
- Migrating from another platform?

### Agent Architecture
- Single agent with multiple tools?
- Multiple specialized agents (supervisor-worker)?
- Agent swarm with dynamic collaboration?
- Hierarchical agent system?

How many agents? What are their responsibilities?

### Integration Requirements
- Local MCP servers for tools?
- Remote MCP servers for distributed capabilities?
- External agents via A2A protocol (LangGraph, CrewAI, BeeAI)?
- External agents via Chat Completions API?
- watsonx AI Agent Builder integration?
- Salesforce AgentForce integration?
- Custom API integrations?

### Communication Patterns
- Native collaboration (agents as collaborators)?
- Agent-to-Agent (A2A) Protocol v0.3.0?
- External Chat API (OpenAI-style)?
- Agentic workflows (orchestrated communication)?
- Event-driven messaging (Apache Kafka)?

### Workflow Complexity
- Simple sequential workflows?
- Conditional branching with decision logic?
- Parallel execution of multiple agents/tools?
- Iterative workflows with loops?
- Long-running workflows (hours to days)?
- Human-in-the-loop with approvals?

Do you need:
- Scheduled workflow execution?
- Large data set handling with compression?

### Security Requirements
- API Key authentication for MCP servers?
- Bearer Token authentication?
- Role-Based Access Control (RBAC)?
- On-Behalf-Of (OBO) flow for user impersonation?
- Agent guardrails and security plugins?
- Development only (no special security)?

### Deployment Target
- Local development (Developer Edition)?
- Remote watsonx Orchestrate environment?
- Production instance?
- IBM Code Engine or other cloud platform?

Do you have environment-specific configurations (dev, staging, prod)?

### Performance Requirements
- Synchronous execution (wait for completion)?
- Asynchronous execution with status polling?
- Low latency (sub-second responses)?
- High throughput (many concurrent requests)?
- Long-running tasks (minutes to hours)?

### Additional Requirements
- Observability and monitoring capabilities?
- Specific LLM models to use?
- Multi-language support?
- Compliance or regulatory requirements?

## Phase 3: Documentation Search

Proactively search ADK documentation based on gathered requirements:

### Search Strategy

**Identify key search terms:**
- A2A protocol → "Agent-to-Agent A2A protocol"
- Workflows → "agentic workflow" + specific node types
- MCP integration → "MCP server integration"
- Agent swarm → "agent swarm pattern"

**Use MCP tools:**
```
search_ibm_watsonx_orchestrate_adk: Search for relevant topics
query_docs_filesystem_ibm_watsonx_orchestrate_adk: Retrieve full pages
```

**Synthesize findings:**
Present relevant patterns, code examples, and best practices that apply to the user's requirements.

### Common Search Topics

**Agent Types:**
- native agents
- external agents
- agent collaboration

**Workflows:**
- agentic workflow
- flow nodes
- branch foreach loop

**MCP Integration:**
- MCP server
- remote MCP
- MCP workflows

**A2A Protocol:**
- Agent-to-Agent A2A
- A2A protocol
- external agents

**Security:**
- RBAC context variables
- authentication
- agent guardrails

## Phase 4: Requirements Summary

Present comprehensive summary:

### Project Overview
- Project type: [new/enhancement/troubleshooting]
- Agent architecture: [single/multi/swarm]
- Number of agents: [count]

### Technical Requirements
- Integration needs: [MCP/A2A/external APIs]
- Communication patterns: [native/A2A/external_chat]
- Workflow complexity: [simple/complex/long-running]
- Execution mode: [sync/async]

### Security and Deployment
- Authentication: [API Key/Bearer Token/RBAC]
- Deployment target: [local/remote/production]
- Environment configs: [yes/no]

### Relevant Patterns
Based on ADK documentation search:
- [List relevant patterns found]
- [List applicable examples]
- [List best practices to follow]

### Planning Preference

Ask how to proceed:
- Create detailed plan.md file first with architecture and design?
- Proceed directly to implementation based on requirements?
- Review and refine requirements before deciding?

## Important Notes

- **ALWAYS start with Phase 1** when beginning a new task
- **Use ask_followup_question** for all questionnaire interactions
- **Provide 2-4 specific suggestions** for each question
- **Proactively search ADK documentation** - don't wait for user to ask
- **Keep questions focused** - avoid overwhelming the user
- **Provide examples** if user is unsure about any requirement