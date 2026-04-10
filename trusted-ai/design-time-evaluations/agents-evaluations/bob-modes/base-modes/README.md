# Build-time AgentOps Evaluator

Your agent passes unit tests — but will it call the right tools with the right arguments when a real user asks an ambiguous question? Will it hallucinate tool calls that don't exist? Will it leak its system prompt under adversarial pressure? Will a single multi-turn conversation burn through your token budget?

**Build-time AgentOps answers these questions before deployment.** This [Bob](https://bob.ibm.com) custom mode (IBM's AI code assistant) puts your watsonx Orchestrate (WXO) agent through rigorous, automated evaluation — LLM-simulated user conversations, tool-calling precision/recall metrics, RAG faithfulness scoring, per-turn token and cost analysis via Langfuse, and adversarial red-teaming across 15 attack vectors. Every failure is traced to its root cause — whether that's the agent, the benchmark, or the infrastructure — with concrete fixes, not generic advice.

## What You Need

**Required:**
- [Bob](https://bob.ibm.com) (IBM's AI code assistant — VSCode extension)
- WXO Developer Edition (local server on port 8080)
- IBM watsonx Orchestrate ADK (2.5.1 or 2.6.x — **not** 2.7.0):
  ```bash
  pip install "ibm-watsonx-orchestrate[agentops]>=2.5.1,<2.7.0"
  pip install "ibm-watsonx-orchestrate-evaluation-framework==1.2.7"
  pip install "langfuse<4"
  ```
- Python 3.12 (3.11 and lower are not supported)
- A WXO agent with tools (and optionally a knowledge base) to evaluate

**Optional:**
- `uvx` installed (`pip install uv`) — needed for the MCP docs server
- A `.env` file with Developer Edition credentials:
  ```
  WO_DEVELOPER_EDITION_SOURCE=orchestrate
  WO_INSTANCE=https://api.<region>.watson-orchestrate.ibm.com/instances/<id>
  WO_API_KEY=<your-api-key>
  ```

## Installation

**Option A: Project-level mode (recommended)**

1. Download `build-time-agentops.zip` from this repo
2. Unzip it into your agent project root:
   ```bash
   unzip build-time-agentops.zip -d /path/to/your/agent/project
   ```
   This places the `.bob/` folder and `.mcp.json` in your project, next to your agent. Bob will detect the mode automatically.

**Option B: Global mode**

1. Download and unzip `build-time-agentops.zip`
2. Append the contents of `.bob/custom_modes.yaml` to Bob's global config:
   ```
   ~/Library/Application Support/IBM Bob/User/globalStorage/ibm.bob-code/settings/custom_modes.yaml
   ```
3. Copy the `.bob/` folder and `.mcp.json` from the unzipped folder to your project root.

Then switch to the **Build-time AgentOps Evaluator** mode in Bob's mode selector.

## How It Works

When you start a conversation, Bob asks what type of evaluation you need:

| Choice | What Bob does |
|--------|-------------|
| **(a) Quick connectivity check** | Verifies ADK, server, agent imported, tools accessible. Done in 2 minutes. |
| **(b) Full end-to-end evaluation** | Benchmarks + metrics + analysis + recommendations. The complete pipeline. |
| **(c) Cost and latency analysis** | Runs evaluation with Langfuse tracing, then queries the Langfuse API to produce a 5-layer cost/token analysis: per-scenario breakdown, per-turn context growth, cost patterns, data-driven recommendations, and production projections. |
| **(d) Red-teaming** | Adversarial security testing — prompt injection, data extraction, jailbreaking. |
| **(e) Something else** | Describe what you need and Bob tailors the workflow. |

Bob checks what already exists (ADK installed? server running? agent imported? benchmarks written?) and **only does what's needed** — it won't repeat steps you've already completed.

## Evaluation Workflow

```
Phase 1: Setup → Phase 2: Smoke Test → Phase 3: Benchmarks → Phase 4: Evaluation → Phase 5: Analysis → Phase 6: Red-Teaming
```

1. **Setup** — Checks Developer Edition prerequisite, locates ADK, verifies server, imports agent
2. **Smoke Test** — Runs `quick-eval` with 2 scenarios as a connectivity check (Yes/No report)
3. **Benchmark Authoring** — Reads your agent's tool code first, writes benchmarks simple-to-complex, validates each with correctness + quality + dry-run checks
4. **Full Evaluation** — Runs benchmarks with LLM-simulated users, optionally with `--with-langfuse`
5. **Analysis & Diagnosis** — Interprets metrics, considers benchmark issues vs agent issues, implements fixes, asks about next steps
6. **Red-Teaming** — Plans and executes adversarial attacks, recommends guardrails

## Cost & Latency Analysis

When you choose option (c), Bob produces a deep cost/latency report by querying the Langfuse API directly:

- **Per-scenario breakdown** — tokens, cost, pass/fail status
- **Per-turn context growth** — how tokens accumulate in multi-turn conversations (the #1 cost driver)
- **Cost patterns** — base cost, growth rate, input/output ratio, wasted spend on failures
- **Data-driven recommendations** — only what the data supports (not a generic checklist)
- **Production projection** — estimated monthly cost at your expected conversation volume

## Mode Contents

```
build-time-agentops/
├── .bob/
│   ├── custom_modes.yaml                    # Mode definition with 16 mandatory rules
│   ├── workflow.md                          # 6-phase workflow + 3 appendices
│   ├── rules-build-time-agentops/
│   │   ├── 1_evaluation_workflow.xml        # Phase-by-phase steps with user context
│   │   ├── 2_benchmark_authoring.xml        # JSON schema, DAG patterns, quality checklist, dry-run
│   │   ├── 3_metrics_and_diagnosis.xml      # Metric definitions, thresholds, diagnosis table
│   │   └── 4_red_teaming.xml               # Attack categories, remediation patterns
│   └── reference-benchmarks/
│       ├── portfolio_advisor_benchmarks/     # 8 working scenario JSONs
│       └── stories_sample.csv               # Sample stories CSV for generate command
└── .mcp.json                                # WXO ADK docs MCP server
```

## MCP: ADK Docs Search

The `.mcp.json` connects Bob to the live WXO ADK documentation server. Bob can search the official ADK docs for command syntax, flags, and best practices — without leaving the conversation.

Requires `uvx` — install with `pip install uv`.

## Key Rules

- Bob asks what type of evaluation you need before doing anything
- Developer Edition is a hard prerequisite — cloud/SaaS mode is not supported
- Always uses `-k python` flag when importing Python tools
- Reads your agent's tool code before writing benchmarks (never guesses)
- Validates every benchmark with correctness + quality + dry-run checks
- Smoke test is connectivity-only (2 scenarios, Yes/No report)
- When analyzing failures, considers benchmark issues vs agent issues
- Queries Langfuse API for cost/token data (doesn't ask you to check the dashboard)
- Never declares "task complete" — asks about next steps

## Example Prompts

```
"Help me evaluate my customer service agent before we go to production."

"I want to understand the cost and latency of my agent — run a cost analysis."

"My evaluation shows Journey Success = 0 but Completion = 80%. What's wrong?"

"My agent passed functional eval. Red-team it for security vulnerabilities."
```

## ADK Commands Covered

| Command | Mode Coverage |
|---------|---------------|
| `evaluate` | Phase 4 (Full Evaluation) |
| `analyze` (default + enhanced) | Phase 5 (Analysis & Diagnosis) |
| `quick-eval` | Phase 2 (Smoke Test) |
| `generate` | Phase 3 (Benchmark Authoring) |
| `record` | Phase 3 (requires live chat UI) |
| `validate-native` / `validate-external` | Appendix A |
| `red-teaming list` / `plan` / `run` | Phase 6 (Red-Teaming) |


## Troubleshooting

**Troubleshooting Error: 'meta-llama/llama-3-405b-instruct' was not found**


If you encounter this error then:
    
1. create the following `config.yaml` at `lab-4-agent-ops/assets/config.yaml`:
- `auth_config:url`: url of your watsonx Orchestrate local edition server.
- `auth_config:token` API key for your watsonx Orchestrate local edition server.  This can be found at `~/.cache/orchestrate/credentials.yaml`

```yaml
auth_config:
  url: http://localhost:4321
  tenant_name: local
  token: <token>
provider_config:
  provider: "gateway"
  model_id: "meta-llama/llama-3-3-70b-instruct"
```

2. Re-run the following command which includes a new `--config` parameter:

```bash
orchestrate evaluations evaluate \
  --test-paths ./lab_eval_subset \
  --output-dir ./lab_eval_results \
  --config ../config.yaml
```




## Learn More

- [Bob — IBM's AI Code Assistant](https://bob.ibm.com)
- [WXO ADK Documentation](https://developer.watson-orchestrate.ibm.com/)
