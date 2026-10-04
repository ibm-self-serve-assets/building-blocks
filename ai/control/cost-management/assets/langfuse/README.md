# Cost in dollars with Langfuse

watsonx Orchestrate can export every conversation's trace to [Langfuse](https://langfuse.com/) (OpenTelemetry). Langfuse prices the token usage of each model generation, which turns traces into **cost per trace, session, model, and tag** — the dollars view that the platform's own dashboards (tokens) do not provide out of the box.

| File | Purpose |
|---|---|
| `langfuse_cost_report.py` | Register model pricing, then pull generations for a time window from the Langfuse API and print cost and tokens per session and per model |
| `COST-ANALYSIS.md` | The five-layer cost analysis (per scenario → per turn → patterns → recommendations → projection) and how to map Langfuse sessions to evaluation cases |

## 1. Connect watsonx Orchestrate to Langfuse

**SaaS** (Trial, Essentials, Standard non-isolated on IBM Cloud; commercial on AWS). One integration per instance — configure it only on an instance you own:

```bash
orchestrate settings observability langfuse configure \
  --url "https://<region>.cloud.langfuse.com/api/public/otel" \
  --api-key "<sk-lf-...>" \
  --health-uri "https://<region>.cloud.langfuse.com" \
  --config-json '{"public_key": "<pk-lf-...>"}'
orchestrate settings observability langfuse get          # verify; `remove` to disconnect
```

or from a file (`spec_version: v1`, `kind: langfuse`, `project_id`, `api_key`, `url`, `host_health_uri`, `config_json.public_key`, `mask_pii: true`) with `--config-file`. Self-hosted Langfuse works the same way; swap the host.

**Developer Edition:** `orchestrate server start -e .env -l` brings up a local Langfuse at `http://localhost:3010` (user `orchestrate@ibm.com`, password printed on first start). `-l` and `-i` (platform traces) are mutually exclusive. Evaluations can then be run with `orchestrate evaluations evaluate … --with-langfuse` to store the evaluation metrics alongside the traces.

## 2. Price the models

Langfuse ships pricing for the common hosted models; watsonx-served models are not pre-registered, so their cost shows as 0 until you add them. Prices are per token; take them from the provider's price list (for watsonx.ai models the published list is per million tokens — divide by 1,000,000).

```bash
export LANGFUSE_HOST=https://<region>.cloud.langfuse.com LANGFUSE_PUBLIC_KEY=pk-lf-... LANGFUSE_SECRET_KEY=sk-lf-...
python langfuse_cost_report.py --register-model "gpt-oss-120b" \
  --match-pattern "(?i)^((watsonx|groq|bedrock)[./])?(openai[./])?gpt-oss-120b.*$" \
  --input-price-per-million 0.159 --output-price-per-million 0.636
```

Pricing applies to generations ingested **after** registration. Match patterns are regular expressions against the model name Langfuse receives (`watsonx/openai/gpt-oss-120b`, `groq/openai/gpt-oss-120b`, …).

## 3. Report

```bash
python langfuse_cost_report.py --since 2h                      # generations in the last 2 hours
python langfuse_cost_report.py --since 24h --session <id>      # one conversation
python langfuse_cost_report.py --from 2026-10-01T00:00:00Z --to 2026-10-01T06:00:00Z
```

Output: cost and tokens per session (one session = one conversation; evaluation runs produce one session per test case), per model, and totals; the script also lists generations without a price so you know what is still unregistered.

## Notes

- Langfuse's original list endpoints (`/api/public/observations`, `/api/public/traces`, …) are deprecated in favour of the `v2` endpoints and are scheduled to stop working in November 2026; the script uses the official Python SDK, which tracks that change — keep `langfuse` current (`pip install -U langfuse`).
- Langfuse Cloud plans rate-limit the API (tens of requests per minute on the free tier) and keep data for a limited time; page sizes in the script are set accordingly.
- Tag traces by use case or version (trace tags, session ids) at the application layer when you need cost per use case; Langfuse's metrics API can then aggregate by tag, model, or trace name.
- The platform's own view of tokens (no dollars) is in the watsonx Orchestrate Agentic Control Plane and in the traces described under [Agent Ops](../../../agent-ops/); use it when Langfuse is not available on the instance.
