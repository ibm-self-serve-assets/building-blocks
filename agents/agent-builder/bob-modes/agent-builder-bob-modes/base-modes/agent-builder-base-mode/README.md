# 🤖 WxO Agent Builder — Bob Mode

A specialized **Bob AI mode** that acts as your expert pair programmer for building [IBM watsonx Orchestrate](https://www.ibm.com/docs/en/watsonx/orchestrate) native agents from scratch — end to end.

> **Built-in knowledge:** This mode comes pre-loaded with IBM watsonx Orchestrate Agent Builder building blocks — including curated concepts, rules, workflow patterns, best practices, and deployment knowledge — so Bob already knows how to build production-ready agents correctly from day one.

---

## What It Does

The **WxO Agent Builder** mode guides you through the full lifecycle of building a production-ready watsonx Orchestrate agent:

```
Discovery → Planning → Implementation → Deployment → Documentation
```

| Phase | What Happens |
|-------|-------------|
| 🔍 **Discovery** | Bob interviews you to understand your use case, users, and requirements |
| 🏗️ **Project Setup** | Creates IBM-recommended folder structure and project scaffolding |
| 📋 **Planning** | Switches to Plan mode and generates a detailed `plan.md` for your approval |
| ⚙️ **Implementation** | Builds agents, Python tools, knowledge bases, and connections |
| 🚀 **Deployment** | Generates `deploy.sh` and `rollback.sh` scripts |
| 📚 **Documentation** | Auto-generates `README.md`, quickstart guides, and project summaries |

---

## Key Features

- **Guided agent creation** — step-by-step questionnaire to capture requirements before writing a single line of code
- **IBM ADK best practices** — follows official naming conventions, folder structures, and patterns
- **Live documentation lookup** — queries the `watsonx-orchestrate-adk-docs` MCP server for up-to-date ADK syntax and examples
- **Full project scaffolding** — agents, tools, knowledge bases, connections, channels, and scripts
- **Multi-agent support** — design orchestrator + specialist agent hierarchies
- **Deployment automation** — ready-to-run shell scripts for deploy and rollback
- **Auto-generated docs** — README, quickstart, and project summary for every project

---

## Built-in Building Blocks Knowledge

This mode has the following Agent Builder concepts, rules, and knowledge baked directly into it:

### 🧠 Concepts & Workflow Patterns
- **Agent styles** — when to use `default`, `react`, or `planner` execution styles
- **Multi-agent architecture** — how to design orchestrator + specialist agent hierarchies with proper routing logic
- **Python tool patterns** — `@tool` decorator usage, type hints, docstrings, and the `@expect_credentials` pattern for authenticated tools
- **Knowledge base (RAG)** — document preparation, indexing workflow, and attaching knowledge bases to agents
- **Connection management** — `key_value`, `api_key`, `bearer`, and `basic` auth types; team vs. member credentials
- **Channel setup** — webchat embed, Slack, WhatsApp/SMS (Twilio), and phone integrations

### 📏 Critical Rules (Always Enforced)
- **MCP-first** — always queries the `watsonx-orchestrate-adk-docs` MCP server for the latest ADK syntax before implementing anything
- **snake_case everywhere** — IBM's official naming standard enforced for all agents, tools, and files
- **No hardcoded credentials** — always uses connections for credential management, never inline secrets
- **No direct deployment** — never runs `orchestrate` CLI commands directly; always generates scripts for user review and control
- **Plan before code** — never starts implementation without an approved `plan.md`

### 🚀 Deployment Knowledge
- Correct `orchestrate` CLI command patterns for importing tools, agents, knowledge bases, and connections
- Path resolution for scripts in the `scripts/` subfolder
- Deploy + rollback script templates with proper error handling (`set -e`)
- Environment management (draft → live promotion)

---

## What Gets Built

A typical agent project produced by this mode looks like:

```
my_agent/
├── agents/          # Agent YAML specifications
├── tools/           # Python tools with @tool decorator
├── knowledge/       # Knowledge base specs and documents
├── connections/     # API connection configurations
├── flows/           # Agentic workflow definitions
├── scripts/
│   ├── deploy.sh    # One-command deployment
│   └── rollback.sh  # One-command rollback
├── docs/
│   ├── PROJECT_SUMMARY.md
│   └── QUICKSTART.md
├── requirements.txt
└── README.md
```

---

## Setup & Installation

1. **Clone this repository**
   ```bash
   git clone <repo-url>
   ```

2. **Open the `agent-builder-base-mode` folder uncompress the file, and open it as the root folder in the Bob application**

3. **That's it!** — The `🤖 WxO Agent Builder` mode will automatically appear in Bob's mode selector, ready to use.

---

## How to Use

1. Select **`🤖 WxO Agent Builder`** from the Bob mode selector
2. Tell Bob what kind of agent you want to build
3. Answer the discovery questions (Bob will ask 2–3 at a time)
4. Review and approve the generated `plan.md`
5. Bob builds everything — tools, agents, connections, scripts, and docs
6. Run `scripts/deploy.sh` to deploy to watsonx Orchestrate

---

**Note:**
- Get the project — clone this repo or download the .bob folder into your project directory.
- Open Bob and open the project folder (the one containing .bob/) in Bob. Important: When starting to use this Bob mode, your project folder should contain only the .bob folder downloaded from this custom mode. No additional files or folders should be present in the project folder to ensure Bob does not receive unwanted context while using this mode.

## Prerequisites

- Bob AI with MCP support enabled
- IBM watsonx Orchestrate access
- Python 3.10+
- `watsonx-orchestrate-adk-docs` MCP server configured (see `.bob/mcp.json`)

---


