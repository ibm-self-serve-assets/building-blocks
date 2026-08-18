# Dashboard Patterns (React + TypeScript)

## App Layout Skeleton (`src/App.tsx`)

```tsx
import { useState, useReducer } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Header from './components/Header';
import KpiRow from './components/KpiRow';
import ErrorRateChart from './components/charts/ErrorRateChart';
import LatencyChart from './components/charts/LatencyChart';
import CallVolumeChart from './components/charts/CallVolumeChart';
import TraceTable from './components/TraceTable';
import TraceDetailModal from './components/TraceDetailModal';
import { filterReducer, initialFilterState } from './hooks/useFilters';

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  );
}

function Dashboard() {
  const [filters, dispatch] = useReducer(filterReducer, initialFilterState);
  const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);

  return (
    <div className="dashboard">
      <Header filters={filters} dispatch={dispatch} />
      <KpiRow appId={filters.appId} windowMinutes={filters.windowMinutes} />
      <div className="chart-grid">
        <ErrorRateChart appId={filters.appId} windowMinutes={filters.windowMinutes} />
        <LatencyChart appId={filters.appId} windowMinutes={filters.windowMinutes} />
        <CallVolumeChart appId={filters.appId} windowMinutes={filters.windowMinutes} />
      </div>
      <TraceTable
        appId={filters.appId}
        windowMinutes={filters.windowMinutes}
        errorsOnly={filters.errorsOnly}
        minLatencyMs={filters.minLatencyMs}
        onTraceClick={setSelectedTraceId}
      />
      {selectedTraceId && (
        <TraceDetailModal
          traceId={selectedTraceId}
          onClose={() => setSelectedTraceId(null)}
        />
      )}
    </div>
  );
}
```

---

## Filter State (`src/hooks/useFilters.ts`)

```ts
export interface FilterState {
  appId: string | null;
  serviceId: string | null;
  windowMinutes: number;
  errorsOnly: boolean;
  minLatencyMs: number;
}

export const initialFilterState: FilterState = {
  appId: null,
  serviceId: null,
  windowMinutes: 60,
  errorsOnly: false,
  minLatencyMs: 0,
};

type FilterAction =
  | { type: 'SET_APP';        appId: string }
  | { type: 'SET_SERVICE';    serviceId: string | null }
  | { type: 'SET_WINDOW';     windowMinutes: number }
  | { type: 'SET_ERRORS_ONLY'; errorsOnly: boolean }
  | { type: 'SET_MIN_LATENCY'; minLatencyMs: number }
  | { type: 'RESET' };

export function filterReducer(state: FilterState, action: FilterAction): FilterState {
  switch (action.type) {
    case 'SET_APP':     return { ...state, appId: action.appId, serviceId: null };
    case 'SET_SERVICE': return { ...state, serviceId: action.serviceId };
    case 'SET_WINDOW':  return { ...state, windowMinutes: action.windowMinutes };
    case 'SET_ERRORS_ONLY': return { ...state, errorsOnly: action.errorsOnly };
    case 'SET_MIN_LATENCY': return { ...state, minLatencyMs: action.minLatencyMs };
    case 'RESET':       return initialFilterState;
    default:            return state;
  }
}
```

---

## Data-Fetch Hooks (`src/hooks/useInstanaData.ts`)

```ts
import { useQuery } from '@tanstack/react-query';
import { instanaClient } from '../lib/instanaClient';

/** Applications list — cached for 60 s */
export function useApplications() {
  return useQuery({
    queryKey: ['applications'],
    queryFn: () => instanaClient.getApplications(),
    staleTime: 60_000,
  });
}

/** Services for a selected application — re-fetches on appId change */
export function useServices(appId: string | null) {
  return useQuery({
    queryKey: ['services', appId],
    queryFn: () => instanaClient.getServices(appId!),
    enabled: !!appId,
    staleTime: 60_000,
  });
}

/** Traces — always fresh (staleTime: 0) */
export function useTraces(appId: string | null, windowMinutes: number, errorsOnly = false) {
  return useQuery({
    queryKey: ['traces', appId, windowMinutes, errorsOnly],
    queryFn: () => instanaClient.getTraces({ appId: appId!, windowMinutes, errorsOnly }),
    enabled: !!appId,
    staleTime: 0,
    refetchInterval: 30_000,   // auto-refresh every 30 s
  });
}

/** Lazy-fetch a single trace tree — only fires when traceId is set */
export function useTraceDetail(traceId: string | null) {
  return useQuery({
    queryKey: ['trace', traceId],
    queryFn: () => instanaClient.getTraceDetail(traceId!),
    enabled: !!traceId,
    staleTime: 300_000,  // trace detail is immutable; cache for 5 min
  });
}

/** KPI metrics — error rate, latency percentiles, call count */
export function useKpiMetrics(appId: string | null, windowMinutes: number) {
  return useQuery({
    queryKey: ['kpi', appId, windowMinutes],
    queryFn: () => instanaClient.getCallGroupMetrics({ appId: appId!, windowMinutes }),
    enabled: !!appId,
    staleTime: 0,
    refetchInterval: 30_000,
  });
}
```

---

## KPI Card Component (`src/components/KpiCard.tsx`)

```tsx
type Status = 'healthy' | 'degraded' | 'error';

interface KpiCardProps {
  label: string;
  value: string;
  status?: Status;
}

const statusColour: Record<Status, string> = {
  healthy:  'var(--color-healthy)',
  degraded: 'var(--color-degraded)',
  error:    'var(--color-error)',
};

export default function KpiCard({ label, value, status = 'healthy' }: KpiCardProps) {
  return (
    <div className="kpi-card" style={{ borderColor: statusColour[status] }}>
      <span className="kpi-label">{label}</span>
      <span className="kpi-value" style={{ color: statusColour[status] }}>{value}</span>
    </div>
  );
}
```

---

## Loading & Error State Pattern

Use React Query's `isLoading` and `isError` directly — no need for extra state:

```tsx
// ⚠️ The traces response wraps each item in a 'trace' envelope.
// The getTraces() client method must map item.trace.* to flat fields.
// See endpoint-reference.md § Traces Response Shape for the full verified shape.

export default function TraceTable({ appId, windowMinutes, onTraceClick }) {
  const { data, isLoading, isError, error } = useTraces(appId, windowMinutes);
  const traces = data?.items ?? [];

  if (!appId)    return <p className="hint">Select an application to load traces.</p>;
  if (isLoading) return <div className="spinner" aria-label="Loading traces…" />;
  if (isError)   return <p className="error-text">Failed to load traces: {String(error)}</p>;

  return (
    <table className="trace-table">
      <tbody>
        {traces.map((trace) => (
          <tr key={trace.traceId}>
            <td>
              <button className="trace-id-btn" onClick={() => onTraceClick(trace.traceId)}>
                {trace.traceId?.slice(0, 8)}…
              </button>
            </td>
            <td>{trace.serviceName}</td>
            <td>{trace.endpoint}</td>
            <td>{trace.duration} ms</td>
            <td>{trace.erroneous ? 'Error' : 'OK'}</td>
            <td>{new Date(trace.timestamp).toLocaleTimeString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```
