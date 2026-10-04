---
name: cost-management
description: Measure, explain, and reduce the cost of watsonx Orchestrate (WXO) agents. Use when asked what an agent, a conversation, an evaluation run, or a use case costs; where the tokens go; how to turn platform traces or Langfuse data into dollars; how to set up the Langfuse integration and model pricing; how to compare cost against evaluation quality (cost per successful journey); or which levers cut spend (model per agent, prompt and tool size, turns, handoffs, runtime controls). Three sources - watsonx Orchestrate Agentic Control Plane (tokens), platform traces (tokens per generation, priced with a list-price table), Langfuse (dollars per trace, session, model, tag). Interview-first; emits commands; never changes an instance's Langfuse integration unless the user owns the instance.
---

# Cost Management (watsonx Orchestrate)

This skill answers "what does this agent cost, why, and what would change it" for watsonx Orchestrate agents, from tokens to dollars, and ties every cost number to a quality number from the Agent Ops suite. Targets: **SaaS** (IBM Cloud or AWS hosted) and **Developer Edition**.

**Stance:** ask first, emit commands second, execute rarely. Bob auto-runs only fast, read-only diagnostics; everything that writes, configures, or calls an LLM is emitted for the user to run.

**Validated against:** ADK 2.18.0 on an IBM Cloud SaaS instance (trace fields observed 2026-10-02) with the loan-underwriting system from the Agent Ops building block. Statements marked *observed* come from those runs; the ADK docs and the provider's price list win if they disagree.

**Two cost measures, say which one you mean:**
- **Model-inference cost** — tokens × a per-token price. Comparable across designs, and the actual cost when the model is billed per token (watsonx.ai, or third-party providers through the model gateway). This is what the scripts compute.
- **Invoice cost** — what the customer pays. WXO SaaS plans meter usage by plan, not per token; confirm how the plan meters before quoting an invoice figure.

---

## First action — one-line prereq notice, then a 3-question interview

> Before we start: for tokens and dollars from platform traces I need the ADK (2.18+) with an activated `orchestrate` environment on the instance; for Langfuse I need read access to the Langfuse project the instance exports to. Nothing gets configured on the instance unless you own it.

### Expert escape hatch

If the opening message names a concrete action (*"how much did yesterday's evaluation run cost"*, *"register pricing for granite-4-h-small"*, *"compare v1 and v2 cost per successful case"*), skip the interview, name the module in one line, and run only its read-only diagnostics.

### Interview

**Q1 — Environment and ownership**
> Which instance, and do you own it?
> (a) SaaS on IBM Cloud · (b) SaaS on AWS · (c) Developer Edition · (d) on-premises
> Is the instance shared with other teams? (Decides whether the Langfuse integration may be touched at all.)

**Q2 — Intent (multi-select)**
> 1. Baseline — tokens and dollars for a conversation, an evaluation run, or a use case, from platform traces
> 2. Langfuse — connect the instance, price the models, verify dollars appear
> 3. Report — cost per scenario, context growth, patterns, recommendations, projection (and cost × quality)
> 4. Optimize — pick levers, estimate the saving, define the re-test
> 5. Compare — two versions, two models, or two designs, cost per successful journey

**Q3 — Current state**
> - Does the instance export to Langfuse already (`orchestrate settings observability langfuse get`)? Whose project?
> - Are the agent's models priced anywhere (Langfuse model definitions, a price table)?
> - Is there an Agent Ops run folder for the same conversations (`summary_metrics.csv`, `<case>.metadata.json`)?
> - Expected volume (conversations per day) for projections?

After Q3, present a one-screen plan, then run the pre-flight for the first module.

---

## Mandatory rules

**RULE 1 — Interview first** (escape hatch excepted).

**RULE 2 — Read-only diagnostics only.** Bob may auto-run: `orchestrate env list`, `orchestrate models list`, `orchestrate settings observability langfuse get` (shows whether an integration exists; never print keys from it), `orchestrate observability traces search --last 1h --limit 5`, `pip show ibm-watsonx-orchestrate langfuse`, file reads in the project. Everything else is emitted: `langfuse configure/remove`, model pricing registration, `server start`, scripts that call APIs, `pip install`, git writes.

**RULE 3 — Ownership gate for Langfuse.** The Langfuse integration is **one setting per instance**; configuring it replaces whatever another team set. Emit `settings observability langfuse configure` only when the user states they own the instance (or the owner asked). On a shared instance, use platform traces instead.

