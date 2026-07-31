# Agent Skill

The **`agent`** skill is your end-to-end companion for building production-ready AI agents on IBM watsonx Orchestrate. It covers the full agent lifecycle — from creating individual agents and tools, to orchestrating complex multi-agent systems, to integrating agents into applications via REST API, to enabling voice interactions across phone, messaging, and chat channels. Everything you need to design, build, deploy, and operate watsonx Orchestrate agents lives in one place, organized into four progressive domains.

## Domains

| Domain | Folder | What it covers |
|---|---|---|
| **1 — Build** | [`1-build/`](./1-build/) | Agents, tools, knowledge bases, connections, embedded chat |
| **2 — Orchestrate** | [`2-orchestrate/`](./2-orchestrate/) | Multi-agent systems, workflows, AI Gateway, MCP, A2A protocol |
| **3 — Integrate** | [`3-integrate/`](./3-integrate/) | REST API integration into applications (Python, Node.js) |
| **4 — Voice** | [`4-voice/`](./4-voice/) | Voice agents, STT/TTS, phone/messaging/Slack channels |

## Directory Structure

```
agent/
├── SKILL.md                        ← Unified skill entry point
├── README.md                       ← This file
│
├── 1-build/                        ← Agent, tool, KB, connection development
│   ├── getting-started.md
│   ├── agents.md
│   ├── tools_and_toolkits.md
│   ├── knowledgebases.md
│   ├── connections.md
│   ├── embedded_chat.md
│   ├── best-practices.md
│   ├── deployment-safety.md
│   ├── checklist.md
│   ├── mcp-documentation-guide.md
│   └── run-adk.sh
│
├── 2-orchestrate/                  ← Multi-agent systems & workflows
│   ├── discovery-workflow.md
│   ├── workflow-patterns.md
│   ├── agent-communication.md
│   ├── mcp-integration.md
│   ├── ai-gateway-integration.md
│   ├── best-practices.md
│   ├── examples.md
│   ├── deployment.md
│   ├── troubleshooting.md
│   └── resources/
│       ├── customer_support_agents.py
│       ├── data_processing_workflow.py
│       ├── approval_workflow.py
│       └── deploy_orchestration.sh
│
├── 3-integrate/                    ← REST API integration into apps
│   ├── getting-started.md
│   ├── critical-patterns.md
│   ├── api-reference.md
│   ├── integration-workflows.md
│   ├── troubleshooting.md
│   └── resources/
│       ├── watsonx_client.py
│       ├── chat_cli.py
│       ├── test_connection.py
│       ├── server.js
│       └── package.json
│
└── 4-voice/                        ← Voice agents & channel integrations
    ├── workflow-patterns.md
    ├── voice-configuration.md
    ├── channel-integration.md
    ├── voice-optimization.md
    ├── deployment.md
    ├── testing-troubleshooting.md
    └── resources/
        ├── deploy_voice_agent.sh
        ├── credentials.sample.yaml
        └── .env.sample
```

## Quick Start

### Activate the skill
```
use_skill: agent
```

### Install the ADK
```bash
# Standard installation
pip install ibm-watsonx-orchestrate

# With voice capabilities (required for Domain 4)
pip install ibm-watsonx-orchestrate --with-voice

```

### Activate your Orchestrate environment
```bash
orchestrate env list
orchestrate env add --name MY_ENV --url WO_INSTANCE_URL
```

## Domain Guide

### When to use each domain

**Domain 1 — Build** (`1-build/`)
> Creating agents from scratch, Python tools with `@tool` decorator, knowledge bases for RAG, connections for credential management, embedded webchat.

**Domain 2 — Orchestrate** (`2-orchestrate/`)
> Multi-agent supervisor-worker patterns, `@flow` agentic workflows, connecting MCP servers, integrating third-party LLMs via AI Gateway (OpenAI, Anthropic, Google, Azure, AWS Bedrock), A2A protocol v0.3.0.

**Domain 3 — Integrate** (`3-integrate/`)
> Calling deployed agents from Python or Node.js applications, REST API authentication (IBM Cloud IAM / AWS JWT), async polling pattern, production-ready client libraries.

**Domain 4 — Voice** (`4-voice/`)
> STT/TTS configuration (Watson, Google, Azure), phone channels via Genesys Audio Connector, WhatsApp/SMS via Twilio, Slack integration, voice response optimization.

## Mandatory Requirement

**Before implementing anything in any domain**, the skill requires verifying the `watsonx-orchestrate-adk-docs` MCP server connection and searching current ADK documentation. ADK specifications change frequently — always use the MCP docs as the source of truth.

## MCP Server

| Server | Purpose |
|---|---|
| `watsonx-orchestrate-adk-docs` | Live ADK documentation search — required for all domains |

## Key Version Notes

| Item | Current | Notes |
|---|---|---|
| ADK toolkit import | `orchestrate toolkits import` (v1.15.0) | Will change to `orchestrate toolkits add` in v2.0 |
| A2A protocol | v0.3.0 | v0.2.1 is deprecated |
| Workflow API | `@flow` decorator | `FlowBuilder` is deprecated |
| REST API | v1 endpoints | v2 does not exist |
