# Audit and Observability

**TRIGGER:** Load when user asks about audit logging, AuditLogger usage, JSONL schema, sink injection (Splunk/ELK/CloudWatch), dashboard aggregation, compliance retention, GDPR/CCPA, jq queries against the audit log, or latency budget per metric category.

---

## AuditLogger constructors

### File mode
```python
audit = AuditLogger(path="/var/log/guardrails/audit.jsonl")
```
Append-only JSONL. Auto-flushes after each record. Parent dirs created on open.

### Sink mode (streaming)
```python
audit = AuditLogger(sink=lambda rec: splunk_client.send(rec))
```
Pluggable callable receives each record dict. Use for Splunk/ELK/CloudWatch/etc.

### Hash-only mode (regulated industries)
```python
audit = AuditLogger(path="...", include_inputs=False)
```
For healthcare/finance: per-record `input` field is dropped; the stable `input_hash` is kept so records remain joinable to source data via a separately-controlled (regulated) store.

### Context manager
```python
with AuditLogger(path="...") as audit:
    ...
```
Closes the file on exit. Recommended for scripts.

## Recording

```python
audit.record(bundle, input_payload={...}, request_id="req-42", actor="optional-user-id")
```

**ONE CALL PER:** request, choke point. Don't batch multiple bundles into one record — each stage gets its own line for filterability.

---

## JSONL schema

One JSON object per line, written via `json.dumps(record) + "\n"`.

| Field | Type | Required | Notes |
|---|---|---|---|
| `timestamp` | ISO8601 | yes | |
| `request_id` | string | yes | example: `"req-42"` |
| `actor` | string | optional | partner-supplied user/agent identifier |
| `record_id` | string | yes | from `bundle.record_id` — internal eval ID |
| `input_hash` | string (16 chars) | yes | stable SHA-256 prefix of input payload. Joinable across records. |
| `overall_action` | enum | yes | `"Block"` \| `"Flag"` \| `"Pass"` (worst of all metric actions) |
| `blocked_metrics` | list[str] | yes | metric names that returned Block |
| `flagged_metrics` | list[str] | yes | metric names that returned Flag |
| `metrics` | dict | yes | per-metric breakdown (score, action, threshold, flag_threshold, category) |
| `input` | dict | optional | raw input payload. Omitted when `include_inputs=False`. |

**Per-metric breakdown shape inside `metrics`:**
```json
{
  "PII Detection": {
    "score": 0.87, "action": "Block",
    "threshold": 0.65, "flag_threshold": 0.4,
    "category": "safety"
  }
}
```

---

## Sink patterns

### Splunk
```python
from splunklib.client import connect
service = connect(host="...", token="...")
audit = AuditLogger(sink=lambda rec: service.indexes["guardrails"].submit(
    json.dumps(rec), source="real-time-guardrails", sourcetype="_json"
))
```
**SPL query:**
```
index=guardrails sourcetype=_json overall_action=Block
| stats count by blocked_metrics{} request_id
```

### Elasticsearch / ELK
```python
from elasticsearch import Elasticsearch
es = Elasticsearch("https://...")
audit = AuditLogger(sink=lambda rec: es.index(index="guardrails", document=rec))
```

### CloudWatch / generic
Wrap your client's `send` / `put` / `index` call in a lambda. The SDK doesn't care what's behind the sink.

---

## jq one-liners against a local audit.jsonl

```bash
# Block rate per metric
jq -r '.metrics | to_entries[] | select(.value.action=="Block") | .key' audit.jsonl | sort | uniq -c | sort -rn

# Flagged requests summary
jq -r 'select(.overall_action=="Flag") | "\(.timestamp) \(.request_id) \(.flagged_metrics|join(","))"' audit.jsonl

# Latency per choke point (requires custom 'choke_point' field added by wrapper)
jq -r '.choke_point' audit.jsonl | sort | uniq -c

# Find by input hash
jq 'select(.input_hash=="ed65c2ab5ccf4aad")' audit.jsonl
```

---

## Dashboards to build

