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
| "multi-agent", "A2A", "AI Gateway", "MCP server", "agent swarm", "agent collaboration" | **Orchestrate** | `2-orchestrate/` |
| "agentic workflow", "@flow", "flow decorator", "foreach", "parallel flow", "loop", "script node", "prompt node", "timer node", "decisions node", "docext", "docproc", "docclassifier", "userflow", "form", "callbacks", "masking", "multi-language flow" | **Flows** | `6-flows/` — start at `getting-started.md` |
| "integrate into app", "REST API", "Python client", "Node.js", "call agent from code" | **Integrate** | `3-integrate/` |
| "voice agent", "phone channel", "STT", "TTS", "WhatsApp", "SMS", "Slack channel" | **Voice** | `4-voice/` |
| "controls", "guardrails", "PII filter", "policy", "rate limit", "SQL sanitizer", "content safety", "secrets detector", "regex filter", "model fallback", "load balance" | **Controls** | `5-controls/` — start at `getting-started.md` |
| "evaluate", "agent evaluation", "benchmark agent", "test agent performance" | **Evaluations** | See `orchestrate evaluations --help` |
| "observability", "traces", "trace export", "monitoring" | **Observability** | See `orchestrate observability --help` |

Tasks that span multiple domains (e.g., build then integrate) simply use both domains in sequence.

### Controls — 3-path routing decision

When controls intent is detected, or when building an agent (Domain 1), apply this decision tree:

```
Is the user building a new agent from scratch?
│
├── YES (Domain 1 + controls gate)
│     → Complete agent build files first
│     → MANDATORY: Before presenting final deliverables, run the
│       Controls Recommendation Engine (see 5-controls/getting-started.md):
│          1. Analyse what was built (purpose, data sensitivity, tools)
│          2. Recommend specific controls with reasons
│          3. Let user pick which to add (all / some / none)
│          ├── User picks some → Path A: generate controls import
│          │   YAML files + CLI commands (controls are standalone,
│          │   NOT embedded in agent YAML)
│          └── User skips → present final deliverables
│
└── NO — is the user asking about controls only?
      │
      ├── Does an agent/tool/model already exist in WXO?
      │     ├── YES → Path C: inspect existing controls with
      │     │         'orchestrate controls list --agent <name>'
      │     │         then generate create/update commands
      │     └── NO  → Path B: controls-only workflow
      │               generate CLI commands / import YAML files
      │               and hand to user to execute
      └── (either way) → open 5-controls/getting-started.md
```

**Path A** (new agent + controls): `1-build/getting-started.md` Phase 5.5 → `5-controls/getting-started.md`
**Path B** (controls only): `5-controls/getting-started.md` → `5-controls/recipes.md`
**Path C** (existing agent + controls): `5-controls/getting-started.md` → `5-controls/cli-reference.md`

> ⚠️ **Controls are always standalone resources** — they are NEVER embedded inside the agent YAML. The agent YAML `plugins` field is a different system (built-in plugins only). Controls are imported separately via `orchestrate controls import` and bound to agents by display name.

### Additional First-Class CLI Commands (not domain-specific)

These `orchestrate` commands are available but not covered by the 4 domains above:

| Command | Purpose |
|---|---|
| `orchestrate controls` | Bind policy artifacts (PII filter, guardrails, rate limiter, SQL sanitizer, secrets detector, regex pattern, model fallback/retry/load-balance) to agents, tools, and models |
| `orchestrate evaluations` | Evaluate agent performance against benchmark datasets in your active environment |
| `orchestrate observability` | Search and export trace data from the observability platform for analysis in third-party tools |
| `orchestrate settings` | Configure environment-level settings for your active env |
| `orchestrate partners` | Generate a submission-ready agent artifact package for partner-built agents |

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
Build sophisticated multi-agent systems and cross-framework integrations.
- **Multi-agent architectures**: supervisor-worker, agent swarms, hierarchical systems
- **MCP server integration**: local and remote MCP toolkits
- **AI Gateway**: connect OpenAI, Anthropic, Google Gemini, Azure OpenAI, AWS Bedrock, and 8+ more providers
- **Agent communication**: native collaboration, A2A protocol v0.3.0, external chat API

### Domain 6 — Flows (`6-flows/`)
Build agentic workflows — Python-code-first orchestration of agents, tools, and humans with the `@flow` decorator.
- **14 node types**: agent, tool, script, conditions, parallel, parallel_conditions, foreach, loop, timer, prompt, decisions, userflow, docext/docproc/docclassifier
- **Forms and user activity**: `userflow()`, `form()` with 15+ field types, dynamic forms, multi-user assignment
- **Data mapping**: `map_input()`/`map_output()`, `DataMap`, `private_schema`, sensitive data masking (`MaskingPolicy`)
- **Document processing** (Public Preview): field extraction (`docext`), text extraction + KVP (`docproc`), classification (`docclassifier`)
- **Callbacks**: `aflow.add_callback()` with 8 `FlowCallbackEventKind` events for audit/monitoring
- **MCP Flow Server** (Public Preview): expose flows as MCP tools with sync/async/query patterns and elicitation handling
- **Error handling**: `NodeErrorHandlerConfig` with retry, show_message, and branch patterns
- **Multi-language**: `target_locales()`, `source_locale()`, translation CSV import/export

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

