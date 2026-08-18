# Ready-Made Analysis Query Bodies

All request bodies are for `POST` endpoints unless noted. Replace placeholder values in `< >`.

> ⚠️ **Verified schema** — confirmed against live Instana API (`ibmdevsandbox-instanaibm.instana.io`).
> Earlier versions of this document contained incorrect field names that caused 422 errors.
> See the correction notes at the bottom.

---

## Error Analysis — Call Groups by Service

**Endpoint:** `POST /api/application-monitoring/analyze/call-groups`

```json
{
  "timeFrame": {
    "to": 1700000000000,
    "windowSize": 3600000
  },
  "tagFilters": [
    { "name": "call.erroneous", "operator": "EQUALS", "value": "true" },
    { "name": "application.id", "operator": "EQUALS", "value": "<app-id>" }
  ],
  "group": { "groupbyTag": "service.name" },
  "metrics": [
    { "metric": "calls",          "aggregation": "SUM" },
    { "metric": "erroneousCalls", "aggregation": "SUM" }
  ]
}
```

**Response shape per item:**
```json
{
  "name": "checkout-service",
  "metrics": {
    "calls.sum":          [[1700000000000, 512.0]],
    "erroneousCalls.sum": [[1700000000000, 43.0]]
  }
}
```

---

## Latency Analysis — P50 / P95 / P99 by Service

**Endpoint:** `POST /api/application-monitoring/analyze/call-groups`

```json
{
  "timeFrame": { "to": 1700000000000, "windowSize": 3600000 },
  "tagFilters": [
    { "name": "application.id", "operator": "EQUALS", "value": "<app-id>" }
  ],
  "group": { "groupbyTag": "service.name" },
  "metrics": [
    { "metric": "calls",    "aggregation": "SUM" },
    { "metric": "latency",  "aggregation": "P50" },
    { "metric": "latency",  "aggregation": "P95" },
    { "metric": "latency",  "aggregation": "P99" }
  ]
}
```

**Response keys:** `latency.p50`, `latency.p95`, `latency.p99` (values in milliseconds).

---

## Call Volume Over Time (Rollup / Time-Series)

**Endpoint:** `POST /api/application-monitoring/analyze/call-groups`

```json
{
  "timeFrame": { "to": 1700000000000, "windowSize": 86400000 },
  "tagFilters": [
    { "name": "application.id", "operator": "EQUALS", "value": "<app-id>" }
  ],
  "group": { "groupbyTag": "service.name" },
  "rollupWindow": 3600000,
  "metrics": [
    { "metric": "calls",          "aggregation": "SUM" },
    { "metric": "erroneousCalls", "aggregation": "SUM" },
    { "metric": "latency",        "aggregation": "P95" }
  ]
}
```

`rollupWindow` is the bucket size in milliseconds. Minimum is `60000` (1 minute).
Each item in the response will have one `[timestamp, value]` pair per bucket in its metrics arrays.

To aggregate across all services into application-level totals, sum `calls.sum` and `erroneousCalls.sum`
across all items at the same timestamp, and average the latency values.

---

## Fetch Recent Traces (All or Erroneous)

**Endpoint:** `POST /api/application-monitoring/analyze/traces`

> ⚠️ **Verified request body** — `"order"` is **not valid** on this endpoint and causes silent failures on some Instana SaaS versions. Omit it entirely.

```json
{
  "timeFrame": { "to": 1700000000000, "windowSize": 3600000 },
  "tagFilters": [
    { "name": "application.id", "operator": "EQUALS", "value": "<app-id>" }
  ],
  "pagination": { "retrievalSize": 10, "offset": 0 }
}
```

To fetch **only erroneous traces**, add a second tag filter:
```json
{ "name": "call.erroneous", "operator": "EQUALS", "value": "true" }
```

**Verified response shape** (each item is an envelope — trace fields are nested):
```json
{
  "items": [
    {
      "trace": {
        "id": "c9c577e62ddddf35",
        "label": "POST /api/auth/logout",
        "startTime": 1782228535226,
        "duration": 55,
        "erroneous": false,
        "service": { "id": "...", "label": "eum-search-api" },
        "endpoint": null
      },
      "cursor": { "type": "IngestionOffsetCursor", "ingestionTime": 1782287807000, "offset": 1 }
    }
  ],
  "totalHits": 196,
  "canLoadMore": true
}
```

> ❌ **Do NOT** attempt to read `item.traceId`, `item.id`, `item.services[]`, `item.requests[]`, or `item.timestamp`. All trace data lives under `item.trace.*`.

Then fetch each trace tree by ID:
`GET /api/application-monitoring/analyze/traces/{traceId}`

where `traceId` = `item.trace.id` from the list response.

---

## Service Topology — All Services for an Application

**Endpoint:** `GET /api/application-monitoring/services`

Query parameters:
```
?applicationId=<app-id>&pageSize=100&page=1
```

---

## Notes

- `to` must be a real Unix timestamp in **milliseconds** — always use `Date.now()` (JS) or `int(time.time() * 1000)` (Python). Do **not** use `0`.
- `windowSize` is always in **milliseconds**.
- `rollupWindow` controls time-bucket size for trend charts; `60000` (1 min) for granular views, `3600000` (1 hr) for daily overviews.
- `group` is **always required** on `analyze/call-groups`. Use `{ "groupbyTag": "service.name" }` as the default. Omitting it returns 422.

---

## ⚠️ Schema Corrections (from live API verification)

The following fields used in older versions of this document are **incorrect** and cause HTTP 422 or silent empty responses:

| ❌ Old (incorrect) | ✅ Correct |
|---|---|
| `"tagFilterExpression": { "type": "TAG_FILTER", ... }` | `"tagFilters": [{ "name": ..., "operator": ..., "value": ... }]` |
| `"groupByTags": ["service.name"]` | `"group": { "groupbyTag": "service.name" }` |
| `"groupByTags": []` (empty/omit) | `"group": { "groupbyTag": "service.name" }` — always required |
| `"metric": "calls.count"` | `"metric": "calls"` |
| `"metric": "calls.erroneous.count"` | `"metric": "erroneousCalls"` |
| `"metric": "latency.p95", "aggregation": "PERCENTILE", "percentile": 95` | `"metric": "latency", "aggregation": "P95"` |
| `"timeFrame": { "to": 0, ... }` | `"timeFrame": { "to": <current_ms_timestamp>, ... }` |
| `"granularity": N` inside metric objects | Top-level `"rollupWindow": N` |
| `"order": { "by": "timestamp", "direction": "DESC" }` on traces | **Omit entirely** — not accepted on `analyze/traces`, causes silent failures |

### Traces Response — Field Access Corrections

| ❌ Old (incorrect — field does not exist) | ✅ Correct |
|---|---|
| `item.traceId` | `item.trace.id` |
| `item.id` | `item.trace.id` |
| `item.services[0]` | `item.trace.service?.label` |
| `item.requests[0].name` | `item.trace.endpoint?.label ?? item.trace.label` |
| `item.timestamp` | `item.trace.startTime` |
| `item.duration` | `item.trace.duration` |
| `item.erroneous` | `item.trace.erroneous` |