**RULE 4 — Never leak credentials.** API keys, bearer tokens, Langfuse secret keys, and instance ids never appear in chat. Tokens are read from `~/.cache/orchestrate/credentials.yaml` inside the emitted command; Langfuse keys come from environment variables the user exports.

**RULE 5 — Prices are inputs, labelled.** Every dollar figure names its price source and date (`assets/prices.yaml` is an indicative list; the provider's current price list and the customer's contract override it). Unpriced models are reported as tokens, never silently as $0.

**RULE 6 — Cost next to quality.** A cost number without the matching journey success (or rubric) number is not a result. Join cost to the Agent Ops run when one exists (`module-report.md`); when none exists, say so and propose running the suite.

**RULE 7 — Traces API limits (observed on SaaS).** Observations need `fromStartTime`/`toStartTime`, at most 4 hours apart; a few lookups per minute. Fetch in slices and pace the calls; cache what you fetched.

**RULE 8 — Optimization is a proposal plus a re-test.** Bob never edits agents, models, or policies on the instance. It proposes one lever at a time, estimates the saving from the data, and names the re-test (the Agent Ops suite plus the cost report on the same cases).

**RULE 9 — Venv propagation and shared-instance hygiene** as in the agent-ops skill: `source "$VENV_ACTIVATE" && \` on every emitted block; list before you touch; never change assets you did not create.

---

## Module dispatch

| Intent | Module | Reference file |
|---|---|---|
| 1 baseline, 5 compare | sources | `reference/module-sources.md` |
| 2 Langfuse | langfuse | `reference/module-langfuse.md` |
| 3 report, 5 compare | report | `reference/module-report.md` |
| 4 optimize | optimize | `reference/module-optimize.md` |

Modules are independent. Typical sequence: sources (baseline) → report → optimize → re-test with Agent Ops → report again. Langfuse is optional; it is the path to dollars with the least custom code when the instance is yours.

---

## Pre-flight checks (read-only)

| Check | Command | If it fails |
|---|---|---|
| `$VENV_ACTIVATE` set | `echo "VENV_ACTIVATE=${VENV_ACTIVATE:-UNSET}"` | ask once |
| ADK version | `pip show ibm-watsonx-orchestrate` → 2.18+ | emit upgrade |
| Active environment | `orchestrate env list` | emit `env activate <env> --api-key "$(...)"` (SaaS tokens expire after about two hours) |
| Traces reachable | `orchestrate observability traces search --last 1h --limit 5` | DevEd: server needs `-i`; SaaS: identity needs admin rights (403), or no traffic in the window |
| Langfuse integration | `orchestrate settings observability langfuse get` | none configured → platform traces, or `module-langfuse.md` if the user owns the instance |
| Langfuse keys (Langfuse path only) | `echo "LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY:+SET}${LANGFUSE_PUBLIC_KEY:-UNSET}"` | ask the user to export them |
| Price table | `assets/prices.yaml` covers the models in `orchestrate models list` that the agents use | add rows (provider price list) before reporting dollars |

---

## Canonical command format

````
**Run this in your terminal** — <purpose>:

```bash
# <comment per non-obvious flag>
source "$VENV_ACTIVATE" && \
<command>
```

When it finishes, paste <the output path | the last 20 lines | y/n> so I can <read it | proceed>.
````

---

## Quick reference

### Sources (tokens → dollars)
- **watsonx Orchestrate Agentic Control Plane** (product UI): visibility into token usage and LLM calls per agent, and usage over time. Tokens, not dollars.
- **Runs API**: `message.completed` carries `usage.token_usage.total_tokens` and `usage.model_usage[]` (`model_name`, `provider`, `token_usage.prompt_tokens/completion_tokens/total_tokens`) — per-run tokens with no extra call.
- **Platform traces**: every conversation is a trace; `GENERATION` observations carry `model`, `usage.input/output/total`, `agentId`, and `metadata.attributes["langfuse.session.id"]` (= the conversation thread id). `scripts/trace_cost.py` fetches traces by id (with the required time window), prices them with `assets/prices.yaml`, and joins them to an Agent Ops run folder.
- **Langfuse**: dollars per trace/session/model/tag once the instance exports there and the models are priced; `scripts/langfuse_cost_report.py`.

### Langfuse
- `orchestrate settings observability langfuse configure --url <host>/api/public/otel --api-key <sk> --health-uri <host> --config-json '{"public_key": "<pk>"}'` (owner only); Developer Edition `server start -l`.
- Price models with `langfuse_cost_report.py --register-model …` (per-million prices from the price list); pricing applies to generations ingested afterwards.

### Report
- Five layers: per scenario → per turn (context growth) → patterns (base cost, growth rate, in:out ratio, wasted spend, concentration) → data-backed recommendations → projection at expected volume.
- Cost × quality: `$ per successful journey` = cost of the run ÷ `is_success` count; show both versions side by side.

### Optimize
- Levers in order of typical payoff: fewer turns and handoffs (context growth) → model per agent (route easy steps to a cheaper model; re-check tool calling) → instructions and tool docstrings (base cost) → tool output size → knowledge-base chunking → evaluation cost itself (`max_user_turns`, `n_runs`) → runtime controls (Rate Limiter, Output Length Guard) as cost guardrails.
- Model policies in WXO are load-balance/fallback across virtual models, not cost-based routing; routing by complexity is agent design.

---

## Field notes (observed; re-check on upgrade)

1. **`orchestrate observability traces export` fails on 2.18.0 against this SaaS API** with `400 VALIDATION_ERROR: fromStartTime is required` (the Python `fetch_trace_observations` has the same gap). `GET /v1/agentops-v3/observations?traceId=<id>&fromStartTime=<ISO Z>&toStartTime=<ISO Z>&limit=500` works; `trace_cost.py --trace-id` wraps it.
2. **Trace fields.** Response is `{"data": [...], "meta": {"cursor": ...}}`. Generations: `type: GENERATION`, `name: WatsonxChatModel.chat`, `model` without the provider prefix (`openai/gpt-oss-120b`), `usage {input, output, total}`, `agentId`, `latency`, `timeToFirstToken`. Cost fields (`calculatedTotalCost`, `inputPrice`, …) exist but are 0/null. `GET /v1/agentops-v3/models` returns a Langfuse-style list of built-in model definitions (`modelName`, `matchPattern`, tokenizer, prices), which suggests the platform could price generations natively; whether registering a model there is permitted or documented is unverified — do not try it on a shared instance, ask the instance owner. Until then price locally (`trace_cost.py`) or in Langfuse.
3. **Join key.** `metadata.attributes["langfuse.session.id"]` (also `thread_id`) equals the thread id the evaluation framework writes to `<case>.metadata.json`; that is how a trace becomes "tc02, failed, $0.0031".
4. **Window and rate.** 4-hour maximum window, "within the last 30 days", a few calls per minute; a trace is complete about 15 seconds after the run ends.
5. **Where tokens go.** In the loan example one conversation = 12 generations ≈ 12k input / 1k output tokens: every handoff restarts a context, and input dominates 10:1. Turn count and handoff count drive cost more than output length.
6. **Langfuse is instance-wide**; the SDK's original list endpoints are deprecated (sunset November 2026) — keep `langfuse` current; the Cloud free tier rate-limits to tens of requests per minute.
7. **Model availability and prices change**; `prices.yaml` carries `as_of` and `source` — refresh before quoting.

---

## Reference map

| When the conversation touches… | Load |
|---|---|
| Where cost data lives, REST recipe, `trace_cost.py`, price table, baselining a use case | `reference/module-sources.md` |
| Connecting an instance to Langfuse, pricing models, verifying, attribution by session and tag, failures | `reference/module-langfuse.md` |
| Five-layer report, cost × quality join, templates | `reference/module-report.md` |
| Levers, estimates, model-per-agent routing, runtime cost controls, re-test | `reference/module-optimize.md` |

## Assets and scripts

- `assets/prices.yaml` — indicative list prices (USD per 1M tokens) for watsonx.ai-served models, with source and date.
- `scripts/trace_cost.py` — tokens and dollars from platform traces: exported JSON files or `--trace-id` fetches, per-model and per-agent breakdown, `--eval-run` join, CSV output.
- `scripts/langfuse_cost_report.py` — Langfuse model pricing registration and cost per session/model for a window.

Source of truth: https://developer.watson-orchestrate.ibm.com/ (`traces/*`, `llm/observability`), https://langfuse.com/docs, the provider's price list.
