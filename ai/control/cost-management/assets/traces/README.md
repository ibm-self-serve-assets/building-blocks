# Dollars from platform traces (no Langfuse needed)

Every watsonx Orchestrate conversation is a trace; each model call inside it is a `GENERATION` observation with the model name and token usage. `trace_cost.py` turns that into tokens and dollars per conversation, per model, and per agent, and can join the numbers to an Agent Ops evaluation run so cost sits next to pass/fail.

| File | Purpose |
|---|---|
| `trace_cost.py` | Read exported trace JSON or fetch traces by id / by evaluation run from the active `orchestrate` environment; price with the table; per-model and per-agent breakdown; CSV/JSON output |
| `prices.yaml` | Indicative list prices (USD per 1M tokens) for watsonx.ai-served models, with source and date — edit before quoting |

## Use

```bash
source <venv>/bin/activate                                        # the ADK venv; the script reuses its token cache
orchestrate env list                                               # the active environment is the one queried

# one or more exported trace files
python trace_cost.py traces/*.json

# fetch by trace id (ids from `orchestrate observability traces search --last 2h`)
python trace_cost.py --trace-id <id> --save traces/

# every id in a saved search table, capped
orchestrate observability traces search --last 2h --limit 100 > traces.txt
python trace_cost.py --from-search traces.txt --limit 20 --save traces/

# an Agent Ops run: cost per case next to is_success, and dollars per successful journey
python trace_cost.py --eval-run results/evaluate_v2/<timestamp>/ --save traces/ --csv results/evaluate_v2/<timestamp>/cost.csv
```

Options: `--prices <yaml>`, `--price <model>=<in>,<out>` (per 1M tokens), `--env <name>`, `--since 4h` or `--from/--to`, `--rate 4` (API calls per minute), `--json <file>`.

## What the numbers mean

- **Model-inference cost at list price**: tokens × the price in the table. Comparable across designs, and the actual cost when the model is billed per token (watsonx.ai, or a third-party provider through the model gateway). WXO SaaS plans meter usage by plan — confirm how the plan meters before quoting an invoice figure.
- Unpriced models are reported in tokens with a note; add a row to `prices.yaml` or pass `--price`.
- Agents are attributed from the trace: the nearest span naming a collaborator, otherwise the orchestrator on the root span.

## Observed on ADK 2.18.0 / IBM Cloud SaaS (October 2026)

- `orchestrate observability traces export` fails with `400 fromStartTime is required`; the observations endpoint needs a window of at most 4 hours and allows a few calls per minute. The script sends the window and paces its calls.
- `GET /v1/agentops-v3/traces?sessionId=<thread id>` finds a conversation's trace; the evaluation framework writes that thread id to `<case>.metadata.json`, which is how `--eval-run` joins cost to cases.
- Observations carry `model` without the provider prefix (`openai/gpt-oss-120b`), `usage {input, output, total}`, and cost fields that stay 0 because no prices are configured on the platform.
- One loan-underwriting conversation: 12 generations, about 11.9k input and 1.0k output tokens, ≈ $0.0025 at list price.