### Domain 5 — Controls (`5-controls/`)
Protect agents, tools, and models with policy controls — no code changes required.
- **13 artifact types** across 3 asset categories (agent, tool, model)
- **Agent controls**: Guardrails (content safety), pii_filter, SecretsDetection, RegexPattern, OutputLengthGuardPlugin
- **Tool controls**: SQLSanitizer, RateLimiterPlugin (+ Guardrails, SecretsDetection, OutputLengthGuardPlugin)
- **Model controls**: fallback (provider failover), load_balance (weighted distribution), retry_mode
- **Execution hooks**: `agent_pre_invoke`, `agent_post_invoke`, `tool_pre_invoke`, `tool_post_invoke`, `prompt_pre_fetch`, `prompt_post_fetch`
- **Priority ordering**: lower number = fires first (blocking controls at 1–10, redaction at 50–90, logging at 100+)
- **Deployment**: YAML import/export for version control and cross-env deployment

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

### Domain 6 — Flows (`6-flows/`)
- `getting-started.md` — `@flow` decorator (all params incl. `private_schema`, `schedulable`), import CLI, testing, key concepts, expression reference, `FlowContextWindow`
- `node-reference.md` — All 14 node types: agent, tool, script, conditions (branch), parallel, parallel_conditions, foreach, loop, timer, prompt, decisions, userflow, docext, docproc, docclassifier
- `forms-and-userflow.md` — `userflow()`, `form()`, all 15+ field types, dynamic forms (visibility/label/value-source behaviours), multi-user assignment, multi-language support
- `data-mapping.md` — `map_input()`, `map_output()`, `DataMap`+`Assignment`, `private_schema`, `aflow.mask_property()` with `MaskingPolicy`/`InputPolicy`, expression reference
- `document-processing.md` — `docproc()` (text extraction, KVP schemas, `PageRange`), `docext()` (`DocExtConfigField`, `DocExtConfigTableField`, `available_options`, OCR language), `docclassifier()`, file limits
- `callbacks-and-mcp.md` — `aflow.add_callback()`, `FlowCallbackEventKind` (8 events), callback payload schema, MCP Flow Server (sync/async/query tools, elicitation handling)
- `error-handling.md` — `NodeErrorHandlerConfig` (`on_error: branch/show_message`, `max_retries`, `retry_interval`, `error_edge_id`)
- `assets/hello_flow.py` — Minimal @flow + tool sequence + test harness
- `assets/approval_flow.py` — Human-in-the-loop form, multi-user assignment, error branching
- `assets/masking_flow.py` — Masking across all node types (input, private, script, tool, userflow)
- `assets/document_extraction_flow.py` — docproc KVP, docext with tables + available_options, docclassifier, OCR language
- `assets/multi_language_flow.py` — target_locales, source_locale, translation CLI workflow
- `assets/parallel_flow.py` — parallel() + parallel_conditions() multi-phase delivery
- `assets/foreach_flow.py` — foreach + ForeachPolicy.SEQUENTIAL / PARALLEL
- `assets/callback_flow.py` — add_callback() with flow and task lifecycle events
- `assets/decisions_flow.py` — Decision table with programmatically built rules
- `assets/timer_loop_flow.py` — Polling loop with timer node
- `assets/mcp_flow_tools.json` — MCP Flow Server tool schema reference

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

### Domain 5 — Controls (`5-controls/`)
- `getting-started.md` — Discovery questionnaire, asset-type matrix, hook cheat-sheet, pitfalls
- `cli-reference.md` — All 10 commands with every flag and live output examples
- `artifact-types.md` — Full config schemas for all 13 artifact types (verified live)
- `hooks-and-priority.md` — Execution flow diagram, priority rules, hook selection guide
- `recipes.md` — 16 copy-paste recipes covering PII, guardrails, secrets, SQL, rate limits, model resilience
- `import-export.md` — YAML file schema, cross-env deployment workflow
- `troubleshooting.md` — Common errors (422, unbound controls, 2.8.0 binary, --type flag)
- `resources/pii-filter.yaml` — Ready-made PII filter control
- `resources/content-guardrails.yaml` — Jailbreak + secrets + regex guard stack
- `resources/sql-sanitizer.yaml` — SQL sanitizer + rate limiter for tools
- `resources/model-resilience.yaml` — Model fallback + retry controls
- `resources/apply-controls.sh` — Deployment script for all resource files

---

## Critical Principles

### 1. Documentation-First (ALL DOMAINS)
**ALWAYS search watsonx Orchestrate ADK documentation before implementing ANY component.**
- Use `SearchIbmWatsonxOrchestrateAdk` MCP tool
- ADK specifications change frequently — never rely solely on static examples
- Search multiple times with different queries if needed

### 2. Version Awareness
- **ADK v2.15.0 (current)**: uses `orchestrate toolkits add` — `toolkits import` is the legacy alias, still works but `add` is the canonical command
- **A2A protocol**: use v0.3.0 (v0.2.1 is deprecated)
- **`@flow` decorator**: the ONLY current workflow API — `FlowBuilder` class-based API is fully deprecated and removed
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

### 7. Controls Principles (Domain 5)
- `--hook` is required on `create` — omitting it causes `422 Unprocessable Entity`
- `--agent` takes the **display_name**, not the internal name or UUID
- Creating without `--agent`/`--tool`/`--model` creates an unbound control (no effect)
- `--agent`/`--hook` in `update` **replace** existing values — re-specify everything you want to keep
- All detection flags in Guardrails / pii_filter / SecretsDetection default to `false` — must opt in
- `orchestrate --version` must show `2.15.0` — if it shows `2.8.0`, activate the venv first

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
