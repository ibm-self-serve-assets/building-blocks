# WXO Domain Agent Builder using Bob

A custom Bob mode that builds and deploys watsonx Orchestrate (WXO) agents end-to-end through an interactive workflow.

## What It Does

You describe a domain (healthcare, retail, education, etc.) and Bob:
1. Interviews you to gather requirements
2. Designs the agent architecture
3. Generates all project files (config, tools, data, knowledge base, scripts)
4. Asks for your WXO API key and instance URL
5. Deploys the agent to watsonx Orchestrate

No manual setup required — just tell Bob what agent to build and provide your credentials when asked.

## Getting Started

### Prerequisites
- **Bob** — IBM Bob (Sign up here if you do't have access yet: https://www.ibm.com/products/bob).
- **uv** — Python package manager by Astral ([install](https://docs.astral.sh/uv/)). Includes `uvx`, which downloads and runs the WXO ADK on the fly — no manual pip install needed
- **WXO API key** — obtain it from WXO: click your profile (top right) → Settings → API details → Generate API key. Save it for later.
- **WXO instance URL** — your instance URL (e.g., `https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/<instance-id>`). Find it in your WXO instance details.

### Step-by-step

1. **Get the project** — clone this repo or download the `.bob` folder into your project directory.

2. **Open Bob** and open the project folder (the one containing `.bob/`) in Bob.

3. **Auto-approve.** On the bottom right, above the text area, click on the sliding button to enable all auto-approve actions except "Questions". 

4. **Ask Bob to build an agent.** For example: *"Build a financial advisor agent"*

5. **Answer Bob's questions.** Bob will ask multiple-choice questions to understand your requirements. Select an option, or click the pencil icon to edit and customize your answer.

6. **Provide your API key and instance URL.** When Bob asks, provide your WXO API key and instance URL. When prompted to enter them, **click the pencil icon on the right** and then paste your values in the text area. **Important Note:** **Do not select the default option. Click the pencil icon on the right** and then paste your values in the text area.

7. **Approve commands.** Bob will ask to run a few deployment commands — click **Run** when prompted.

8. **Done!** Bob will confirm when deployment is complete. Check your WXO instance to see your new agent deployed and live.

9. **Check the business use case.** Open `BUSINESS_USE_CASE.md` in your agent's directory for sample queries. Copy and paste some into the "Quick start prompts" section for your agent in WXO.

10. 🎉 Congrats! You’ve successfully built and deployed a tool-augmented agent with RAG capabilities in your custom domain. Enjoy! ✨

## How It Works: uvx and the WXO ADK

The WXO Agent Development Kit (ADK) does **not** need to be manually installed. Every CLI command Bob runs is prefixed with:
```bash
uvx --from ibm-watsonx-orchestrate orchestrate ...
```

`uvx` (included with `uv`) handles everything on the fly:
1. **First run** — downloads `ibm-watsonx-orchestrate` (the ADK package) into an isolated, temporary environment
2. **Subsequent runs** — uses the cached version (fast)
3. **Runs the `orchestrate` CLI** from that package

Think of `uvx` like `npx` in the Node.js world — it downloads and runs a package without installing it globally. This is why no `pip install`, no venv, and no `requirements.txt` are needed.

## Repo Contents

```
domain-agent-builder/
├── README.md                              # This file
└── .bob/                                  # Bob mode config, rules, and templates
    ├── custom_modes.yaml                  # Bob mode configuration
    ├── .mcp.json                          # MCP server config (copied to project root during setup)
    ├── rules-domain-agent-builder/        # Rule files Bob reads during the workflow
    │   ├── 1_agent_building_workflow.xml  # 7-phase workflow
    │   ├── 2_domain_examples.xml         # Domain examples
    │   ├── 3_file_templates.xml          # File templates and validation
    │   └── 4_wxo_deployment_practices.xml # WXO deployment practices
    └── portfolio-advisor-agent/           # Reference template (proven, deployed)
        ├── agent_config.yaml
        ├── BUSINESS_USE_CASE.md
        ├── README.md
        ├── TROUBLESHOOTING.md
        ├── tools/
        │   ├── account_holder_tools.py
        │   └── communication_tools.py
        ├── data/
        │   ├── account_holders.csv
        │   ├── compliance_guidelines.txt
        │   └── investment_policies.txt
        ├── knowledge_bases/
        │   └── finance_portfolio_kb.yaml
        └── scripts/
            ├── deploy_all.sh
            ├── import_tools.sh
            ├── import_kb.sh
            └── deploy_agent.sh
```

## Agent Architecture

The agents Bob builds are **tool-augmented agents with RAG capability**:

### Tool-Calling (Primary)
The LLM decides which Python tools to invoke based on user queries. Tools embed data directly as Python dicts and handle structured operations:
- Entity lookup (by ID, by tier, by status)
- Filtered queries
- Metrics and calculations
- Personalized communication generation (HTML emails, notifications)

### Knowledge Base / RAG (Secondary)
A vector-indexed knowledge base (`ibm/slate-125m-english-rtrvr-v2`) provides semantic search over CSV/text documents for open-ended questions the tools can't answer.

### LLM Orchestration
The LLM (`groq/openai/gpt-oss-120b`) sits on top and routes:
- Structured questions → **tools**
- Open-ended questions → **knowledge base**
- Conversational messages → **direct response**

## Project Structure (Generated)

```
{agent-name}-agent/
├── agent_config.yaml          # Agent config (name, LLM, tools, KB, instructions)
├── tools/
│   ├── {entity}_tools.py      # Entity management tools (embedded data)
│   └── communication_tools.py # Communication generation (self-contained)
├── data/
│   └── {entities}.csv         # Data files (for KB vectorization only)
├── knowledge_bases/
│   └── {domain}_{entity}_kb.yaml  # KB config with vector embeddings
└── scripts/
    ├── deploy_all.sh          # Full deployment orchestrator
    ├── import_tools.sh        # Import Python tools
    ├── import_kb.sh           # Import knowledge base
    └── deploy_agent.sh        # Import config + deploy agent
```

## Key Design Decisions

- **Embedded data in tools**: WXO tools run in isolated cloud environments and cannot access local files. Data is embedded as Python dicts directly in tool code.
- **Tool isolation**: Each tool is self-contained. Tools cannot call other tools. The agent LLM orchestrates multi-tool workflows.
- **5 tools recommended**: 5 or fewer tools is recommended for optimal performance (typically 3 entity + 1 communication + 1 domain-specific), though agents can use more if needed.
- **uvx for CLI**: All orchestrate commands use `uvx --from ibm-watsonx-orchestrate` for isolated execution without manual venv activation.
- **Dynamic env setup**: Before each deployment, Bob recreates the CLI environment with the user's instance URL (`env remove` → `env add -u URL` → `env activate`) to avoid stale cached instance URLs. The API key is piped to env activate to avoid interactive prompts.

## MCP Servers

The `.bob/.mcp.json` file configures two MCP servers that Bob can leverage during the workflow:

| Server | Purpose |
|--------|---------|
| `wxo-docs` | Searches WXO ADK documentation via `SearchIbmWatsonxOrchestrateAdk` |
| `orchestrate-adk` | Inspects the WXO instance — `list_tools`, `list_agents`, `list_knowledge_bases`, etc. |

During Phase 3 (Project Setup), Bob copies `.bob/.mcp.json` to the project root so the MCP servers become available.

## Rule Files

The mode's behavior is defined in `.bob/rules-domain-agent-builder/`:

| File | Purpose |
|------|---------|
| `1_agent_building_workflow.xml` | 7-phase workflow (interview → deploy) |
| `2_domain_examples.xml` | Domain examples (healthcare, retail, education, finance) |
| `3_file_templates.xml` | File templates and validation checklists |
| `4_wxo_deployment_practices.xml` | WXO deployment practices and common pitfalls |

## Reference Template

The proven, deployed portfolio advisor agent at `.bob/portfolio-advisor-agent/` serves as the foundation. Bob copies it and adapts it for each new domain. New agents are created parallel to `.bob/` in the project root.
