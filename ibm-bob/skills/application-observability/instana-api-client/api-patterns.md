# Instana API Patterns (TypeScript / axios)

## Shared Client Structure (`src/lib/instanaClient.ts`)

```typescript
import axios, { AxiosInstance, AxiosResponse } from 'axios';

export class InstanaClient {
  private http: AxiosInstance;

  constructor(baseUrl: string, apiToken: string) {
    if (!apiToken) throw new ConfigurationError('INSTANA_API_TOKEN is required');
    this.http = axios.create({
      baseURL: baseUrl.replace(/\/$/, ''),
      timeout: 30_000,
      headers: {
        Authorization: `apiToken ${apiToken}`,
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor — centralised error mapping + rate-limit logging
    this.http.interceptors.response.use(
      (res) => {
        const remaining = res.headers['x-ratelimit-remaining'];
        if (remaining !== undefined) {
          const n = Number(remaining);
          if (n < 5)  console.warn(`[instana] Rate limit critical: ${n} requests remaining`);
          else if (n < 10) console.debug(`[instana] Rate limit low: ${n} requests remaining`);
        }
        return res;
      },
      (err) => Promise.reject(mapAxiosError(err)),
    );
  }

  /** Low-level request helper — all methods go through this */
  async request<T>(method: string, path: string, data?: unknown, params?: Record<string, unknown>): Promise<T> {
    const res: AxiosResponse<T> = await this.http.request({ method, url: path, data, params });
    return res.data;
  }
}

/** Singleton instance — create once, import everywhere */
import { getConfig } from './config';
const cfg = getConfig();
export const instanaClient = new InstanaClient(cfg.baseUrl, cfg.apiToken);
```

---

## Config Loader (`src/lib/config.ts`)

```typescript
export interface InstanaConfig {
  baseUrl: string;
  apiToken: string;
  timeoutMs: number;
  maxRetries: number;
}

export function getConfig(): InstanaConfig {
  // Vite exposes env vars via import.meta.env; Node uses process.env
  const baseUrl   = (import.meta?.env?.VITE_INSTANA_BASE_URL  ?? process.env.INSTANA_BASE_URL  ?? '').trim();
  const apiToken  = (import.meta?.env?.VITE_INSTANA_API_TOKEN ?? process.env.INSTANA_API_TOKEN ?? '').trim();

  if (!baseUrl)  throw new Error('VITE_INSTANA_BASE_URL / INSTANA_BASE_URL is required');
  if (!apiToken) throw new Error('VITE_INSTANA_API_TOKEN / INSTANA_API_TOKEN is required');

  return {
    baseUrl,
    apiToken,
    timeoutMs:  Number(import.meta?.env?.VITE_INSTANA_TIMEOUT_MS  ?? process.env.INSTANA_TIMEOUT_MS  ?? 30_000),
    maxRetries: Number(import.meta?.env?.VITE_INSTANA_MAX_RETRIES ?? process.env.INSTANA_MAX_RETRIES ?? 3),
  };
}
```

---

## Pagination Helper

Instana paginated responses follow this envelope:

```json
{ "items": [...], "page": 1, "pageSize": 50, "totalHits": 200 }
```

```typescript
interface PaginatedResponse<T> {
  items: T[];
  page: number;
  pageSize: number;
  totalHits: number;
}

async function paginate<T>(
  client: InstanaClient,
  path: string,
  params: Record<string, unknown> = {},
  pageSize = 100,
): Promise<T[]> {
  const results: T[] = [];
  let page = 1;

  while (true) {
    const data = await client.request<PaginatedResponse<T>>('GET', path, undefined, {
      ...params,
      page,
      pageSize,
    });
    results.push(...data.items);
    if (results.length >= data.totalHits) break;
    page++;
  }
  return results;
}
```

---

## Connection Validation

```typescript
export async function validateConnection(): Promise<void> {
  await instanaClient.request('GET', '/api/instana/health');
}
```

---

## Example Endpoint Methods

