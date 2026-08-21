# Agent Skill

The **`agent`** skill is your end-to-end companion for building production-ready AI agents on IBM watsonx Orchestrate. It covers the full agent lifecycle — from creating individual agents and tools, to orchestrating complex multi-agent systems, to integrating agents into applications via REST API, to enabling voice interactions across phone, messaging, and chat channels, to enforcing policy controls for safety, privacy, and resilience. Everything you need to design, build, deploy, and operate watsonx Orchestrate agents lives in one place, organized into five progressive domains.

## Domains

| Domain | Folder | What it covers |
|---|---|---|
| **1 — Build** | [`1-build/`](./1-build/) | Agents, tools, knowledge bases, connections, embedded chat |
| **2 — Orchestrate** | [`2-orchestrate/`](./2-orchestrate/) | Multi-agent systems, AI Gateway, MCP, A2A protocol |
| **3 — Integrate** | [`3-integrate/`](./3-integrate/) | REST API integration into applications (Python, Node.js) |
| **4 — Voice** | [`4-voice/`](./4-voice/) | Voice agents, STT/TTS, phone/messaging/Slack channels |
| **5 — Controls** | [`5-controls/`](./5-controls/) | Policy controls — PII filter, guardrails, secrets, SQL sanitizer, rate limits, model resilience |
| **6 — Flows** | [`6-flows/`](./6-flows/) | Agentic workflows — `@flow` decorator, all node types, forms, data mapping, doc processing, callbacks, MCP |

## Directory Structure

```
agent/
├── SKILL.md                        ← Unified skill entry point
├── README.md                       ← This file
│
├── 1-build/                        ← Agent, tool, KB, connection development
│   ├── getting-started.md          ← Phase workflow incl. Phase 5.5 controls gate
│   ├── agents.md
│   ├── tools_and_toolkits.md
│   ├── knowledgebases.md
│   ├── connections.md
│   ├── embedded_chat.md
│   ├── best-practices.md
│   ├── deployment-safety.md
│   ├── checklist.md                ← Includes Controls Gate Checklist
│   ├── mcp-documentation-guide.md
│   └── run-adk.sh
│
├── 2-orchestrate/                  ← Multi-agent systems & cross-framework integrations
│   ├── discovery-workflow.md
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
├── 4-voice/                        ← Voice agents & channel integrations
│   ├── workflow-patterns.md
│   ├── voice-configuration.md
│   ├── channel-integration.md
│   ├── voice-optimization.md
│   ├── deployment.md
│   ├── testing-troubleshooting.md
│   └── resources/
│       ├── deploy_voice_agent.sh
│       ├── credentials.sample.yaml
│       └── .env.sample
│
├── 5-controls/                     ← Policy controls (PII, guardrails, SQL, rate limits, model resilience)
    ├── getting-started.md          ← 3-path routing + Controls Recommendation Engine
    ├── cli-reference.md            ← All 10 commands with every flag
    ├── artifact-types.md           ← Full config schemas for all 13 artifact types
    ├── hooks-and-priority.md       ← Execution flow, priority rules
    ├── recipes.md                  ← 16 copy-paste recipes
    ├── import-export.md            ← YAML schema (spec_version: v1) + deployment
    ├── troubleshooting.md          ← 422 errors, unbound controls, schema mistakes
    └── resources/
        ├── pii-filter.yaml         ← Ready-made PII filter control
        ├── content-guardrails.yaml ← Content Guardrails control
        ├── sql-sanitizer.yaml      ← SQL Sanitizer control
        ├── model-resilience.yaml   ← Model Fallback control
        └── apply-controls.sh       ← Bulk deployment script

└── 6-flows/                        ← Agentic workflows — @flow decorator, all node types
    ├── getting-started.md          ← 3-path routing + Controls Recommendation Engine
    ├── cli-reference.md            ← All 10 commands with every flag
    ├── artifact-types.md           ← Full config schemas for all 13 artifact types
    ├── hooks-and-priority.md       ← Execution flow, priority rules
    ├── recipes.md                  ← 16 copy-paste recipes
    ├── import-export.md            ← YAML schema (spec_version: v1) + deployment
    ├── troubleshooting.md          ← 422 errors, unbound controls, schema mistakes
    └── resources/
        ├── pii-filter.yaml         ← Ready-made PII filter control
        ├── content-guardrails.yaml ← Content Guardrails control
        ├── sql-sanitizer.yaml      ← SQL Sanitizer control
        ├── model-resilience.yaml   ← Model Fallback control
        └── apply-controls.sh       ← Bulk deployment script
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
> Creating agents from scratch, Python tools with `@tool` decorator, knowledge bases for RAG, connections for credential management, embedded webchat. Includes a mandatory **Phase 5.5 Controls Gate** — after building, Bob analyses the agent and recommends specific policy controls before handing over deliverables.

**Domain 2 — Orchestrate** (`2-orchestrate/`)
> Multi-agent supervisor-worker patterns, `@flow` agentic workflows, connecting MCP servers, integrating third-party LLMs via AI Gateway (OpenAI, Anthropic, Google, Azure, AWS Bedrock), A2A protocol v0.3.0.

**Domain 3 — Integrate** (`3-integrate/`)
> Calling deployed agents from Python or Node.js applications, REST API authentication (IBM Cloud IAM / AWS JWT), async polling pattern, production-ready client libraries.

**Domain 4 — Voice** (`4-voice/`)
> STT/TTS configuration (Watson, Google, Azure), phone channels via Genesys Audio Connector, WhatsApp/SMS via Twilio, Slack integration, voice response optimization.

**Domain 5 — Controls** (`5-controls/`)
> Attach policy artifacts to agents, tools, and models — no code changes required. Three entry paths: **Path A** (new agent, contextual recommendations after build), **Path B** (controls only, push to existing WXO instance), **Path C** (add controls to an already-deployed agent). 13 artifact types across agent / tool / model categories. Controls are standalone resources imported via `orchestrate controls import` — never embedded in agent YAML.

## Mandatory Requirement

**Before implementing anything in any domain**, the skill requires verifying the `watsonx-orchestrate-adk-docs` MCP server connection and searching current ADK documentation. ADK specifications change frequently — always use the MCP docs as the source of truth.

## MCP Server

| Server | Purpose |
|---|---|
| `watsonx-orchestrate-adk-docs` | Live ADK documentation search — required for all domains |

## Key Version Notes

| Item | Current | Notes |
|---|---|---|
| ADK version | 2.15.0 | Always verify with `orchestrate --version` |
| ADK toolkit command | `orchestrate toolkits add` | `toolkits import` is the legacy alias — still works but `add` is canonical |
| A2A protocol | v0.3.0 | v0.2.1 is deprecated |
| Workflow API | `@flow` decorator | **Only** current API — `FlowBuilder` class-based API is fully deprecated and removed |
| Controls YAML schema | `spec_version: v1` + `artifact_name:` + `agent_names:` | Legacy flat format (`artifact:` / `agents:`) causes 422 errors |
| Controls in agent YAML | ❌ Not supported | Controls are standalone — `plugins` field in agent YAML is a separate built-in system |
| REST API | v1 endpoints | v2 does not exist |
| Controls | `orchestrate controls` | First-class command for policy enforcement on agents, tools, and models |
| Evaluations | `orchestrate evaluations` | First-class command for benchmarking agent performance |
