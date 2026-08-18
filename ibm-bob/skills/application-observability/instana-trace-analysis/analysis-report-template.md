# Analysis Report Template

Use this structure when presenting trace or service analysis results.

---

## Template

```markdown
# Instana Analysis Report
**Application:** <app-name>
**Time window:** <start> → <end> (<duration>)
**Generated:** <timestamp>

---

## Summary
<One paragraph describing what the analysis found — which services are affected, severity, and whether
the issue is ongoing or historical.>

---

## Key Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Error rate | X.X% | 🔴 Critical / 🟡 Degraded / 🟢 Healthy |
| p50 latency | XXX ms | 🟢 Healthy |
| p95 latency | XXX ms | 🟡 Degraded |
| p99 latency | XXXX ms | 🔴 Critical |
| Total calls | X,XXX | — |
| Erroneous calls | XXX | — |

---

## Top Issues

### 1. <Service / Endpoint name> — <N> errors (<X.X%>)
- **Error types:** HTTP 5xx (N), HTTP 4xx (N)
- **p99 latency:** X,XXX ms
- **Sample trace ID:** `<trace-id>`

### 2. <Next service / endpoint…>

---

## Root Cause Evidence

### Trace `<trace-id>` — <service> — <timestamp>
- **Duration:** X,XXX ms
- **Error:** `<error message>`
- **Root span:** `<span name>` in `<service>` at depth N
- **Relevant spans:**
  | Span | Service | Duration | Status |
  |------|---------|----------|--------|
  | `<name>` | `<service>` | XXX ms | ❌ Error |
  | `<name>` | `<service>` | XXX ms | ✅ OK |

---

## Recommendations

1. **<Service>:** <Specific, actionable recommendation — e.g. "Add circuit breaker for calls to downstream-service">
2. **<Endpoint>:** <Recommendation — e.g. "Optimise SQL query in span 'db.query' — currently X,XXX ms">
3. **Monitoring:** <e.g. "Set alert on error rate > 2% for this application">

---

## Raw Data

Saved to: `<path/to/raw-results.json>` (if persisted)
```

---

## Usage Note

When generating a report, fill in every section. Do not omit the "Root Cause Evidence" section even if only one trace is available — always cite at least one concrete trace ID to support the findings. Use the status emojis (🔴 🟡 🟢) consistently per the thresholds in `analysis-metrics.md`.
