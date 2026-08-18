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
  return instanaClient.request<TraceDetail>('GET', `/api/application-monitoring/analyze/traces/${traceId}`);
}
```

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

// Time-series: add rollupWindow (ms per bucket, min 60000)
async function getTimeSeriesMetrics(appId: string, windowMinutes: number): Promise<CallGroupItem[]> {
  const windowMs = windowMinutes * 60_000;
  const body = {
    timeFrame:   { to: Date.now(), windowSize: windowMs },
    tagFilters:  [{ name: 'application.id', operator: 'EQUALS', value: appId }],
    group:       { groupbyTag: 'service.name' },
    rollupWindow: Math.max(Math.round(windowMs / 30), 60_000), // ~30 buckets, min 1 min
    metrics: [
      { metric: 'calls',          aggregation: 'SUM' },
      { metric: 'erroneousCalls', aggregation: 'SUM' },
      { metric: 'latency',        aggregation: 'P95' },
    ],
  };
  const raw = await instanaClient.request<{ items: CallGroupItem[] }>(
    'POST', '/api/application-monitoring/analyze/call-groups', body,
  );
  return raw.items ?? [];
}
```
