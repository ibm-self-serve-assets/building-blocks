# Agent Ops

Your agent passes unit tests — but will it call the right tools with the right arguments when a real user asks an ambiguous question? Will it hallucinate tool calls that don't exist? Will it leak its system prompt under adversarial pressure? Will a single multi-turn conversation burn through your token budget?

**Agent Ops answers these questions before deployment.** This [Bob](https://bob.ibm.com) custom mode (IBM's AI code assistant) puts your watsonx Orchestrate (WXO) agent through rigorous, automated evaluation — LLM-simulated user conversations, tool-calling precision/recall metrics, RAG faithfulness scoring, per-turn token and cost analysis via Langfuse, and adversarial red-teaming. Every failure is traced to its root cause — whether that's the agent, the benchmark, or the infrastructure — with concrete fixes, not generic advice.

**Built-in safeguards** for the WXO ADK 2.6 eval-framework landmines: ancestor `.env` pollution (the silent hijacker of `WO_INSTANCE`/`WO_API_KEY`), explicit-token requirement in `config.yaml`, and the deprecated default judge model. Bob walks you through the pre-flight checks before every run, so you don't lose an afternoon to `iam.cloud.ibm.com` 400 errors.

## What You Need

**Required:**
- [Bob](https://bob.ibm.com) (IBM's AI code assistant)
- WXO Developer Edition (local server on port 4321 for ADK 2.6+, or 8080 on older builds)
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

1. Download `agent-ops.zip` from this repo
2. Unzip it into your agent project root:
   ```bash
   unzip agent-ops.zip -d /path/to/your/agent/project
   ```
   This places the `.bob/` folder and `.mcp.json` in your project, next to your agent. Bob will detect the mode automatically.

**Option B: Global mode**

1. Download and unzip `agent-ops.zip`
2. Append the contents of `.bob/custom_modes.yaml` to Bob's global config:
   ```
   ~/Library/Application Support/IBM Bob/User/globalStorage/ibm.bob-code/settings/custom_modes.yaml
   ```
3. Copy the `.bob/` folder and `.mcp.json` from the unzipped folder to your project root.

Then switch to the **🛡️ Agent Ops** mode in Bob's mode selector.

## How It Works

When you start a conversation, Bob asks what type of evaluation you need:

| Choice | What Bob does |
|--------|-------------|
| **(a) Quick connectivity check** | Verifies ADK, server, agent imported, tools accessible. Done in 2 minutes. |
| **(b) Full end-to-end evaluation** | Benchmarks + metrics + analysis + recommendations. The complete pipeline. |
| **(c) Cost and latency analysis** | Runs evaluation with Langfuse tracing, then queries the Langfuse API to produce a 5-layer cost/token analysis: per-scenario breakdown, per-turn context growth, cost patterns, data-driven recommendations, and production projections. |
| **(d) Red-teaming** | Adversarial security testing — prompt injection, data extraction, jailbreaking. |
| **(e) Something else** | Describe what you need and Bob tailors the workflow. |

Bob checks what already exists (ADK installed? server running? agent imported? benchmarks written? **stale ancestor `.env` polluting the eval framework?**) and **only does what's needed** — it won't repeat steps you've already completed.

## Evaluation Workflow

```
Phase 1: Setup → Phase 2: Smoke Test → Phase 3: Benchmarks → Phase 4: Evaluation → Phase 5: Analysis → Phase 6: Red-Teaming
```

1. **Setup** — Checks Developer Edition prerequisite, locates ADK, verifies server, imports agent, **runs the 4-check pre-flight (RULE 19)**
2. **Smoke Test** — Runs `quick-eval` with 2 scenarios as a connectivity check (Yes/No report)
3. **Benchmark Authoring** — Reads your agent's tool code first, writes benchmarks simple-to-complex, validates each with correctness + quality + dry-run checks
4. **Full Evaluation** — Runs benchmarks with LLM-simulated users via the gateway provider with explicit token + supported `model_id`
5. **Analysis & Diagnosis** — Interprets metrics, considers benchmark issues vs agent issues, implements fixes, asks about next steps
6. **Red-Teaming** — Plans and executes adversarial attacks, recommends guardrails. Plan generation requires a cloud-active env (RULE 1 + RULE 17 walk you through it)

## Cost & Latency Analysis

When you choose option (c), Bob produces a deep cost/latency report by querying the Langfuse API directly:

- **Per-scenario breakdown** — tokens, cost, pass/fail status
- **Per-turn context growth** — how tokens accumulate in multi-turn conversations (the #1 cost driver)
- **Cost patterns** — base cost, growth rate, input/output ratio, wasted spend on failures
- **Data-driven recommendations** — only what the data supports (not a generic checklist)
- **Production projection** — estimated monthly cost at your expected conversation volume

## Mode Contents

```
agent-ops/
├── .bob/
│   ├── custom_modes.yaml                # Mode definition with 19 mandatory rules
│   ├── workflow.md                      # 6-phase workflow + 3 appendices + 4-check pre-flight
│   ├── rules-agent-ops/
│   │   ├── 1_evaluation_workflow.xml    # Phase-by-phase steps with user context + STEP 3.5 (configure_eval_llm)
│   │   ├── 2_benchmark_authoring.xml    # JSON schema, DAG patterns, quality checklist, dry-run
│   │   ├── 3_metrics_and_diagnosis.xml  # Metric definitions, thresholds, diagnosis table
│   │   └── 4_red_teaming.xml            # Attack categories, remediation patterns, <cloud_required> block
│   └── reference-benchmarks/
│       ├── portfolio_advisor_benchmarks/  # 8 working scenario JSONs
│       └── stories_sample.csv             # Sample stories CSV for generate command
├── .mcp.json                            # WXO ADK docs MCP server
└── .gitignore                           # Ignores eval outputs and macOS junk
```

## MCP: ADK Docs Search

The `.mcp.json` connects Bob to the live WXO ADK documentation server. Bob can search the official ADK docs for command syntax, flags, and best practices — without leaving the conversation.

Requires `uvx` — install with `pip install uv`.

## Key Rules

- Bob asks what type of evaluation you need before doing anything
- Developer Edition is the default — cloud is used **only** for red-teaming `plan` (which needs an LLM)
- **RULE 17** — Cloud-env selection: read existing config first, reuse cached tokens, ask which instance the user's API key is for, never auto-pick or hardcode
- **RULE 18** — Eval framework LLM config: explicit token in `config.yaml`, gateway provider, override the deprecated default model
- **RULE 19** — Ancestor `.env` pollution: pre-flight check before every quick-eval/evaluate run
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

### `model_not_supported` / `Model 'meta-llama/llama-3-405b-instruct' was not found`

The eval framework's default model is deprecated on eval-fw 1.2.x. Fix:

1. Run `orchestrate env activate local` (this populates `~/.cache/orchestrate/credentials.yaml`)
2. Read your local mcsp token:
   ```bash
   python3 -c "import yaml; print(yaml.safe_load(open('$HOME/.cache/orchestrate/credentials.yaml'))['auth']['local']['wxo_mcsp_token'])"
   ```
3. Create `config.yaml` in your project root with the token explicit:
   ```yaml
   auth_config:
     url: http://localhost:4321
     tenant_name: local
     token: <paste the JWT here>
   provider_config:
     provider: "gateway"
     model_id: "meta-llama/llama-3-3-70b-instruct"
   ```
4. Pass `--config ./config.yaml` on every `quick-eval` / `evaluate` invocation:
   ```bash
   orchestrate evaluations quick-eval \
     --test-paths ./benchmarks \
     --tools-path ./<your-agent>/tools \
     --output-dir ./quick_eval_results \
     --config ./config.yaml
   ```

`--config` is supported on `evaluate` and `quick-eval` only — not on `generate`, `red-teaming plan`, or `red-teaming run`.

**Note:** judges in `agentops/evaluation_package.py` are hardcoded to the deprecated 405b for now. The conversation runs and emits Langfuse traces normally; only the post-conversation metrics summary table is broken on this version of the eval framework. Langfuse-focused workflows are not affected.

### `400 Bad Request` from `iam.cloud.ibm.com/identity/token`

This is the ancestor-`.env` pollution case. `dotenv.load_dotenv()` walks UP the directory tree, so a stale `.env` in any ancestor of your project (e.g., `~/src/.env`) gets auto-loaded and silently overrides your `config.yaml`. Detect:

```bash
cd <project-dir> && python3 -c "from dotenv import find_dotenv; print(repr(find_dotenv()))"
```

If the path is outside your project, move it aside for the eval session:

```bash
mv <ancestor>/.env <ancestor>/.env.disabled
```

(Restore after.)

### `Scope not found: Scope{scopeType='SERVICE', scopeId='<uuid>'}`

The active orchestrate env's instance UUID doesn't match the API key. Bob walks you through this in RULE 17 — ask which instance your key is actually for, then either activate the matching env or `orchestrate env add` a new one with the correct URL and explicit `--type`.

## Learn More

- [Bob — IBM's AI Code Assistant](https://bob.ibm.com)
- [WXO ADK Documentation](https://developer.watson-orchestrate.ibm.com/)
