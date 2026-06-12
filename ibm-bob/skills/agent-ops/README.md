# Agent Ops — Bob Skill (watsonx Orchestrate)

A Bob skill that drives **build-time evaluation, adversarial red-teaming, and runtime observability** for watsonx Orchestrate (WXO) agents using the WXO ADK. Targets supported: **Developer Edition** (local server on `:4321`) and **SaaS** cloud.

## What this skill does

When a developer says they want to evaluate, red-team, or observe a WXO agent, this skill drives a 3-question interview to understand the target environment, intent, and current state — then emits bash commands for the user to run in their terminal. Bob never runs mutating evals itself.

The skill covers 5 self-contained modules (any order):

1. **Eval** — `orchestrate evaluations quick-eval` (smoke) and `evaluate --with-langfuse` (full)
2. **Benchmarks** — `record`, `generate`, or manual JSON authoring with full schema validation
3. **Analyze** — `analyze` and `analyze --mode enhanced`; metric thresholds + failure diagnosis
4. **Red-teaming** — `list` / `plan` / `run`; OWASP Top 10 for LLM attack catalog; severity ratings + remediation prompts
5. **Observability** — traces CLI + Python SDK + Langfuse (local & hosted) + IBM Telemetry; cost & latency 5-layer report

## When to use this skill

- Validating a WXO agent before deploying to SaaS or releasing to customers
- Authoring benchmark scenarios from real chat sessions (`record`) or rough stories (`generate`)
- Interpreting `summary_metrics.csv`, `knowledge_base_summary_metrics.json`, or `results.json` from a prior eval
- Diagnosing why scenarios failed (benchmark issue vs agent issue vs infra crash)
- Running adversarial security testing on native WXO agents
- Searching and exporting runtime traces; setting up Langfuse for cost / latency analysis
- Asked about WXO performance tuning (this skill fetches live docs via MCP)

## When NOT to use this skill — see instead

- **Add runtime safety/quality guardrails to an AI agent in production** (4-choke-point Pass/Flag/Block enforcement, watsonx.governance metrics) → use the **real-time-guardrails** skill. Agent Ops is *build-time* validation; Real-Time Guardrails is *runtime* enforcement.
- **Evaluate a non-WXO GenAI app or RAG pipeline with watsonx.governance metrics** (Faithfulness, Answer Relevancy, HAP, PII via MCP) → use the **build-time-gen-ai-evals** skill. Agent Ops is WXO-specific; Build-Time GenAI is for general LLM apps / RAG / agentic tool-call evaluation.

| Skill | Lifecycle stage | Trigger |
|---|---|---|
| **agent-ops** (this one) | Build-time (pre-deploy) | WXO agent ready for validation |
| real-time-guardrails | Runtime (per-request) | Production traffic |
| build-time-gen-ai-evals | Build-time (pre-deploy) | Dataset of inputs/outputs/traces |

## Prerequisites

| Component | Version | Purpose |
|---|---|---|
| **WXO ADK with `[agentops]` extra** | `>= 2.6.0, < 3.0.0` (pulls eval-fw `>= 1.4.0, < 2.0.0`) | The CLI Bob emits commands for |
| **Python** | **3.12** (3.11 may work; 3.13+ not yet supported) | venv for the ADK |
| **Docker runtime** | recent | DevEd Lima VM (WXO server + Langfuse + Milvus + OpenSearch + ClickHouse, ~20 containers, ~16 GB RAM) |
| **`uv` / `uvx`** | latest | Launches the WXO docs MCP server |
| **IBM Cloud + watsonx.ai** | API key + project/space | RAG judges (Faithfulness, Relevancy) + red-teaming planner |
| **Langfuse keys** (optional) | from local or hosted UI | Cost & latency analysis |

See `assets/PREREQUISITES.md` for the full credential matrix, hardware requirements, network egress, and troubleshooting table.

## What's in this skill

```
agent-ops/
├── SKILL.md                       # Bob loads this on every invocation
├── README.md                      # this file (partner-facing overview)
├── USAGE-GUIDE.md                 # install + first-run walkthrough
├── setup.sh                       # one-command venv + ADK install
├── reference/                     # detailed knowledge, Bob loads on demand
│   ├── auth-env-matrix.md         # capability × {DevEd, SaaS} env requirements
│   ├── module-eval.md             # quick-eval, evaluate, --with-langfuse, failure modes
│   ├── module-benchmarks.md       # JSON schema, DAG patterns, arg_matching, coverage
│   ├── module-analyze.md          # metric thresholds + diagnosis table + benchmark-vs-agent
│   ├── module-red-teaming.md      # attack catalog, severity, remediation prompts
│   ├── module-observability.md    # traces CLI + Python SDK + Langfuse + cost/latency
│   └── command-emission.md        # canonical bash-block format + worked examples
├── examples/                      # working benchmark scenarios
│   ├── portfolio_advisor/         # 8 scenarios, all passing on a real agent
│   ├── minimal_single_tool/       # smallest valid benchmark (use for `generate` priming)
│   ├── multi_agent_routing/       # facilitator + 2 collaborators (Routing F1)
│   ├── rag_only/                  # 2 KB-bound scenarios (Faithfulness in isolation)
│   └── stories_sample.csv         # CSV input format for `generate`
└── assets/
    ├── mcp.json                   # registers watsonx-orchestrate-adk-docs MCP server
    └── PREREQUISITES.md           # full install, credentials, hardware, network, troubleshooting
```

## Installing this skill

Drop the `agent-ops/` folder into your Bob skill directory:

```bash
cp -r agent-ops ~/path/to/your/repo/.bob/skills/
```

Then open your agent's project in Bob and ask something like:

- *"Help me evaluate this WXO agent before I deploy to SaaS"*
- *"Run red-teaming on my portfolio-advisor agent"*
- *"My eval results came back with Faithfulness 0.65 — what's wrong?"*
- *"How do I set up Langfuse so I can see cost per scenario?"*

Bob will run the 3-question interview, then drive the relevant module(s).

## Design properties

- **Modular** — 5 self-contained modules can be invoked in any order; you don't have to go through eval before red-teaming or observability.
- **DevEd + SaaS parity** — target environment is asked upfront; both paths are first-class throughout.
- **Terminal-emitting** — Bob never runs `pip install`, `server start`, or `evaluations evaluate` itself. It writes the command; you run it in your terminal. No surprise mutations.
- **Live ADK doc search** — the bundled `watsonx-orchestrate-adk-docs` MCP server keeps Bob in sync with the current ADK docs at conversation time.
- **Field-curated guidance** — metric thresholds, failure-diagnosis tables, severity tiers, and report formats are starting points from real customer engagements, labeled distinctly from WXO-published semantics so you know which is which.

## Underlying CLI

This skill drives the **IBM WXO ADK** — `ibm-watsonx-orchestrate` Python package with the `[agentops]` extra. Source of truth for ADK semantics: https://developer.watson-orchestrate.ibm.com/.
