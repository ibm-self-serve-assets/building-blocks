# Cost Management — Bob skill (watsonx Orchestrate)

A Bob skill that answers **what a watsonx Orchestrate agent costs, why, and what would change it** — from tokens to dollars, always next to the quality number from the Agent Ops suite.

Validated with ADK 2.18.0 on an IBM Cloud SaaS instance against the loan-underwriting system shipped with the Agent Ops building block.

## What the skill does

Bob runs a short interview (instance and ownership, intent, current state), proposes a plan, runs read-only checks, and emits the commands for you to run. It then reads the output and writes the report.

| Module | What you get |
|---|---|
| **Sources** | Tokens for a conversation, an evaluation run, or a use case from platform traces (or the runs API), priced with a list-price table; a baseline per use case |
| **Langfuse** | The instance connected to a Langfuse project you own, models priced, dollars verified, attribution by session and tag |
| **Report** | Cost per scenario → context growth per turn → patterns → data-backed recommendations → projection; cost × quality (dollars per successful journey) |
| **Optimize** | The levers that move the number, an estimate from the data, and the re-test that proves quality held |

## When to use it

- "How much does this agent cost per conversation, and per *successful* conversation?"
- "v2 passes more cases — is it more expensive?"
- "Set up Langfuse so finance can see dollars per use case"
- "Where do 12,000 input tokens per conversation come from?"
- "Can a cheaper model take the easy steps without breaking tool calling?"

## When not to use it

| Need | Use instead |
|---|---|
| Evaluate behaviour, write test cases, red-team, read a trace for correctness | the `agent-ops` skill |
| Runtime controls (rate limits, output length, PII) | the `agent-controls` skill (Guardrails building block) |
| Cloud infrastructure FinOps (Apptio, Turbonomic) | the Optimize building blocks |

## Prerequisites

| Component | Requirement |
|---|---|
| Python | 3.12 venv; `pyyaml` (bundled with the ADK) |
| ADK | `pip install "ibm-watsonx-orchestrate[agentops]>=2.18.0,<3.0.0"` and an activated environment on the instance (the scripts reuse its token cache) |
| Traces | SaaS: on by default, identity with admin rights; Developer Edition: `orchestrate server start -e .env -i` |
| Langfuse path | `pip install -U langfuse`; `LANGFUSE_HOST`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` for a project the instance exports to; instance ownership to configure the export |
| Prices | `assets/prices.yaml` (indicative) or the provider's current price list |

## What is in the skill

```
cost-management/
├── SKILL.md                      # interview, rules, dispatch, field notes
├── README.md
├── reference/
│   ├── module-sources.md         # Control Plane, runs API, traces REST recipe, trace_cost.py, baselines
│   ├── module-langfuse.md        # integration, pricing, verification, attribution, failures
│   ├── module-report.md          # five-layer report, cost × quality join, templates
│   └── module-optimize.md        # levers, estimates, routing by agent, runtime cost controls, re-test
├── assets/prices.yaml            # indicative USD per 1M tokens, with source and date
└── scripts/
    ├── trace_cost.py             # tokens and dollars from platform traces (files or --trace-id), --eval-run join, CSV
    └── langfuse_cost_report.py   # Langfuse pricing registration and cost per session/model for a window
```

## Install

```bash
cp -r cost-management <your-repo>/.bob/skills/
```

Then ask Bob, for example: *"What did the last evaluation run of the underwriting agent cost, per case, and which cases failed?"*

## Design properties

- **Two cost measures, named.** Model-inference cost (tokens × price) for design comparisons and per-token billing; invoice cost depends on the WXO plan — the skill says which one it is quoting.
- **Ownership gate.** The Langfuse integration is one setting per instance; Bob never emits `configure` on an instance the user does not own.
- **Cost next to quality.** Every report joins the Agent Ops run when one exists; dollars per successful journey is the headline.
- **Labelled prices.** Every figure carries its price source and date; unpriced models stay in tokens.

Source of truth: https://developer.watson-orchestrate.ibm.com/ and https://langfuse.com/docs
