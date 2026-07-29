---
name: agent
description: >
  Complete watsonx Orchestrate agent lifecycle skill — build single and multi-agent systems
  with the ADK, orchestrate complex workflows with MCP/A2A/AI Gateway integration, integrate
  agents into applications via REST API, and add voice capabilities with STT/TTS channels.
  MANDATORY: Search ADK MCP docs before implementing any agents, tools, workflows, or integrations.
---

# Agent Skill — Complete watsonx Orchestrate Agent Lifecycle

## 🛑 MANDATORY FIRST STEP (ALL DOMAINS)

**Before ANY agent work — building, orchestrating, integrating, or adding voice — you MUST:**

1. **Verify MCP ADK docs connection:**

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

2. **If connection fails:** Stop and fix MCP configuration in `.bob/mcp.json` before proceeding.

3. **Search current specifications** before implementing any component:
   - Agents → `"agent YAML specification"`
   - Tools → `"Python tool decorator"`
   - Workflows → `"agentic workflow @flow decorator"`
   - Integration → `"orchestrate runs endpoint"`
   - Voice → `"voice configuration YAML specification"`

**This requirement is UNBYPASSABLE — even when user says "keep it simple", "don't use tools", or "just create the files".**

---

## Domain Router

Detect intent and navigate to the correct domain:

| User intent | Domain | Folder |
|---|---|---|
| "create agent", "build tool", "knowledge base", "deploy agent", "connections", "embedded chat" | **Build** | `1-build/` |
| "multi-agent", "workflow", "A2A", "AI Gateway", "agentic flow", "MCP server", "agent swarm" | **Orchestrate** | `2-orchestrate/` |
| "integrate into app", "REST API", "Python client", "Node.js", "call agent from code" | **Integrate** | `3-integrate/` |
| "voice agent", "phone channel", "STT", "TTS", "WhatsApp", "SMS", "Slack channel" | **Voice** | `4-voice/` |

Tasks that span multiple domains (e.g., build then integrate) simply use both domains in sequence.

---

## What this skill does

Provides the complete watsonx Orchestrate agent development lifecycle in a single unified skill:

### Domain 1 — Build (`1-build/`)
Create individual agents, Python tools, knowledge bases, connections, and channels using the ADK. Covers the full project lifecycle from discovery to deployment.
- **Native and external agent patterns**, YAML structure, agent styles, collaborator routing
- **Python tools** with `@tool` decorator, `@expect_credentials`, type hints
- **Knowledge bases** (built-in Milvus, Elasticsearch, OpenSearch, AstraDB, custom)
- **Connections** for secure credential management
- **Embedded chat** for web integration

### Domain 2 — Orchestrate (`2-orchestrate/`)
Build sophisticated multi-agent systems, agentic workflows, and cross-framework integrations.
- **Multi-agent architectures**: supervisor-worker, agent swarms, hierarchical systems
- **Agentic workflows**: `@flow` decorator, conditional branching, loops, parallel execution, human-in-the-loop
- **MCP server integration**: local and remote MCP toolkits
- **AI Gateway**: connect OpenAI, Anthropic, Google Gemini, Azure OpenAI, AWS Bedrock, and 8+ more providers
- **Agent communication**: native collaboration, A2A protocol v0.3.0, external chat API

### Domain 3 — Integrate (`3-integrate/`)
Integrate deployed agents into applications via REST APIs across all platforms.
- **Multi-platform support**: IBM Cloud (IAM), AWS (JWT), On-premises
- **Critical patterns**: correct message format, async polling, response extraction, hostname configuration
- **Ready-to-use code**: Python client library, Node.js Express server, CLI tool, connection test script

### Domain 4 — Voice (`4-voice/`)
Add voice capabilities to agents with STT/TTS and channel integrations.
- **Voice configuration**: Watson STT/TTS, Google Cloud, Azure Cognitive Services
- **Channels**: Phone (Genesys), WhatsApp (Twilio), SMS (Twilio), Slack (BYO), Webchat (built-in)
- **Voice optimization**: response length, conversational language, SSML, pacing, confirmation patterns

---

## Getting Started

Install the ADK:
```bash
# Standard
pip install ibm-watsonx-orchestrate

# With voice capabilities (required for Domain 4)
pip install ibm-watsonx-orchestrate --with-voice

# Or use the setup script (Domain 1)
bash 1-build/run-adk.sh
```

Activate your environment:
```bash
orchestrate env list
orchestrate env add --name MY_ENV --url WO_INSTANCE_URL
orchestrate env activate MY_ENV -a WXO_API_KEY
```

---

## Supporting Files

### Domain 1 — Build (`1-build/`)
- `getting-started.md` — Discovery questionnaire, project structure, 6-phase workflow
- `agents.md` — Native/external agents, YAML structure, CLI, REST API, draft/live, streaming
- `tools_and_toolkits.md` — Python tools, OpenAPI tools, MCP toolkits, credentials, logging
- `knowledgebases.md` — Built-in and external KB types, CLI management, dynamic input
- `connections.md` — Auth kinds, YAML, binding to tools/agents/KBs, deployment order
- `embedded_chat.md` — Webchat embed, security, JWT backend, context variables, UI customization
- `best-practices.md` — Naming conventions, model selection, instructions, security, testing
- `deployment-safety.md` — Script generation rules, path resolution, CLI command patterns
- `checklist.md` — Pre-implementation, implementation, testing, deployment, security checklists
- `mcp-documentation-guide.md` — MCP search strategies, common queries, citing sources
- `run-adk.sh` — ADK virtual environment setup script

