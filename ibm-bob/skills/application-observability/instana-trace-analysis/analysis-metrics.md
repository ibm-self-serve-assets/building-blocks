# Analysis Metric Formulas and SLO Defaults

## Core Metric Formulas

| Metric | Formula | Unit |
|--------|---------|------|
| Error rate | `(erroneous_calls / total_calls) × 100` | % |
| Success rate | `100 − error_rate` | % |
| Throughput | `total_calls / window_minutes` | calls/min |
| p95 breach | `p95_latency > p95_slo_ms` | boolean |
| Error spike multiplier | `current_error_rate / baseline_error_rate` | ratio |
| Apdex score | `(satisfied + frustrated × 0.5) / total` | 0–1 |

---

## Default SLO Thresholds

These are conservative starting points. Override them based on actual SLO agreements.

| Metric | Healthy | Degraded | Critical |
|--------|---------|----------|---------|
| Error rate | < 1% | 1–5% | > 5% |
| p50 latency | < 200 ms | 200–500 ms | > 500 ms |
| p95 latency | < 500 ms | 500–2000 ms | > 2000 ms |
| p99 latency | < 2000 ms | 2000–5000 ms | > 5000 ms |
| Availability | > 99.9% | 99–99.9% | < 99% |

---

## Error Classification

| HTTP Range | Category | Investigation approach |
|-----------|---------|----------------------|
| 4xx (client) | Client errors | Check input validation, authentication, deprecated API usage |
| 5xx (server) | Server errors | Check logs, downstream dependencies, DB connections |
| Timeout / no response | Infrastructure | Check network, service restarts, resource exhaustion |

---

## Baseline Calculation

To detect anomalies, compare the current window against a baseline. Recommended approach:

```python
def classify_error_rate(current_pct: float) -> str:
    if current_pct < 1.0:
        return "healthy"
    elif current_pct < 5.0:
        return "degraded"
    return "critical"

def latency_status(p95_ms: float, p99_ms: float) -> str:
    if p99_ms > 5000 or p95_ms > 2000:
        return "critical"
    elif p99_ms > 2000 or p95_ms > 500:
        return "degraded"
    return "healthy"
```

---

## Root Cause Heuristics

When analyzing a trace tree, apply these heuristics in order:

1. **Deepest erroneous span** — the span furthest from the root that has `erroneous: true` is the likely origin.
2. **Longest span** — if no explicit error, the span with the greatest `duration` is the latency bottleneck.
3. **Sequential vs parallel** — spans with overlapping timestamps ran in parallel; sequential spans compound latency.
4. **External calls** — spans with `call.type = HTTP` pointing to external hosts are common latency sources.
5. **Database calls** — look for spans with `db.type` or `call.db.statement`; slow queries appear here.
