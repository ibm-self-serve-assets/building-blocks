# Common Instana Endpoint Reference

All paths are relative to `https://<unit>.instana.io`.

---

## Health / Connectivity

| Method | Path | Notes |
|--------|------|-------|
| GET | `/api/instana/health` | Lightweight ping — use for connection validation |

---

## Application Monitoring

| Method | Path | Key Parameters |
|--------|------|----------------|
| GET | `/api/application-monitoring/applications` | `page`, `pageSize` |
| GET | `/api/application-monitoring/applications/{id}` | — |
| GET | `/api/application-monitoring/services` | `applicationId`, `page`, `pageSize` |
| GET | `/api/application-monitoring/endpoints` | `serviceId`, `page`, `pageSize` |
| POST | `/api/application-monitoring/analyze/call-groups` | `tagFilters`, `group`, `metrics`, `timeFrame` |
| POST | `/api/application-monitoring/analyze/traces` | `tagFilters`, `timeFrame`, `pagination` |
| GET | `/api/application-monitoring/v2/analyze/traces/{traceId}` | Returns span list for a single trace — **verified working** |

---

## Infrastructure Monitoring

| Method | Path | Key Parameters |
|--------|------|----------------|
| POST | `/api/infrastructure-monitoring/snapshots` | `query`, `windowSize` |
| GET | `/api/infrastructure-monitoring/snapshots/{id}` | `to`, `windowSize` |

---

## Events

| Method | Path | Key Parameters |
|--------|------|----------------|
| GET | `/api/events` | `from`, `to`, `eventTypeFilters`, `excludeTriggered` |
| GET | `/api/events/{eventId}` | — |

---

## SLOs

| Method | Path | Key Parameters |
|--------|------|----------------|
| GET | `/api/slo` | `page`, `pageSize` |
| GET | `/api/slo/{sloId}/status` | `from`, `to` |

---

## Common Request Body Shapes

### Time Frame
```json
{ "to": 1700000000000, "windowSize": 3600000 }
```
`windowSize` is in milliseconds. `to` must be a real Unix timestamp in **milliseconds** — do **not** use `0` or omit it; always pass `Date.now()` (JS) or `int(time.time() * 1000)` (Python).

### Application Perspective Scoping — Critical Behaviour

Different endpoints use different field names to scope by application perspective:

| Endpoint | Field that scopes | Works? |
|---|---|---|
| `POST /api/application-monitoring/metrics/services` | `"applicationId": "<id>"` (top-level string) | ✅ Yes |
| `POST /api/application-monitoring/metrics/endpoints` | `"applicationId": "<id>"` (top-level string) | ✅ Yes |
| `POST /api/application-monitoring/analyze/traces` | `"applicationId"` top-level | ❌ **Ignored — returns all apps** |
| `POST /api/application-monitoring/analyze/traces` | `"tagFilterExpression"` matching app's own filter | ✅ Yes |

**The traces endpoint MUST use `tagFilterExpression` to scope to an application.**

The correct approach: fetch the app perspective's config once from `GET /api/application-monitoring/settings/application/{id}`, extract its `tagFilterExpression`, and pass that as the `tagFilterExpression` in every traces request. This guarantees traces match exactly what the application perspective monitors.

```js
// Step 1 — get the app's own tag filter (cache this)
const appConfig = await apiFetch(`/api/application-monitoring/settings/application/${APP_ID}`);
const appFilter = appConfig.tagFilterExpression;
// e.g. { type: 'TAG_FILTER', name: 'kubernetes.namespace.name',
//         operator: 'EQUALS', stringValue: 'techxchange', entity: 'DESTINATION' }

// Step 2 — use it in trace requests
const body = {
  tagFilterExpression: appFilter,   // scopes to the application
  timeFrame: { to: Date.now(), windowSize: 3600000 },
  pagination: { page: 1, pageSize: 50 },
  order: { by: 'START_TIME', direction: 'DESC' },
};

// Step 3 — erroneous-only: wrap in an AND expression
const errFilter = { type: 'TAG_FILTER', name: 'call.erroneous',
  operator: 'EQUALS', stringValue: 'true', value: 'true', entity: 'NOT_APPLICABLE' };
const combined = {
  type: 'EXPRESSION', logicalOperator: 'AND',
  elements: [appFilter, errFilter],
};
```

### Tag Filters (call-groups and traces)
The filter field is a flat **array** named `tagFilters` — not `tagFilterExpression`.
```json
"tagFilters": [
  { "name": "application.id", "operator": "EQUALS", "value": "<app-id>" }
]
```