```typescript
// src/lib/instanaClient.ts (continued)

export interface Application { id: string; label: string; }
export interface Service     { id: string; label: string; }

export async function getApplications(): Promise<Application[]> {
  return paginate<Application>(instanaClient, '/api/application-monitoring/applications');
}

export async function getServices(appId: string): Promise<Service[]> {
  return paginate<Service>(instanaClient, '/api/application-monitoring/services', { applicationId: appId });
}

export async function getTraceDetail(traceId: string): Promise<TraceDetail> {
  // ⚠️ Only the /v2/ path works — /analyze/traces/{id} without /v2/ returns 404.
  // The response is { items: [...spans] } — no top-level trace object.
  // Span fields (raw API → mapped):
  //   s.id              → spanId
  //   s.parentId        → parentSpanId  (NOT s.parentSpanId)
  //   s.destination?.service?.label → serviceName  (NOT s.serviceName or s.service?.name)
  //   s.timestamp       → startTime     (NOT s.startTime)
  //   (s.errorCount??0)>0 → erroneous  (NOT s.erroneous — that field doesn't exist)
  const raw = await instanaClient.request<{ items: RawSpan[] }>(
    'GET', `/api/application-monitoring/v2/analyze/traces/${traceId}`
  );
  const rawSpans = raw.items ?? [];
  const spans = rawSpans.map((s) => ({
    spanId:       s.id                           ?? '',
    parentSpanId: s.parentId                     ?? null,
    name:         s.name                         ?? '—',
    serviceName:  s.destination?.service?.label  ?? '—',
    duration:     s.duration                     ?? 0,
    erroneous:    (s.errorCount ?? 0) > 0,
    errorMessage: (s.errorCount ?? 0) > 0 ? `${s.errorCount} error(s)` : null,
    startTime:    s.timestamp                    ?? null,
  }));
  const rootSpan = rawSpans.find((s) => !s.parentId) ?? rawSpans[0] ?? {};
  return {
    traceId,
    startTime: rootSpan.timestamp ?? null,
    duration:  rootSpan.duration  ?? 0,
    erroneous: spans.some((s) => s.erroneous),
    spans,
  };
}
```

---

## `metrics/services` and `metrics/endpoints` — Verified Working Pattern

> ⚠️ **Verified against live Instana API (`unit0-techzone.150-240-162-27.nip.io`).**
>
> These two endpoints share the same request/response shape. Key differences from `analyze/call-groups`:
> - **No `group` field required** — results are already grouped per service or endpoint.
> - **No `tagFilters` array** — use top-level `"applicationId"` string to scope.
> - **Service/endpoint name is in `.label`** — not `.name`. The field `item.service.name` and `item.endpoint.name` **do not exist**; use `item.service.label` and `item.endpoint.label`.
> - **Mixing calls + latency metrics in one request silently drops latency** — always send calls and latency in separate parallel requests.

```js
// src/services/instanaApi.js — fetchServiceMetrics (verified correct)

export async function fetchServiceMetrics(applicationId, timeRangeMinutes, signal) {
  const windowSize = timeRangeMinutes * 60 * 1000;
  const to         = Date.now();
  const commonBody = {
    applicationId,
    timeFrame: { windowSize, to },
    pagination: { page: 1, pageSize: 25 },
  };

  // ✅ Two parallel requests — mixing calls+latency in one request silently drops latency
  const [callsRes, latencyRes] = await Promise.all([
    api.post('/api/application-monitoring/metrics/services', {
      ...commonBody,
      metrics: [{ metric: 'calls', aggregation: 'SUM' }],           // → key: calls.sum
    }, { signal }),
    api.post('/api/application-monitoring/metrics/services', {
      ...commonBody,
      metrics: [
        { metric: 'latency', aggregation: 'MEAN' },                  // → key: latency.mean
        { metric: 'latency', aggregation: 'P95'  },                  // → key: latency.p95
      ],
    }, { signal }),
  ]);

  const callsItems   = callsRes.data?.items   ?? [];
  const latencyItems = latencyRes.data?.items ?? [];

  // ✅ item.service.label — NOT item.service.name (that field does not exist)
  const callsData = callsItems.map((item) => ({
    service: item.service?.label ?? 'Unknown',
    calls:   sumMetric(item.metrics?.['calls.sum']) ?? 0,
  })).filter((d) => d.calls > 0);

  const latencyData = latencyItems.map((item) => ({
    service:     item.service?.label ?? 'Unknown',
    meanLatency: Math.round(avgMetric(item.metrics?.['latency.mean']) ?? 0),  // ✅ 'latency.mean' NOT 'latency.mean.mean'
    p95Latency:  Math.round(avgMetric(item.metrics?.['latency.p95'])  ?? 0),  // ✅ 'latency.p95'  NOT 'latency.p95.p95'
  })).filter((d) => d.meanLatency > 0 || d.p95Latency > 0);

  return { callsData, latencyData };
}

// Identical pattern for endpoints — use /metrics/endpoints and item.endpoint.label
export async function fetchEndpointMetrics(applicationId, timeRangeMinutes, signal) {
  const windowSize = timeRangeMinutes * 60 * 1000;
  const to         = Date.now();
  const commonBody = {
    applicationId,
    timeFrame: { windowSize, to },
    pagination: { page: 1, pageSize: 25 },
  };

  const [callsRes, latencyRes] = await Promise.all([
    api.post('/api/application-monitoring/metrics/endpoints', {
      ...commonBody,
      metrics: [{ metric: 'calls', aggregation: 'SUM' }],
    }, { signal }),
    api.post('/api/application-monitoring/metrics/endpoints', {
      ...commonBody,
      metrics: [
        { metric: 'latency', aggregation: 'MEAN' },
        { metric: 'latency', aggregation: 'P95'  },
      ],
    }, { signal }),
  ]);

  const callsItems   = callsRes.data?.items   ?? [];
  const latencyItems = latencyRes.data?.items ?? [];

  // ✅ item.endpoint.label — NOT item.endpoint.name
  const callsData = callsItems.map((item) => ({
    endpoint: item.endpoint?.label ?? 'Unknown',
    calls:    sumMetric(item.metrics?.['calls.sum']) ?? 0,
  })).filter((d) => d.calls > 0);

  const latencyData = latencyItems.map((item) => ({
    endpoint:    item.endpoint?.label ?? 'Unknown',
    meanLatency: Math.round(avgMetric(item.metrics?.['latency.mean']) ?? 0),
    p95Latency:  Math.round(avgMetric(item.metrics?.['latency.p95'])  ?? 0),
  })).filter((d) => d.meanLatency > 0 || d.p95Latency > 0);

  return { callsData, latencyData };
}
```

