# Cost Management Bob Skills

Bob skill for **measuring, explaining, and reducing the cost of watsonx Orchestrate (WXO) agents** — from tokens to dollars, next to the quality numbers from the Agent Ops suite.

## Overview

The `cost-management` skill turns IBM Bob into a cost analyst for watsonx Orchestrate agents. Ask what an agent, a conversation, an evaluation run, or a use case costs and Bob runs a short interview (instance and ownership, intent, current state), proposes a plan, runs read-only checks, and emits the commands for you to run — then reads the output and writes the report. Bob never configures the Langfuse integration on an instance you do not own (it is one setting per instance) and never edits agents: optimizations are proposals with a re-test.

The same skill is published unpacked at [`ibm-bob/skills/cost-management/`](../../../../ibm-bob/skills/cost-management/) and inside the repo-wide `skills.zip`.

## Available skills

| Skill | Zip | Use when |
|---|---|---|
| `cost-management` | [`cost-management.zip`](cost-management.zip) | Baselining cost per conversation or per successful journey; connecting Langfuse and pricing models; a five-layer cost report; choosing optimization levers; comparing two versions or models on cost and quality |

### `cost-management`

Four modules, any order:

- **Sources** — watsonx Orchestrate Agentic Control Plane (tokens), runs API usage, platform traces priced with an indicative table (`scripts/trace_cost.py`: fetch by trace id or by Agent Ops run, per-model and per-agent breakdown, CSV)
- **Langfuse** — ownership gate, integration (`settings observability langfuse configure`), model pricing, verification, attribution by session and tag (`scripts/langfuse_cost_report.py`)
- **Report** — per scenario → context growth per turn and handoff → patterns → data-backed recommendations → projection; cost × quality with dollars per successful journey
- **Optimize** — levers (turns, handoffs, model per agent, prompt and tool size, tool outputs, retrieval, evaluation cost, runtime cost guardrails), estimates from the data, and the re-test with the Agent Ops suite

Validated with ADK 2.18.0 on an IBM Cloud SaaS instance against the loan-underwriting example from the Agent Ops building block.

---

## Installation

```bash
unzip cost-management.zip          # from your project root; creates .bob/skills/cost-management/
```

Enable `cost-management` in IBM Bob → Skills.

Prerequisites: Python 3.12 venv with the ADK (`pip install "ibm-watsonx-orchestrate[agentops]>=2.18.0,<3.0.0"`) and an activated environment on the instance (the scripts reuse its token cache); `pip install -U langfuse` only for the Langfuse path.

## Usage examples

- *"What did last night's evaluation run cost, per case, and which cases failed?"*
- *"v2 passes more cases than v1 — what is the cost per successful journey of each?"*
- *"Set up Langfuse for this instance and price gpt-oss-120b and granite-4-h-small"*
- *"Where do 12,000 input tokens per conversation come from, and what would cut them?"*

## Related

- [`../assets/traces/`](../assets/traces/) — `trace_cost.py` and `prices.yaml`
- [`../assets/langfuse/`](../assets/langfuse/) — Langfuse setup, pricing, cost report, five-layer analysis guide
- [`../../agent-ops/bob-skills/`](../../agent-ops/bob-skills/) — the Agent Ops skill (evaluation, rubrics, red-teaming, traces for correctness)
