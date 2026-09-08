# Agent Ops Bob Skills

Bob skill for **build-time evaluation, adversarial red-teaming, and runtime observability** of **watsonx Orchestrate (WXO)** agents, using the WXO Agent Development Kit (ADK).

## Overview

The `agent-ops` skill turns IBM Bob into an Agent Ops assistant for watsonx Orchestrate agents. When you ask Bob to evaluate, red-team, or observe a WXO agent, it runs a short interview to understand your environment (Developer Edition or SaaS), intent, and current state — then emits the exact `orchestrate` CLI commands for you to run in your terminal. Bob never runs mutating evaluations itself.

## Available Skills

| Skill | Zip | Use When |
|---|---|---|
| `agent-ops` | [`agent-ops.zip`](agent-ops.zip) | Validating, red-teaming, or observing a watsonx Orchestrate agent before (and after) deploying to SaaS |

---

### `agent-ops`

Five self-contained modules you can invoke in any order:

- **Eval** — `orchestrate evaluations quick-eval` (smoke test) and `evaluate --with-langfuse` (full evaluation with LLM-simulated users)
- **Benchmarks** — author test scenarios via `record`, `generate`, or hand-written JSON, with full schema validation
- **Analyze** — `analyze` and `analyze --mode enhanced`; metric thresholds and failure diagnosis (benchmark issue vs agent issue vs infra crash)
- **Red-teaming** — `list` / `plan` / `run` against an OWASP-Top-10-for-LLM attack catalog with severity ratings and remediation prompts
- **Observability** — traces CLI + Python SDK + Langfuse (local & hosted) + IBM Telemetry; 5-layer cost & latency reporting

Supports both **Developer Edition** (local server on `:4321`) and **SaaS** as first-class targets, and keeps in sync with current ADK semantics via a bundled `watsonx-orchestrate-adk-docs` MCP server.

---

## Installation

### Step 1 — Install the skill

The zip is pre-structured with `.bob/skills/<skill-folder>/` internally. Extract from your **project root**:

```bash
# From the root of your Bob workspace project
unzip agent-ops.zip
```

This creates:

```
.bob/skills/agent-ops/SKILL.md
```

(along with the skill's `reference/`, `examples/`, and `assets/` folders and `setup.sh`).

### Step 2 — Enable in IBM Bob

Open IBM Bob → Skills panel → enable `agent-ops`. Bob will use it as active context for every prompt in this workspace.

### Step 3 — Verify

Ask Bob: *"What Agent Ops capabilities do you have active?"*

---

## Usage Examples

Once activated, you can ask Bob:

- *"Help me evaluate this WXO agent before I deploy to SaaS"*
- *"Run red-teaming on my portfolio-advisor agent"*
- *"My eval results came back with Faithfulness 0.65 — what's wrong?"*
- *"Generate benchmark scenarios from these user stories"*
- *"How do I set up Langfuse so I can see cost per scenario?"*

Bob runs a 3-question interview, then drives the relevant module(s).

---

## What Bob Can Help You Build

1. **Pre-deployment validation**: quick-eval smoke tests and full LLM-simulated-user evaluations
2. **Benchmark authoring**: scenarios from recorded chat sessions (`record`) or rough stories (`generate`)
3. **Failure diagnosis**: interpreting `summary_metrics.csv` / `results.json` and isolating root cause
4. **Security testing**: adversarial red-teaming with severity ratings and remediation prompts
5. **Runtime observability**: trace search/export and Langfuse cost & latency analysis

---

## Prerequisites

Before using this skill, ensure you have:

- **watsonx Orchestrate ADK** with the `[agentops]` extra (`>= 2.6.0, < 3.0.0`)
- **Python 3.12** (3.11 may work; 3.13+ not yet supported)
- **Docker runtime** for Developer Edition (WXO server + Langfuse + Milvus + OpenSearch + ClickHouse, ~16 GB RAM)
- **`uv` / `uvx`** to launch the WXO docs MCP server
- **IBM Cloud + watsonx.ai** API key + project/space (RAG judges and red-teaming planner)
- **Langfuse keys** (optional) for cost & latency analysis

See [`.bob/skills/agent-ops/assets/PREREQUISITES.md`](agent-ops.zip) inside the zip for the full credential matrix, hardware requirements, network egress, and troubleshooting table.

## Skill Capabilities Summary

| Capability | Description |
|---|---|
| **Eval** | `quick-eval` smoke tests + full `evaluate --with-langfuse` runs |
| **Benchmarks** | `record` / `generate` / manual JSON with schema validation |
| **Analyze** | Metric thresholds + failure-diagnosis (benchmark vs agent vs infra) |
| **Red-teaming** | OWASP Top 10 for LLM attack catalog, severity + remediation |
| **Observability** | Traces CLI + SDK + Langfuse + IBM Telemetry, 5-layer cost/latency |
| **DevEd + SaaS parity** | Both environments first-class throughout |
| **Terminal-emitting** | Bob writes commands; you run them — no surprise mutations |

## Troubleshooting

**Skill doesn't appear after installation:**
1. Verify `.bob/skills/agent-ops/SKILL.md` exists
2. Restart Bob to refresh the skills list
3. Ensure the Skills button is enabled in your current mode

**Bob runs the eval itself instead of emitting a command:**
- This skill is terminal-emitting by design — Bob should write the `orchestrate …` command for you to run. If it tries to run mutating evals, remind it to emit the command block.

## Related

- [`../bob-modes/`](../bob-modes/) — Agent Ops Bob Modes
- [`../assets/`](../assets/) — Agent Ops evaluation SDK and sample agents
- [`../README.md`](../README.md) — Agent Ops building block overview
