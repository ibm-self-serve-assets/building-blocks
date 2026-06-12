# Module: Observability

**TRIGGER:** Load when user wants to search runtime traces, export a trace as JSON, asks about the Python traces SDK (`TracesController`, `TraceFilters`), wants to set up Langfuse (local or hosted), asks about cost/latency analysis, the 5-layer cost report, or how to register model pricing in Langfuse.

---

## Three observability surfaces

1. **Traces (OpenTelemetry-based)**
   - CLI: `orchestrate observability traces search / export`
   - Python: `ibm_watsonx_orchestrate.client.observability.traces` (SDK)
   - Works on DevEd (with `server start -i`) and SaaS (on by default).

2. **Langfuse**
   - Local: `server start -l`; UI at `http://localhost:3010`
   - Hosted: `orchestrate settings observability langfuse configure / get / remove`

3. **IBM Telemetry (DevEd-side flag)**
   - `server start --with-ibm-telemetry` / `-i`
   - Mutually exclusive with `-l` (RULE 8)

For metric interpretation of an eval RUN, see `reference/module-analyze.md`. This module is about ongoing runtime visibility: which conversations happened, how long they took, how much they cost, what went wrong.

**Authoritative docs:**
- Traces overview: https://developer.watson-orchestrate.ibm.com/traces/overview.md
- Traces CLI: https://developer.watson-orchestrate.ibm.com/traces/traces_with_cli.md
- Traces Python SDK: https://developer.watson-orchestrate.ibm.com/traces/traces_with_python.md
- Langfuse observability: https://developer.watson-orchestrate.ibm.com/llm/observability.md

---

## Inputs

- **Required:** target env from Q1.
- **For DevEd traces:** server started with `-i`. **For DevEd Langfuse:** `-l`. (Not both — RULE 8.)
- **For SaaS:** env activated.

## Read-only diagnostics

1. **DevEd: which observability flag was used:** `lsof -ti :4321` (server up?); ask user whether `-l` or `-i`. Fail action: if user wants traces but server started with `-l`, ask them to restart with `-i` (or vice versa).
2. **Traces CLI low-limit probe:** `orchestrate observability traces search --start-time <1h ago> --end-time <now> --limit 5`. Fail action: if empty + DevEd, confirm `-i` is on. If empty + SaaS, confirm there has been real traffic.
3. **Langfuse UI reachable:** for DevEd: `lsof -ti :3010`. For hosted: read `settings observability langfuse get` output.

---

## Traces CLI

### `traces_search_recent`
**Time window mandatory (RULE 6).**

```bash
# On ADK >= 2.6.0 you may substitute `--last 1h` for --start-time/--end-time.
source "$VENV_ACTIVATE" && \
orchestrate observability traces search \
  --start-time "$(date -u -v-1H +%Y-%m-%dT%H:%M:%S)" \
  --end-time "$(date -u +%Y-%m-%dT%H:%M:%S)" \
  --limit 20
```

### `traces_search_filtered`
```bash
source "$VENV_ACTIVATE" && \
orchestrate observability traces search \
  --start-time "<ISO>" \
  --end-time "<ISO>" \
  --agent-name "<agent>" \
  --user-id "<user>" \
  --session-id "<session>" \
  --min-spans 5 \
  --limit 50 \
  --sort-field start_time \
  --sort-direction desc
```

### `traces_export`
**Purpose:** export a single trace as JSON for offline analysis.

```bash
source "$VENV_ACTIVATE" && \
orchestrate observability traces export \
  --trace-id <TRACE_ID> \
  --pretty \
  --output traces/$(date +%Y%m%d-%H%M%S)-<TRACE_ID>.json
```

After user pastes output path, Bob reads the span tree locally and surfaces the top-3 slowest spans, any error spans, and a one-paragraph summary.

---

## Traces Python SDK

**Purpose:** programmatic trace export — useful for batch analysis, CI integrations, custom dashboards.

```python
# export_traces.py — save in your project, then run.
# See https://developer.watson-orchestrate.ibm.com/traces/traces_with_python.md for the full API.
from datetime import datetime, timedelta, timezone
from ibm_watsonx_orchestrate.client.observability.traces import TracesController, TraceFilters

now = datetime.now(timezone.utc)
filters = TraceFilters(
    start_time=now - timedelta(hours=24),
    end_time=now,
    # agent_name="my_agent",
    # user_id="user@example.com",
    min_spans=5,
    limit=100,
)
controller = TracesController()
traces = controller.search(filters)

for t in traces:
    span_data = controller.export(trace_id=t.trace_id)
    # ... persist span_data, send to your dashboard, etc.
    print(t.trace_id, len(span_data.get("spans", [])), "spans")
```

Run with:
```bash
source "$VENV_ACTIVATE" && python3 export_traces.py
```

---

## Langfuse — local

### `server_start_with_langfuse`
**Purpose:** start DevEd server with bundled local Langfuse stack.

```bash
source "$VENV_ACTIVATE" && \
orchestrate server start -e .env -l
```

**Do NOT also pass `-i` — RULE 8.**

When server is up, log into `http://localhost:3010` with `orchestrate@ibm.com` (password prints in terminal on first server start). Fetch Langfuse keys from Settings → API Keys.

### `langfuse_env_vars`
```bash
export LANGFUSE_BASE_URL="http://localhost:3010"
export LANGFUSE_PUBLIC_KEY="<public>"
export LANGFUSE_SECRET_KEY="<secret>"
```

---

## Langfuse — hosted

### `langfuse_configure`
```bash
# --config-file points at YAML with full Langfuse config (URL, project, mask_pii, etc.)
# --config-json is the inline alternative.
source "$VENV_ACTIVATE" && \
orchestrate settings observability langfuse configure \
  --config-file langfuse_config.yaml
```

