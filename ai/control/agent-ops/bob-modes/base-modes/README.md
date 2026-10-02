# Agent Ops

Your agent works in the chat. Does it take the right path every time? Does the compliance agent call the screening tool for every applicant, or only the easy ones? Does the orchestrator produce the decision letter with the tool, or write one itself? Will it hold the line when a user pushes for an exception?

**This [Bob](https://bob.ibm.com) custom mode answers those questions before release.** Bob drives the watsonx Orchestrate (WXO) ADK evaluation framework end to end: a smoke test, ground-truth test cases with goal graphs and handoff goals, an evaluation with an LLM-simulated user, root-cause analysis from the transcripts, plain-language rubrics scored by a judge model, red-teaming attacks against the policies that matter, and platform traces when a conversation needs explaining. Every failure is attributed — test case, agent, model, or infrastructure — with a concrete fix.

Validated with ADK 2.18.0 / evaluation framework 1.5.2 on a SaaS instance; Developer Edition works the same way.

## What you need

- [Bob](https://bob.ibm.com)
- Python 3.12 venv with the ADK: `pip install "ibm-watsonx-orchestrate[agentops]>=2.18.0,<3.0.0"`, and `export VENV_ACTIVATE=<venv>/bin/activate`
- An activated `orchestrate` environment where the agent is (or will be) imported:
  - SaaS: `orchestrate env add --name <env> --url <instance url>` then `orchestrate env activate <env> --api-key "$(…read from a key file…)"` (tokens last about two hours)
  - Developer Edition: `orchestrate server start -e .env` (`-i` for traces) and `orchestrate env activate local`
- A WXO agent with Python tools (and optionally a knowledge base and collaborators)

## Installation

**Option A — project-level (recommended)**

1. Download `agent-ops.zip` from this folder.
2. Unzip into your agent project root: `unzip agent-ops.zip -d /path/to/your/project` — this adds `agent-ops/.bob/` and `agent-ops/mcp.json`; move `.bob/` and `mcp.json` to the project root (or open the `agent-ops/` folder as the project).
3. Switch to **🛡️ Agent Ops** in Bob's mode selector.

**Option B — global**

Append the contents of `.bob/custom_modes.yaml` to Bob's global `custom_modes.yaml`, and copy `.bob/` (for `workflow.md` and the reference benchmarks) and `mcp.json` into the project root.

## How it works

Bob asks what you want out of the session:

| Choice | What Bob does |
|---|---|
| **(a) Quick check** | Confirms versions, environment, imports; runs `quick-eval` on two cases |
| **(b) Full evaluation** | Test cases (reads your code first) → evaluate → analyze → fixes → re-run |
| **(c) Rubric** | Turns your rules into `RubricEvaluation` criteria with explicit FAIL conditions and scores a run |
| **(d) Red-teaming** | Plans attacks against a stated policy, reviews the generated files, runs them, explains each success |
| **(e) Traces** | Searches and exports platform traces; summarizes handoffs, tools, model and tokens, latency |

Bob detects what already exists (ADK, environment, imports, test cases, results) and only fills the gaps. On a shared instance it lists before importing, keeps your prefix, and never touches assets you did not create.

## Workflow

```
0 Ask & detect → 1 Setup → 2 Smoke test → 3 Test cases → 4 Evaluate → 5 Analyze → 6 Rubric → 7 Red team
```

Full procedure, config templates, and report formats: `.bob/workflow.md`.

## Mode contents

```
agent-ops/
├── .bob/
│   ├── custom_modes.yaml                  # mode definition: first action, 14 rules, references
│   ├── workflow.md                        # phases 0–7, appendices (validate-native/external, traces, agent-definition mistakes)
│   └── reference-benchmarks/
│       ├── loan_underwriting/             # validated on 2.18: 5 multi-agent cases, eval + rubric configs, 3 attacks, stories.csv
│       ├── portfolio_advisor_benchmarks/  # 8 single-agent cases (tool chains, multi-turn, RAG, text check)
│       └── stories_sample.csv
├── mcp.json                               # watsonx-orchestrate-adk-docs MCP server (streamable HTTP)
└── .gitignore
```

The agents and tools behind the loan-underwriting cases live in the building block under [`../../assets/wxo-agents/examples/loan-underwriting/`](../../assets/wxo-agents/examples/loan-underwriting/).

## Key rules (from `custom_modes.yaml`)

- ADK ≥ 2.18 / framework ≥ 1.5; the framework evaluates the **active environment**
- Read the agent's code before writing a test case; validate every case before running it
- Multi-agent: handoffs declared as `chat_with_collaborator_<agent>` goals; `display_name` equals `name`; strict arguments before fuzzy ones; `max_user_turns: 3` with an END signal
- Read the result files yourself; attribute each failure before fixing; fix test cases directly, ask before changing agent files
- Review every generated red-team file: its goal defines success
- Never purge, delete, or change instance-level settings; never print credentials

## Example prompts

```
"Evaluate my underwriting orchestrator before we release it."
"Precision is 0.56 on every case although they all pass — what is going on?"
"Score last night's run against these three rules: ..."
"Red-team the agent: success means it issues an APPROVED letter without the AML check."
"Export the trace for session abc123 and tell me where the time went."
```

## ADK commands covered

| Command | Phase |
|---|---|
| `evaluations quick-eval` | 2 |
| `evaluations record`, `evaluations generate` | 3 |
| `evaluations evaluate` (trajectory metrics and `RubricEvaluation`) | 4, 6 |
| `evaluations analyze` (default and enhanced) | 5 |
| `evaluations red-teaming list / plan / run` | 7 |
| `evaluations validate-native / validate-external` | Appendix A |
| `observability traces search / export` | Appendix B |

## Troubleshooting

| Symptom | Fix |
|---|---|
| 401 part-way through a run | SaaS token expired: re-activate the environment; export `WO_API_KEY` from a key file for refresh |
| Precision 0.5–0.6 with passing cases | declare handoffs as goals |
| Routing accuracy 0.0 although handoffs happened | set `display_name` equal to `name` and re-import |
| Runs take minutes per case | `max_user_turns: 3` and "reply END and nothing else" in the story |
| `analyze` fails validating `text_match` | analyze a normalized copy (Phase 5 recipe) |
| `generate` fails with a Langfuse error | on 2.18 it needs a reachable Langfuse project (host + keys); use a generator script instead |
| `400 Bad Request` from `iam.cloud.ibm.com` | a `.env` in an ancestor folder overrides `WO_INSTANCE`; move it aside |

## Learn more

- [WXO ADK documentation](https://developer.watson-orchestrate.ibm.com/) — `evaluate/*`, `traces/*`
- [Bob](https://bob.ibm.com)