### Group (call-groups — always required)
`group` is **always required** on `analyze/call-groups` — even when not logically grouping. Use `service.name` as the default grouping tag. The field is `group.groupbyTag` (singular, lowercase `g`).
```json
"group": { "groupbyTag": "service.name" }
```
Omitting `group` or sending `null` returns HTTP **422** — `"group must not be null"`.

### Metrics (call-groups, metrics/services, metrics/endpoints)
Confirmed working metric names and aggregations (verified against live Instana API):

| Purpose | `metric` | `aggregation` |
|---------|----------|---------------|
| Call count | `"calls"` | `"SUM"` |
| Error count | `"erroneousCalls"` | `"SUM"` |
| Latency mean | `"latency"` | `"MEAN"` |
| Latency median | `"latency"` | `"P50"` |
| Latency 95th pct | `"latency"` | `"P95"` |
| Latency 99th pct | `"latency"` | `"P99"` |
| Latency max | `"latency"` | `"MAX"` |
| Latency min | `"latency"` | `"MIN"` |

> ⚠️  **Do NOT** use `"latency.mean"`, `"latency.p95"`, `"latency.p99"` as the `metric` field name in **any** endpoint (`analyze/call-groups`, `metrics/services`, `metrics/endpoints`, `metrics/applications`). These all return HTTP **400** `"Missing metrics"`. The metric name is always the short form `"latency"`; the aggregation carries the statistic type.

> ⚠️  Do **not** use `"calls.count"`, `"calls.erroneous.count"` — these return 422 `"Metric type unknown"`.

### Response Keys (all metrics endpoints)
Each item's `metrics` map uses keys of the form `<metric>.<aggregation_lowercase>`:

| Requested `metric` + `aggregation` | Response key |
|------------------------------------|-------------|
| `"calls"` + `"SUM"` | `calls.sum` |
| `"erroneousCalls"` + `"SUM"` | `erroneousCalls.sum` |
| `"latency"` + `"MEAN"` | `latency.mean` |
| `"latency"` + `"P50"` | `latency.p50` |
| `"latency"` + `"P95"` | `latency.p95` |
| `"latency"` + `"P99"` | `latency.p99` |
| `"latency"` + `"MAX"` | `latency.max` |
| `"latency"` + `"MIN"` | `latency.min` |

Each value is a `[[timestamp_ms, value]]` array. For rollup queries each array has one entry per time bucket.

> ⚠️  **Do NOT** read `metrics['latency.mean.mean']`, `metrics['latency.p95.p95']` — these keys do not exist. The response key is just `latency.mean` / `latency.p95`, never double-suffixed.

### Time-Series / Rollup
Add top-level `rollupWindow` (milliseconds per bucket) to get multiple time-series data points per item:
```json
"rollupWindow": 60000
```
Minimum `rollupWindow` is `60000` (1 minute). Do **not** add `granularity` inside individual metric objects — that is not valid.

### Pagination Cursor (traces)
```json
{ "page": 1, "pageSize": 50 }
```

> ⚠️ The `"order"` field behaviour varies by Instana version — it is accepted on some instances (e.g. `{ "by": "LATENCY", "direction": "DESC" }`) but silently ignored or rejected on others. Default ordering is reverse-chronological. Omit `"order"` if consistent cross-version behaviour is needed.

---

### Traces Response Shape (`POST /api/application-monitoring/analyze/traces`)

> ⚠️ **Verified against live Instana API (`ibmdevsandbox-instanaibm.instana.io`).**
> Each item is a **wrapper object** — the trace fields are nested one level deep under a `trace` key, not flat on the item itself.

**Response envelope:**
```json
{
  "items": [...],
  "totalHits": 196,
  "canLoadMore": true,
  "totalRepresentedItemCount": 196,
  "totalRetainedItemCount": 196,
  "adjustedTimeframe": { "windowSize": 3600000, "to": 1700000000000 }
}
```

**Each item shape:**
```json
{
  "trace": {
    "id": "c9c577e62ddddf35",
    "label": "POST /api/auth/logout",
    "startTime": 1782228535226,
    "duration": 55,
    "erroneous": false,
    "service": {
      "id": "50afd80fb05760b3db0de3ea200c8fc27711e9fc",
      "label": "eum-search-api",
      "types": [],
      "technologies": null,
      "snapshotIds": [],
      "entityType": "SERVICE"
    },
    "endpoint": null
  },
  "cursor": {
    "type": "IngestionOffsetCursor",
    "ingestionTime": 1782287807000,
    "offset": 1
  }
}
```

**Field mapping — what to read from each item:**

