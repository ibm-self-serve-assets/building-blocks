# Cost Management

Part of **[Control](../)** in the **[AI Control Plane](../../)**.

AI agents turn every interaction into model calls, tool calls, and tokens. Without visibility, spend grows quietly: a looping agent, a verbose prompt, or an oversized model can burn through a budget before anyone notices. **Cost Management** gives you that visibility, starting at the level of each agent interaction.

---

## Why This Matters

- **Agent cost is hard to predict.** The same request can take one model call or ten, depending on how the agent reasons and which tools it calls.
- **Token budgets burn silently.** Without per-interaction tracking, runaway loops and oversized prompts show up only on the invoice.
- **Cost has to be weighed against quality.** Choosing a smaller model or a shorter prompt only makes sense when you can see both the cost and the evaluation results.

---

## Available Today — Agent Cost and Token Tracking

For **watsonx Orchestrate agents** there are three places to look, from tokens to dollars:

| Source | What you get | Where |
|---|---|---|
| **Agentic Control Plane** (product UI) | token consumption, model usage, call volume per agent; FinOps view in preview | watsonx Orchestrate → Agentic Control Plane |
| **Platform traces** | tokens and model per generation inside every conversation's span tree; token totals per run on the runs API | [Agent Ops](../agent-ops/) → observability |
| **Langfuse** | **cost in dollars** per trace, session, model, and tag — once the integration is configured and the models are priced | this folder |

| Capability (Langfuse) | What It Does |
|---|---|
| **Cost per scenario** | tokens, cost, and pass or fail for every evaluation scenario, so expensive paths show up before production |
| **Context growth per turn** | how cost climbs as multi-turn conversations grow, the main driver of multi-turn cost |
| **Cost patterns** | base cost, growth rate, input-to-output token ratio, spend wasted on failed runs |
| **Production projection** | cost at your expected conversation volume, with data-driven recommendations |

Langfuse receives traces from watsonx Orchestrate through the instance's Langfuse integration (SaaS: `orchestrate settings observability langfuse configure …`; Developer Edition: `orchestrate server start -l`). The integration is **one setting per instance** — on a shared instance it belongs to the instance owner. Cost appears when Langfuse has pricing for the agent's model; watsonx-served models need their pricing registered first. Latency and tokens are always recorded.

### Where the code lives

- [`assets/traces/`](assets/traces/) — `trace_cost.py`: tokens and dollars from platform traces (fetches by trace id with the required time window, joins an Agent Ops run by thread id, per-model and per-agent breakdown, CSV), with `prices.yaml`, an indicative list-price table.
- [`assets/langfuse/`](assets/langfuse/) — setup for the Langfuse integration (SaaS and Developer Edition), model pricing registration, the cost report script, and the five-layer cost analysis guide (`COST-ANALYSIS.md`).

---

## Coming Soon — Enterprise Cost Management

- **Allocation** of AI spend by team, use case, or model.
- **Budgets and alerts** before costs become unmanageable.
- **Optimization** — identifying waste and cost per outcome across AI workloads.

---

### [Bob Skills](bob-skills/)

The `cost-management` skill ([`bob-skills/cost-management.zip`](bob-skills/), also at [`ibm-bob/skills/cost-management/`](../../../ibm-bob/skills/cost-management/)) gives Bob the expertise to answer *what does this agent cost, why, and what would change it*: tokens and dollars from platform traces (`trace_cost.py`, with an indicative price table), the Langfuse integration and model pricing, the five-layer cost report with cost per successful journey, and the optimization levers with their re-test. Interview-first; Bob emits the commands and never configures an instance it does not own.

For evaluation, rubrics, red-teaming, and reading traces for correctness use the [Agent Ops skill](../agent-ops/bob-skills/).

📖 Docs: [Cost Management](https://ibm-self-serve-assets.github.io/building-blocks-docs/ai-core/control/cost-management/)
