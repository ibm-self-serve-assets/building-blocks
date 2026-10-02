# Module: Sources (tokens → dollars from the platform)

**TRIGGER:** the user wants a baseline — tokens or dollars for a conversation, an evaluation run, or a use case — without Langfuse, asks where cost data lives in watsonx Orchestrate, how to price tokens, or how to compare two versions.

Authoritative docs: https://developer.watson-orchestrate.ibm.com/traces/overview.md, `traces/traces_with_cli.md`, `traces/traces_with_python.md`; price list: https://www.ibm.com/products/watsonx-ai/pricing

---

## Three places the numbers live

| Source | Granularity | Dollars? | Access |
|---|---|---|---|
| **Agentic Control Plane** (product UI) | tokens, model usage, call volume per agent and over time; FinOps view in preview | no | watsonx Orchestrate UI → Agentic Control Plane |
| **Runs API** | one run: `usage.token_usage.total_tokens`, `usage.model_usage[]` with `model_name`, `provider`, `prompt_tokens`, `completion_tokens` on the `message.completed` event | no | any application that calls `POST /v1/orchestrate/runs?stream=true` can log it per conversation at no extra cost |
| **Platform traces** | every conversation as a span tree; each `GENERATION` observation carries `model`, `usage.input/output/total`, `agentId`, latency | no (cost fields exist but are unpriced) | `orchestrate observability traces search`, REST `GET /v1/agentops-v3/observations`, `scripts/trace_cost.py` |

Dollars come from **tokens × price**. The price is an input: `assets/prices.yaml` (indicative list prices, dated) or the provider's current list. Label it in every report (RULE 5).

*Observed, unverified lead:* observations carry Langfuse-style cost fields (`calculatedTotalCost`, `inputPrice`, `outputPrice`) and `GET /v1/agentops-v3/models` lists built-in model definitions with match patterns and prices — the platform may be able to price generations natively if model definitions can be registered. Not documented; do not experiment on a shared instance; ask the instance owner or IBM support before relying on it.

---

## Inputs

- Active environment on the instance (`orchestrate env list`); traces enabled (SaaS default; DevEd `-i`).
- Trace ids, or a time window and a session (thread) id, or an Agent Ops run folder (its `<case>.metadata.json` files carry the thread ids).
- The price table.

## Read-only diagnostics

1. `orchestrate env list` — environment and token freshness.
2. `orchestrate observability traces search --last 1h --limit 5` — traces reachable (403 → the identity lacks admin rights; empty on DevEd → server without `-i`).
3. `orchestrate models list` — which model ids the agents can use; compare with the price table.
4. Read the agent YAMLs: the `llm` per agent tells you which rows of the price table matter.

---

## Finding traces

```bash
# ids, timestamps, agent names, latency for the window (<= 4h on SaaS); --session-id narrows to one conversation
source "$VENV_ACTIVATE" && \
orchestrate observability traces search --last 2h --limit 100 --sort-field start_time --sort-direction desc
```

Save the table (`> traces.txt`) when you want to feed every id to the script.

## Fetching a trace (REST — the CLI export fails on 2.18.0 against this API)

*Observed:* `orchestrate observability traces export --trace-id <id>` returns `400 VALIDATION_ERROR: fromStartTime is required`; the observations endpoint needs a window of at most 4 hours that contains the trace. `trace_cost.py --trace-id` does this for you; the raw call, for the record:

```bash
# token and instance url come from the orchestrate caches inside the shell (RULE 4); window = last 4h
TOKEN=$(python3 -c "import yaml,os; print(yaml.safe_load(open(os.path.expanduser('~/.cache/orchestrate/credentials.yaml')))['auth']['<ENV>']['wxo_mcsp_token'])") && \
INSTANCE=$(python3 -c "import yaml,os; print(yaml.safe_load(open(os.path.expanduser('~/.config/orchestrate/config.yaml')))['environments']['<ENV>']['wxo_url'])") && \
curl -sS -H "Authorization: Bearer ${TOKEN}" -H "Accept: application/json" \
  "${INSTANCE}/v1/agentops-v3/observations?traceId=<TRACE_ID>&fromStartTime=$(date -u -v-4H +%Y-%m-%dT%H:%M:%SZ)&toStartTime=$(date -u +%Y-%m-%dT%H:%M:%SZ)&limit=500" \
  -o traces/<TRACE_ID>.json && python3 -c "import json;d=json.load(open('traces/<TRACE_ID>.json'));print(len(d['data']),'observations; cursor:',d['meta'].get('cursor'))"
```

