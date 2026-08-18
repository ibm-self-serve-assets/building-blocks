# API Client Performance Patterns (TypeScript / React)

## 1 — Axios Instance Reuse

Create the `axios` instance **once** in `instanaClient.ts` and export it as a singleton. Never call `axios.create()` inside a component, hook, or per-request function.

```typescript
// ✅ Correct — instance created once at module load
export const instanaClient = new InstanaClient(cfg.baseUrl, cfg.apiToken);

// ❌ Wrong — new instance per request
async function getApplications() {
  const http = axios.create(...); // never do this inside a function
}
```

---

## 2 — Request Timeout

Set `timeout` on the axios instance constructor — it applies to every request automatically.

```typescript
this.http = axios.create({
  baseURL: baseUrl,
  timeout: 30_000,  // 30 seconds
  headers: { Authorization: `apiToken ${apiToken}` },
});
```

---

## 3 — React Query as the Cache Layer

For a React app, use `@tanstack/react-query` as the cache — do not build a manual TTL cache. Configure `staleTime` per query based on how frequently the data changes:

```typescript
// Stable data — application and service lists change rarely
useQuery({ queryKey: ['applications'], queryFn: getApplications, staleTime: 60_000 });

// Live data — traces and metrics must always be fresh
useQuery({ queryKey: ['traces', appId], queryFn: () => getTraces(appId!), staleTime: 0 });

// Auto-refresh live panels every 30 s without blocking the UI
useQuery({ queryKey: ['kpi', appId], queryFn: () => getKpi(appId!), refetchInterval: 30_000 });
```

**Cache-eligible (high `staleTime`):** application list, service list, SLO definitions, endpoint list.  
**Never cache (staleTime: 0):** traces, call-group analysis, events, infrastructure snapshots.

---

## 4 — Parallel Fetching with `Promise.all`

When a component or script needs data from multiple independent endpoints, fetch in parallel:

```typescript
// ✅ Parallel — both requests fire simultaneously
const [apps, services] = await Promise.all([
  getApplications(),
  getServices(appId),
]);

// ❌ Sequential — services waits for applications to finish first
const apps     = await getApplications();
const services = await getServices(appId);
```

In React, place independent `useQuery` calls at the top of the component — React Query fires them in parallel automatically:

```tsx
function Dashboard({ appId }: { appId: string }) {
  const { data: kpi }    = useKpiMetrics(appId, 60);   // fires in parallel
  const { data: traces } = useTraces(appId, 60);        // fires in parallel
  // ...
}
```

---

## 5 — Prefetching on Hover

Prefetch trace detail data when the user hovers over a trace row so the modal opens instantly:

```tsx
import { useQueryClient } from '@tanstack/react-query';
import { getTraceDetail } from '../lib/instanaClient';

function TraceRow({ trace, onTraceClick }) {
  const qc = useQueryClient();

  const prefetch = () =>
    qc.prefetchQuery({
      queryKey: ['trace', trace.traceId],
      queryFn: () => getTraceDetail(trace.traceId),
      staleTime: 300_000,
    });

  return (
    <tr onMouseEnter={prefetch}>
      <td>
        <button onClick={() => onTraceClick(trace.traceId)}>
          {trace.traceId.slice(0, 8)}…
        </button>
      </td>
      {/* ... */}
    </tr>
  );
}
```

---

## 6 — Axios Response Interceptor for Rate-Limit Logging

Add this to the axios instance in `InstanaClient` constructor:

```typescript
this.http.interceptors.response.use((res) => {
  const remaining = Number(res.headers['x-ratelimit-remaining']);
  if (!isNaN(remaining)) {
    if (remaining < 5)  console.warn(`[instana] Rate limit critical: ${remaining} remaining`);
    else if (remaining < 10) console.debug(`[instana] Rate limit low: ${remaining} remaining`);
  }
  return res;
}, (err) => Promise.reject(mapAxiosError(err)));
```

---

## 7 — Scripts: Parallel Fetch with `Promise.allSettled`

In non-React Node.js scripts, use `Promise.allSettled` to collect as much data as possible even if one endpoint fails:

```typescript
const results = await Promise.allSettled([
  getApplications(),
  getServices(appId),
  getCallGroupMetrics({ appId, windowMinutes: 60 }),
]);

results.forEach((r, i) => {
  if (r.status === 'rejected') console.error(`Task ${i} failed:`, r.reason);
});
```