### Common mistakes to avoid (`metrics/services` and `metrics/endpoints`)

| ❌ Wrong | ✅ Correct | Why |
|---------|-----------|-----|
| `{ metric: 'latency.mean', aggregation: 'MEAN' }` | `{ metric: 'latency', aggregation: 'MEAN' }` | `"latency.mean"` is not a valid metric name — returns HTTP 400 |
| `item.metrics['latency.mean.mean']` | `item.metrics['latency.mean']` | Response key is `latency.mean`, never double-suffixed |
| `item.metrics['latency.p95.p95']` | `item.metrics['latency.p95']` | Response key is `latency.p95`, never double-suffixed |
| `item.service?.name` | `item.service?.label` | The `.name` field does not exist on service objects |
| `item.endpoint?.name` | `item.endpoint?.label` | The `.name` field does not exist on endpoint objects |
| One request for calls + latency together | Two parallel requests | Sending both in one request causes only `calls.sum` to appear in response |

---

## Call Groups — Verified Working Example

```typescript
// Confirmed working against live Instana API.
// See instana-api-client/endpoint-reference.md for the full field-name correction table.

type CallGroupItem = {
  name: string;                              // value of the groupbyTag (e.g. service name)
  metrics: Record<string, number[][]>;       // key → [[timestamp_ms, value], ...]
};

async function getServiceMetrics(appId: string, windowMinutes: number): Promise<CallGroupItem[]> {
  const body = {
    timeFrame:  { to: Date.now(), windowSize: windowMinutes * 60_000 },  // ← real timestamp, NOT 0
    tagFilters: [{ name: 'application.id', operator: 'EQUALS', value: appId }],
    group:      { groupbyTag: 'service.name' },                           // ← always required
    metrics: [
      { metric: 'calls',          aggregation: 'SUM' },   // → response key: calls.sum
      { metric: 'erroneousCalls', aggregation: 'SUM' },   // → response key: erroneousCalls.sum
      { metric: 'latency',        aggregation: 'P50' },   // → response key: latency.p50
      { metric: 'latency',        aggregation: 'P95' },   // → response key: latency.p95
      { metric: 'latency',        aggregation: 'P99' },   // → response key: latency.p99
    ],
  };

  const raw = await instanaClient.request<{ items: CallGroupItem[] }>(
    'POST', '/api/application-monitoring/analyze/call-groups', body,
  );
  return raw.items ?? [];
}

// Time-series: add rollupWindow using a fixed ladder — NOT dynamic division.
// Dynamic division (windowMs / 30) produces a value the server rounds up to
// the full windowSize, returning Array(1) per metric and making charts invisible.
//
// Ladder (window → bucket → ~N points):
//   ≤ 30 min  →  1 min  → up to 30 pts
//   ≤  3 hr   →  5 min  → up to 36 pts
//   ≤ 12 hr   → 15 min  → up to 48 pts
//   ≤ 24 hr   → 30 min  → up to 48 pts
//   > 24 hr   → 60 min
function buildRollupWindow(windowMinutes: number): number {
  if (windowMinutes <= 30)   return  1 * 60 * 1000;
  if (windowMinutes <= 180)  return  5 * 60 * 1000;
  if (windowMinutes <= 720)  return 15 * 60 * 1000;
  if (windowMinutes <= 1440) return 30 * 60 * 1000;
  return                            60 * 60 * 1000;
}

async function getTimeSeriesMetrics(appId: string, windowMinutes: number): Promise<CallGroupItem[]> {
  const windowMs = windowMinutes * 60_000;
  const body = {
    timeFrame:    { to: Date.now(), windowSize: windowMs },
    tagFilters:   [{ name: 'application.id', operator: 'EQUALS', value: appId }],
    group:        { groupbyTag: 'service.name' },
    rollupWindow: buildRollupWindow(windowMinutes),
    metrics: [
      { metric: 'calls',          aggregation: 'SUM' },
      { metric: 'erroneousCalls', aggregation: 'SUM' },
      { metric: 'latency',        aggregation: 'P50' },
      { metric: 'latency',        aggregation: 'P95' },
    ],
  };
  const raw = await instanaClient.request<{ items: CallGroupItem[] }>(
    'POST', '/api/application-monitoring/analyze/call-groups', body,
  );
  return raw.items ?? [];
}
```

