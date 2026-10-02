# Agent Ops Bob Skills

Bob skill for **build-time evaluation, rubric scoring, red-teaming, and trace inspection** of **watsonx Orchestrate (WXO)** agents, using the evaluation framework in the WXO Agent Development Kit (ADK 2.18+).

## Overview

The `agent-ops` skill turns IBM Bob into an evaluation specialist for watsonx Orchestrate agents. Ask Bob to test, score, attack, or trace a WXO agent and it runs a short interview (environment, intent, current state), proposes a plan, runs read-only checks, and emits the exact `orchestrate` commands for you to run in your terminal. Bob then reads the result files and explains them. Bob never runs evaluations, imports, or installs itself, and never touches assets it did not create on a shared instance.

The same skill is published unpacked at [`ibm-bob/skills/agent-ops/`](../../../../ibm-bob/skills/agent-ops/) and inside the repo-wide `skills.zip`.

## Available skills

| Skill | Zip | Use when |
|---|---|---|
| `agent-ops` | [`agent-ops.zip`](agent-ops.zip) | Validating a WXO agent before release or after a change; writing ground-truth test cases; diagnosing failures; turning policies into rubrics; red-teaming; reading traces |

### `agent-ops`

Six modules you can invoke in any order:

- **Eval** — `quick-eval` (smoke test without ground truth) and `evaluate` (LLM-simulated user, per-case metrics)
- **Test cases** — `record`, `generate`, generator scripts, or hand-written JSON; goal DAGs, handoff goals, `arg_matching`
- **Analyze** — `analyze` (default and enhanced); metric meaning; attribution: test case, agent, model, or infrastructure
- **Rubric** — `RubricEvaluation`: plain-language rules scored pass/fail by a judge model, with reasoning
- **Red-teaming** — `list` / `plan` / `run` over 15 attacks; attack-file review; remediation
- **Observability** — platform traces by CLI, Python, and REST: handoffs, tool calls, model and tokens, latency

Supports **SaaS** (IBM Cloud or AWS hosted) and **Developer Edition**; ships the validated `examples/loan_underwriting/` assets and an MCP server entry for live ADK docs search.

Runtime controls are covered by the Agent Controls skill (Guardrails), cost in dollars by the Cost Management building block, LangGraph/LangChain evaluation by the Model Evaluation skill.

---

## Installation

### Step 1 — Install the skill

The zip is pre-structured with `.bob/skills/agent-ops/` inside. Extract it from your **project root**:

```bash
unzip agent-ops.zip
```

This creates `.bob/skills/agent-ops/SKILL.md` along with `reference/`, `examples/`, `assets/`, `README.md`, `USAGE-GUIDE.md`, and `setup.sh`.

### Step 2 — Enable in IBM Bob

Open IBM Bob → Skills panel → enable `agent-ops`.

### Step 3 — Prerequisites

- Python 3.12 venv with `pip install "ibm-watsonx-orchestrate[agentops]>=2.18.0,<3.0.0"` (or run `.bob/skills/agent-ops/setup.sh`), and `export VENV_ACTIVATE=<venv>/bin/activate`
- An activated `orchestrate` environment pointing at the instance where the agent is imported (SaaS tokens expire after about two hours)
- Developer Edition only: a Docker runtime

Details: `.bob/skills/agent-ops/assets/PREREQUISITES.md` inside the zip.

### Step 4 — Verify

Ask Bob: *"What Agent Ops capabilities do you have active?"*

---

## Usage examples

- *"Evaluate this agent before I ship it"*
- *"Write five test cases for the refund flow and run them"*
- *"Precision is 0.56 but every case passed — what is going on?"*
- *"Turn these compliance rules into a rubric and score last night's run"*
- *"Red-team the orchestrator for instruction override and crescendo"*
- *"Show me the trace for the conversation that approved the wrong applicant"*

## Skill capabilities summary

| Capability | Description |
|---|---|
| **Eval** | `quick-eval` smoke tests and full `evaluate` runs from a config file |
| **Test cases** | schema, DAG patterns, handoff goals, `arg_matching`, `record` / `generate` / generator scripts, validation table |
| **Analyze** | framework-1.5 metric columns, curated thresholds, diagnosis table, attribution |
| **Rubric** | `RubricEvaluation` criteria and results |
| **Red-teaming** | attack catalogue, `plan` review, attack-file schema, remediation |
| **Observability** | traces search/export, Python `TracesController`, REST, Agentic Control Plane |
| **SaaS + Developer Edition** | both first-class; the framework evaluates the active environment |
| **Terminal-emitting** | Bob writes commands; you run them — no surprise mutations on shared instances |

## Troubleshooting

**Skill doesn't appear:** check `.bob/skills/agent-ops/SKILL.md` exists, restart Bob, confirm the Skills button is enabled in the current mode.

**Bob runs an evaluation itself:** the skill is terminal-emitting by design; remind it to emit the command block.

## Related

- [`../bob-modes/`](../bob-modes/) — the Agent Ops Bob mode (hands-on variant: Bob runs the commands)
- [`../assets/`](../assets/) — scripts, the single-agent sample, and the loan-underwriting example
- [`../README.md`](../README.md) — Agent Ops building block overview