Response: `{"data": [observation, ...], "meta": {"cursor": ...}}`. A conversation of the loan example is ~90 observations (12 generations, 5 tool runs, handoffs, HTTP spans) and ~700 KB because inputs and outputs are included.

---

## `scripts/trace_cost.py`

Tokens and dollars from traces, no Langfuse needed.

```bash
# one or more exported files
source "$VENV_ACTIVATE" && python3 .bob/skills/cost-management/scripts/trace_cost.py traces/*.json

# fetch by id (active environment, or --env <name>); paced to the API's rate limit; --save keeps the JSON
source "$VENV_ACTIVATE" && python3 .bob/skills/cost-management/scripts/trace_cost.py --trace-id <id1> --trace-id <id2> --save traces/

# every id from a saved `traces search` table
source "$VENV_ACTIVATE" && python3 .bob/skills/cost-management/scripts/trace_cost.py --from-search traces.txt --save traces/

# an Agent Ops run: joins traces to cases by thread id and brings is_success; writes a CSV for the report
source "$VENV_ACTIVATE" && python3 .bob/skills/cost-management/scripts/trace_cost.py --eval-run results/evaluate_v2/<timestamp>/ --from-search traces.txt --save traces/ --csv results/evaluate_v2/<timestamp>/cost.csv
```

Options: `--prices <yaml>` (default `assets/prices.yaml`), `--price <model>=<in>,<out>` (per 1M, overrides), `--env <orchestrate env>`, `--since 4h` (fetch window), `--rate 4` (fetches per minute), `--csv <file>`, `--json <file>`.

Output per trace: start time, duration, agents involved, generations, input/output tokens, dollars (or "unpriced: <model>"); then per model and per agent; totals; and with `--eval-run`, one row per case with `is_success` and the dollars-per-successful-journey headline.

*Observed with the loan example:* one conversation ≈ 12 generations, 11.9k input / 1.0k output tokens on `openai/gpt-oss-120b` → about $0.0025 at list price; a five-case evaluation run ≈ $0.013 plus the framework's own judge and simulator calls.

---

## Baselining a use case (procedure)

1. **Pick the conversations.** Either the Agent Ops suite (deterministic, repeatable, already labelled pass/fail) or a sample of production sessions from `traces search` in a representative window.
2. **Fetch and price them** with `trace_cost.py` (`--eval-run` for the suite). Keep the JSON (`--save`) so the baseline can be re-read without new API calls.
3. **Record the baseline:** conversations, tokens in/out, dollars, dollars per successful journey, per-agent and per-model split, the price table's `as_of`. Put it next to the Agent Ops results of the same run.
4. **Re-run after every change** (prompt, model, tool, routing) on the same cases; the difference is the saving, and the Agent Ops numbers say whether quality held (`module-optimize.md`).

## Comparing two versions

Run the same suite against both versions (the loan example ships v1 and v2), fetch both runs, and present:

```
| | v1 | v2 |
|---|---|---|
| journey success | 3/5 | 5/5 |
| tokens per conversation (in / out) | … | … |
| $ per conversation (list price, <as_of>) | … | … |
| $ per successful journey | … | … |
```

The last row is the one that matters: a version that costs 10% more per conversation but succeeds twice as often is cheaper.

---

## Done when

- Tokens and dollars per conversation, per model, and per agent for the chosen conversations, with the price source named.
- The join to the Agent Ops run (when one exists) and the dollars-per-successful-journey figure.
- The saved trace JSON and CSV paths, and the user's choice: report (`module-report.md`), optimize, or stop.