| Dashboard | Axes / breakdown | Alert |
|---|---|---|
| **Block rate over time** | x: time (1-min buckets); y: block count; breakdown: by metric name | spike alert if block rate > baseline * 3 for 5 min |
| **Flag rate over time** | x: time; y: flag count | identify borderline content drift |
| **Latency per choke point** | x: time; y: p50/p95/p99; breakdown: by stage | p95 > 2s sustained → investigate LLM-judge cost (RULE 12) |
| **LLM-judge token spend** | watsonx.ai cost from LLM-as-judge metrics | only relevant if `WXG_PROJECT_ID` is set |
| **Per-partner distribution** | breakdown by partner_id | detect single partner dragging up overall block rate |

---

## Latency budget per category (RULE 12)

| Category | Cost |
|---|---|
| Pattern (Keyword, Regex) | ~1ms |
| Quality deterministic (TextGradeLevel, TextReadingEase, UnsuccessfulRequests) | ~1ms |
| Granite Guardian (most Safety, RAG-generation, Topic, ToolCallAccuracy) | 200-800ms each |
| LLM-as-judge (Answer Completeness, Conciseness, Tool Call Relevance) | 1-3s each |

**RULE:** Order cheap-first per choke point. Don't run LLM-judge metrics on every request — sample (10% of traffic is a common default).

---

## Dashboard starter (build your own)

**Reference component:** `examples/dashboard_skeleton.jsx` — complete MUI-based React dashboard.

**Data source recommendation:**
- **RECOMMENDED:** backend endpoint that tails the JSONL (see `examples/backend_guardrails_proxy.py` — `GET /api/audit/recent`). Frontend polls every 30s.
- **AVOID:** direct browser → JSONL file access. Browser → guardrails REST directly. localStorage as data source (compliance issue — RULE 15).

### Aggregation snippets (JavaScript)

**Average score per metric:**
```javascript
function avgScorePerMetric(records) {
  const sums = new Map(), counts = new Map();
  for (const rec of records) {
    for (const [name, m] of Object.entries(rec.metrics || {})) {
      if (m.score == null) continue;
      sums.set(name, (sums.get(name) || 0) + m.score);
      counts.set(name, (counts.get(name) || 0) + 1);
    }
  }
  const out = new Map();
  for (const [name, s] of sums) out.set(name, s / counts.get(name));
  return out;
}
```

**Action counts per metric:**
```javascript
function actionCountsPerMetric(records) {
  const out = new Map();
  for (const rec of records) {
    for (const [name, m] of Object.entries(rec.metrics || {})) {
      if (!out.has(name)) out.set(name, { Pass: 0, Flag: 0, Block: 0 });
      const bucket = out.get(name);
      if (bucket[m.action] != null) bucket[m.action] += 1;
    }
  }
  return out;
}
```

**Overall Pass/Flag/Block counts:**
```javascript
function overallActionCounts(records) {
  const out = { Pass: 0, Flag: 0, Block: 0 };
  for (const rec of records) {
    if (out[rec.overall_action] != null) out[rec.overall_action] += 1;
  }
  return out;
}
```

### Visualizations

- **Summary stacked bar:** Pass/Flag/Block counts as one stacked horizontal bar at the top. Counts + percentages labeled inside segments.
- **Per-metric linear progress:** one row per metric — MUI LinearProgress showing average score, with text annotation for action counts.
- **History table expandable:** one row per decision (newest first). Expand to see per-metric breakdown.
- **Time-bucketed trend (optional):** per-hour block rate over last 24h.

### Refresh strategy

- **Polling (default):** 30s interval. Simple, works through any proxy/firewall. Sufficient for compliance dashboards.
- **SSE:** for sub-second latency — convert `/api/audit/recent` into an SSE stream. Requires proxy changes.
- **WebSockets:** for bidirectional or very high-frequency updates. Heavier lift; rarely justified for compliance.

---

## Compliance notes

**Retention:** default file mode appends forever. For GDPR/CCPA right-to-delete, rotate the JSONL daily and run a periodic redaction job purging records older than the retention policy.

**PII in logs:** if you don't use `include_inputs=False`, raw input may include PII. Either (a) treat audit logs as PII-class storage with encryption at rest, OR (b) use `include_inputs=False` and store the original input in a separately-controlled system, joined via `input_hash`.

**Audit log chain of custody:** for regulated industries, sign the JSONL records (e.g. HMAC with a tamper-evident key) before persisting. Out of scope for the SDK but easy to add via the `sink=` callable.