| Purpose | Path | Notes |
|---------|------|-------|
| Trace ID | `item.trace.id` | 16-char hex string |
| Operation / endpoint label | `item.trace.label` | e.g. `"POST /api/auth/logout"` |
| Service name | `item.trace.service?.label` | May be `null` if no service resolved |
| Named endpoint | `item.trace.endpoint?.label` | Usually `null`; fall back to `item.trace.label` |
| Start timestamp | `item.trace.startTime` | Epoch milliseconds |
| Duration | `item.trace.duration` | Milliseconds |
| Error flag | `item.trace.erroneous` | Boolean |

> ❌ **Do NOT read** `item.traceId`, `item.id`, `item.services`, `item.requests`, `item.timestamp` — these fields do not exist at the item level. All trace data is under `item.trace.*`.

**TypeScript type:**
```typescript
type TraceEnvelope = {
  trace: {
    id: string;
    label: string;
    startTime: number;
    duration: number;
    erroneous: boolean;
    service: { id: string; label: string } | null;
    endpoint: { label: string } | null;
  };
  cursor: unknown;
};

type TracesResponse = {
  items: TraceEnvelope[];
  totalHits: number;
  canLoadMore: boolean;
};
```

**Correct mapper (TypeScript):**
```typescript
const items = (raw.items ?? []).map((item) => ({
  traceId:     item.trace.id,
  serviceName: item.trace.service?.label ?? 'unknown',
  endpoint:    item.trace.endpoint?.label ?? item.trace.label ?? '/',
  duration:    item.trace.duration ?? 0,
  erroneous:   item.trace.erroneous ?? false,
  timestamp:   item.trace.startTime ?? 0,
}));
```

---

### Trace Detail Response Shape (`GET /api/application-monitoring/v2/analyze/traces/{traceId}`)

> ⚠️ **Verified against live Instana instance (`unit0-techzone.150-240-162-27.nip.io`).**
>
> **Do NOT use any of these paths — all return 404:**
> - `/api/application-monitoring/trace/{traceId}`
> - `/api/application-monitoring/analyze/traces/{traceId}` ← **this is the most common mistake — no `/v2/`**
> - `/api/application-monitoring/traces/{traceId}`
>
> The only working path is: **`/api/application-monitoring/v2/analyze/traces/{traceId}`**
>
> The response has **no top-level trace object** — only an `items` array of spans. All trace metadata (startTime, duration, root service) must be derived from the spans array by finding the root span (`parentId === null`).

The response is an **object with an `items` array** — each item is a span/call node (not a flat array).

**Response shape:**
```json
{
  "items": [
    {
      "id": "6955fb70a5d1de16",
      "parentId": null,
      "foreignParentId": null,
      "name": "POST /api/auth/logout",
      "timestamp": 1787567699906,
      "duration": 2,
      "errorCount": 0,
      "callCount": 1,
      "destination": {
        "service":  { "id": "...", "label": "backend" },
        "endpoint": { "id": "...", "label": "POST /api/auth/logout", "type": "HTTP" }
      },
      "cursor": { "type": "IngestionOffsetCursor", "ingestionTime": 0, "offset": 1 }
    }
  ],
  "canLoadMore": false,
  "totalHits": 1
}
```

**Field mapping:**

| Purpose | Path | Notes |
|---------|------|-------|
| Span ID | `item.id` | hex string |
| Parent span ID | `item.parentId` | `null` for root span |
| Span name | `item.name` | e.g. `"POST /api/auth/logout"` |
| Service name | `item.destination.service.label` | |
| Endpoint label | `item.destination.endpoint.label` | falls back to `item.name` |
| Timestamp | `item.timestamp` | epoch ms |
| Duration | `item.duration` | ms |
| Has errors | `item.errorCount > 0` | integer, **not** a boolean `erroneous` field |

> ❌ **Do NOT read** `item.spanId`, `item.parentSpanId`, `item.erroneous`, `item.serviceName` — these fields do not exist.

**Correct mapper:**
```js
const spanArray = result?.items ?? [];

const spans = spanArray.map((s) => ({
  spanId:       s.id       || '',
  parentSpanId: s.parentId || null,
  name:         s.name     || '—',
  serviceName:  s.destination?.service?.label  || '—',
  endpoint:     s.destination?.endpoint?.label || s.name || '—',
  duration:     s.duration  || 0,
  erroneous:    (s.errorCount ?? 0) > 0,
  errorMessage: (s.errorCount ?? 0) > 0 ? `${s.errorCount} error(s)` : null,
}));

const firstSpan = spanArray[0] ?? {};
return {
  traceId:   traceId,
  startTime: firstSpan.timestamp ?? Date.now(),
  duration:  firstSpan.duration  ?? 0,
  erroneous: spanArray.some((s) => (s.errorCount ?? 0) > 0),
  spans,
};
```