---

## Time-Series Bucket Merge Pattern (multi-service)

When the time-series request groups by `service.name`, the API returns **one item per service**, each carrying its own independent `[[timestamp_ms, value]]` arrays. To produce chart-ready data you must merge all services into a single bucket-map keyed by timestamp.

### ⚠️ Critical: seed buckets from ALL metric arrays, not just `calls`

The naive approach seeds a bucket only when a `calls.sum` data point is encountered, then guards all other metrics with `if (bucketMap[ts])`. This silently drops latency and error data at any timestamp where `calls.sum` happens to be `null` (Instana returns `null`, not `0`, for empty buckets). Result: `latencyTimeSeries` and `errorRateTimeSeries` appear empty even when the API returns data.

**Wrong — latency/error data silently dropped when calls is null at that ts:**
```js
callsData.forEach(([ts, v]) => {
  if (!bucketMap[ts]) bucketMap[ts] = { ... }; // ❌ only seeds from calls
  bucketMap[ts].calls += (v ?? 0);
});
latencyData.forEach(([ts, v]) => {
  if (v !== null && bucketMap[ts]) {            // ❌ silently skipped if bucket missing
    bucketMap[ts].latencySum += v;
  }
});
```

**Correct — pre-seed ALL timestamps from ALL metric arrays first:**
```js
const bucketMap = {};

const ensureBucket = (ts) => {
  if (!bucketMap[ts]) bucketMap[ts] = { calls: 0, erroneous: 0, meanSum: 0, meanCount: 0, p95max: null };
};

items.forEach((item) => {
  const callsData = item.metrics?.['calls.sum']          ?? [];
  const errData   = item.metrics?.['erroneousCalls.sum'] ?? [];
  const meanData  = item.metrics?.['latency.p50']        ?? [];
  const p95Data   = item.metrics?.['latency.p95']        ?? [];

  // ✅ Pre-seed every timestamp present in ANY metric array
  [callsData, errData, meanData, p95Data].forEach((arr) => {
    arr.forEach(([ts]) => ensureBucket(ts));
  });

  // Now all buckets exist — accumulate safely
  callsData.forEach(([ts, v]) => { bucketMap[ts].calls     += (v ?? 0); });
  errData  .forEach(([ts, v]) => { bucketMap[ts].erroneous += (v ?? 0); });
  meanData .forEach(([ts, v]) => {
    if (v !== null) { bucketMap[ts].meanSum += v; bucketMap[ts].meanCount += 1; }
  });
  p95Data  .forEach(([ts, v]) => {
    if (v !== null) {
      bucketMap[ts].p95max = bucketMap[ts].p95max === null ? v : Math.max(bucketMap[ts].p95max, v);
    }
  });
});

// Sort by timestamp and map to chart-ready shape
const sorted = Object.entries(bucketMap).sort(([a], [b]) => Number(a) - Number(b));

const callsTimeSeries = sorted.map(([ts, b]) => ({
  time:  new Date(Number(ts)).toLocaleString(),
  calls: b.calls,
}));

const latencyTimeSeries = sorted.map(([ts, b]) => ({
  time: new Date(Number(ts)).toLocaleString(),
  mean: b.meanCount > 0 ? Math.round(b.meanSum / b.meanCount) : 0,
  p95:  b.p95max ?? 0,
}));

const errorRateTimeSeries = sorted.map(([ts, b]) => ({
  time:      new Date(Number(ts)).toLocaleString(),
  errorRate: b.calls > 0 ? (b.erroneous / b.calls) * 100 : 0,
}));
```

**Rule:** always pre-seed all timestamps before accumulating. Never guard an accumulation step with `if (bucketMap[ts])` — the pre-seed pass guarantees the bucket exists.