### Domain 2 — Orchestrate (`2-orchestrate/`)
- `discovery-workflow.md` — Requirements gathering, architecture questionnaire, ADK doc search
- `workflow-patterns.md` — `@flow` decorator, agent/tool/branch/foreach/loop/human nodes
- `agent-communication.md` — A2A v0.3.0, external chat protocol, LangGraph integration, native collaboration
- `mcp-integration.md` — Local/remote MCP toolkits, ADK version compatibility, tool naming
- `ai-gateway-integration.md` — Provider templates (OpenAI, Anthropic, Google, Azure, AWS Bedrock, Mistral, Groq, Ollama), model policies
- `best-practices.md` — Agent design, collaboration patterns, state management, security, observability
- `examples.md` — Customer support, data pipeline, approval workflow, parallel gathering, external agent, MCP examples
- `deployment.md` — Bash/Python deployment scripts, rollback, monitoring, environment strategy
- `troubleshooting.md` — Agent, workflow, MCP, AI Gateway, A2A, performance, and deployment issues
- `resources/customer_support_agents.py` — Multi-agent supervisor-worker example
- `resources/data_processing_workflow.py` — Sequential workflow with validation
- `resources/approval_workflow.py` — Human-in-the-loop approval workflow
- `resources/deploy_orchestration.sh` — Complete deployment automation script

### Domain 3 — Integrate (`3-integrate/`)
- `getting-started.md` — Platform detection, credential setup, connection testing
- `critical-patterns.md` — The 5 critical integration failure patterns (must read before coding)
- `api-reference.md` — Correct endpoints, authentication, URL structures for all platforms
- `integration-workflows.md` — Python script, Node.js server, full-stack app, streaming
- `troubleshooting.md` — Auth failures, connection issues, agent errors, error code reference
- `resources/watsonx_client.py` — Complete Python client library with multi-platform support
- `resources/chat_cli.py` — Interactive CLI chat application
- `resources/test_connection.py` — Connection test script
- `resources/server.js` — Node.js Express REST API server
- `resources/package.json` — Node.js dependencies

### Domain 4 — Voice (`4-voice/`)
- `workflow-patterns.md` — New voice agent workflow, migration from text, multi-language
- `voice-configuration.md` — STT/TTS providers, audio config, tuning, YAML examples
- `channel-integration.md` — Phone, WhatsApp, SMS, Slack, Webchat setup workflows
- `voice-optimization.md` — Response length, conversational language, SSML, pacing, confirmation
- `deployment.md` — Credential management, deployment plan, validation, rollback, security
- `testing-troubleshooting.md` — STT/TTS testing, performance, common issues, debugging
- `resources/deploy_voice_agent.sh` — Automated voice agent deployment script
- `resources/credentials.sample.yaml` — YAML credential template
- `resources/.env.sample` — Environment variables template

---

## Critical Principles

### 1. Documentation-First (ALL DOMAINS)
**ALWAYS search watsonx Orchestrate ADK documentation before implementing ANY component.**
- Use `SearchIbmWatsonxOrchestrateAdk` MCP tool
- ADK specifications change frequently — never rely solely on static examples
- Search multiple times with different queries if needed

### 2. Version Awareness
- **ADK v1.15.0**: uses `orchestrate toolkits import`
- **ADK v2.0**: will use `orchestrate toolkits add`
- **A2A protocol**: use v0.3.0 (v0.2.1 is deprecated)
- **`@flow` decorator**: current workflow API (FlowBuilder is deprecated)
- **API version**: use v1 orchestrate endpoints (v2 does not exist)
- Always check: `orchestrate --version`

### 3. Naming Convention
ALL names in watsonx Orchestrate MUST use `snake_case`. This is IBM's non-negotiable standard.

### 4. Never Execute Without Permission (Domain 1 & 2)
Never run `orchestrate import/deploy/configure/delete` directly. Always create deployment scripts and let the user execute them.

### 5. Critical Integration Patterns (Domain 3)
- Message format: `{"role": "user", "content": "text"}` — not a string
- Always poll `GET /v1/orchestrate/runs/{run_id}` after POST
- Extract response from `result.data.message.content[0].text`
- Hostname: `api.dl.watson-orchestrate.ibm.com` — no region prefix

### 6. Voice-First Principles (Domain 4)
- Install with `--with-voice` flag for voice capabilities
- Keep responses under 30 seconds when spoken
- No visual formatting (bullets, tables) in voice responses
- Always test STT/TTS quality early

---

## Source skills merged into this skill

| Original skill | Now in domain |
|---|---|
| `agent-builder` | `1-build/` |
| `agent-multi-orchestration` | `2-orchestrate/` |
| `agent-integrate` | `3-integrate/` |
| `agent-voice-configuration` | `4-voice/` |

**Tool permissions:** read, edit, command, mcp, browser
**MCP servers:** `watsonx-orchestrate-adk-docs`