### `langfuse_get_or_remove`
```bash
source "$VENV_ACTIVATE" && \
orchestrate settings observability langfuse get --output yaml
# To remove:
# orchestrate settings observability langfuse remove
```

### Langfuse config YAML shape
```yaml
# langfuse_config.yaml
url: https://langfuse.example.com
health_uri: /api/public/health
project_id: <project>
api_key: <key>
mask_pii: true   # documented; masks PII before traces leave the tenant
```

---

## Cost & latency analysis (5-layer report)

**SOURCE NOTE (RULE 9):** The 5-layer report SHAPE below is curated; NOT WXO-published. The underlying DATA (tokens, cost, latency per span) comes from Langfuse — that data is authoritative. The framework for organizing that data into a customer-ready report is this skill's recommendation; tailor sections to what your customer cares about.

**When to use:** user asked about cost or latency, OR `analyze` surfaced an Avg Response Time regression.

### Prerequisites for cost data

Cost data appears in Langfuse ONLY when BOTH conditions hold:

1. **Agent's model is REGISTERED in Langfuse with pricing** (see `register_model_pricing` below). Langfuse ships 161 model definitions out of the box, but `groq/openai/gpt-oss-120b` and other watsonx-served models are NOT pre-registered.

2. **Eval was run with `--with-langfuse` AND token usage is propagated to Langfuse observations.** If observations show `usage.total = 0` even after eval-fw 1.4+ with `-l`, the WXO server isn't propagating usage from the agent's LLM response — that's an upstream gap unrelated to pricing. Verify by inspecting a single trace (see `inspect_trace_usage` below) before assuming pricing is the blocker.

**Latency data is always available** (recorded automatically per observation). You can always do a latency-only report if cost is unavailable.

### The 5-layer report shape

Bob queries Langfuse's REST API directly for cost/token data — NOT the UI dashboard.

1. **Per-scenario breakdown** (tokens, cost, pass/fail)
2. **Per-turn context growth** (multi-turn cost driver)
3. **Cost patterns** (base cost, growth rate, input/output ratio, wasted spend on failures)
4. **Data-driven recommendations** (only what the data supports)
5. **Production projection** at expected conversation volume

### `register_model_pricing`
**Purpose:** register a non-standard model in Langfuse so cost computes from token usage. Source for pricing: official provider price page. For `groq/openai/gpt-oss-120b`: input $0.15/M tokens, output $0.75/M tokens. Match pattern intentionally accepts groq/openai/bedrock/watsonx prefixes since the same underlying model appears under different routing prefixes.

```bash
# Adjust modelName, matchPattern, inputPrice, outputPrice for your agent's model.
# Use the OpenAI gpt-4o tokenizer as a reasonable approximation for token counting.
AUTH="Basic $(printf '%s' "${LANGFUSE_PUBLIC_KEY}:${LANGFUSE_SECRET_KEY}" | base64)"
curl -sS -X POST \
  -H "Authorization: $AUTH" \
  -H "Content-Type: application/json" \
  "${LANGFUSE_BASE_URL}/api/public/models" \
  -d '{
    "modelName": "gpt-oss-120b",
    "matchPattern": "(?i)^((groq|openai|bedrock|watsonx)[\\./])?(openai[\\./])?(gpt-oss-120b)([\\.-]?1[\\.:]?0)?$",
    "tokenizerId": "openai",
    "tokenizerConfig": {"tokenizerModel": "gpt-4o"},
    "unit": "TOKENS",
    "inputPrice": 1.5e-7,
    "outputPrice": 7.5e-7,
    "startDate": "2024-08-01"
  }' | python3 -m json.tool
```

You should see a model entry with an `id` field — that confirms registration. New observations matching the pattern will get cost computed on the fly.

### `inspect_trace_usage`
**Purpose:** confirm whether usage data is actually being propagated. If observations show non-zero `promptTokens` / `completionTokens`, cost should compute once pricing is registered. If they're all 0, pricing won't help — that's an upstream propagation gap.

```bash
AUTH="Basic $(printf '%s' "${LANGFUSE_PUBLIC_KEY}:${LANGFUSE_SECRET_KEY}" | base64)"
# Replace <TRACE_ID> with an ID from `traces?limit=5`
curl -sS -H "Authorization: $AUTH" \
  "${LANGFUSE_BASE_URL}/api/public/traces/<TRACE_ID>" | \
  python3 -c "
import json,sys
t=json.load(sys.stdin)
print(f'totalCost: {t.get(\"totalCost\")}, inputTokens: {t.get(\"inputTokens\")}, outputTokens: {t.get(\"outputTokens\")}')
for o in t.get('observations',[])[:6]:
    print(f'  obs type={o.get(\"type\")} model={o.get(\"model\")} cost={o.get(\"totalPrice\")} tokens={o.get(\"promptTokens\")}/{o.get(\"completionTokens\")}')
"
```

### List traces with cost/token summary
```bash
# Use limit<=25 to avoid the legacy endpoint's timeout under load.
AUTH="Basic $(printf '%s' "${LANGFUSE_PUBLIC_KEY}:${LANGFUSE_SECRET_KEY}" | base64)"
curl -sS -H "Authorization: $AUTH" \
  "${LANGFUSE_BASE_URL}/api/public/traces?limit=25" | python3 -m json.tool
```

---

## Done-when criteria

- **For traces:** Bob has surfaced a list of relevant trace IDs (or none, with explanation if none exist).
- **For exported traces:** Bob has produced the span-tree summary with top-3 slowest spans and any error spans.
- **For Langfuse:** keys are wired into user's env; subsequent eval runs will persist traces.
- **For cost/latency:** the 5-layer report is delivered, with concrete next actions and a production projection.
