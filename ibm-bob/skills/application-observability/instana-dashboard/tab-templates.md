# Tab Reference Implementations

The three tab components define the fixed layout for each primary tab. Implement them exactly as shown. Do not add, remove, or reorder sections.

---

## `src/tabs/ServiceOverview.jsx`

```jsx
import { useEffect, useState, useCallback, useRef } from 'react';
import { Grid, Column } from '@carbon/react';
import { DASHBOARD_CONFIG } from '../config/dashboardConfig';
import KPICard    from '../components/KPICard';
import ChartCard  from '../components/ChartCard';
import ServiceCallsChart       from '../charts/ServiceCallsChart';
import ServiceLatencyChart     from '../charts/ServiceLatencyChart';
import EndpointCallsChart      from '../charts/EndpointCallsChart';
import EndpointLatencyChart    from '../charts/EndpointLatencyChart';
import StatusDistributionChart from '../charts/StatusDistributionChart';

import {
  fetchMetrics,
  fetchServiceMetrics,
  fetchEndpointMetrics,
} from '../services/instanaApi';
import { computeKpis, computeStatus } from '../services/analysisService';

const CHART_COMPONENTS = {
  ServiceCallsChart,
  ServiceLatencyChart,
  EndpointCallsChart,
  EndpointLatencyChart,
  StatusDistributionChart,
};

export default function ServiceOverview({ timeRange }) {
  const [metrics,          setMetrics]          = useState(null);
  const [serviceMetrics,   setServiceMetrics]   = useState(null);
  const [endpointMetrics,  setEndpointMetrics]  = useState(null);
  const [loading,          setLoading]          = useState(true);
  const [error,            setError]            = useState(null);
  const abortRef = useRef(null);

  const loadData = useCallback(async () => {
    // Cancel any in-flight request
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    setError(null);

    try {
      const appId = DASHBOARD_CONFIG.applicationId;
      const [m, sm, em] = await Promise.all([
        fetchMetrics(appId, timeRange, controller.signal),
        fetchServiceMetrics(appId, timeRange, controller.signal),
        fetchEndpointMetrics(appId, timeRange, controller.signal),
      ]);
      if (!controller.signal.aborted) {
        setMetrics(m);
        setServiceMetrics(sm);
        setEndpointMetrics(em);
        setLoading(false);
      }
    } catch (err) {
      if (!controller.signal.aborted) {
        setError(err.message || 'Failed to load Service Overview data.');
        setLoading(false);
      }
    }
  }, [timeRange]);

  // Initial load + refresh interval
  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, DASHBOARD_CONFIG.refreshInterval);
    return () => {
      clearInterval(interval);
      if (abortRef.current) abortRef.current.abort();
    };
  }, [loadData]);

  // Compute KPI values from metrics
  const kpiValues = metrics ? computeKpis(metrics) : {};

  // Chart data keyed by dashboardConfig.charts[].dataKey
  const chartData = {
    serviceCallsData:      serviceMetrics?.callsData      ?? [],
    serviceLatencyData:    serviceMetrics?.latencyData    ?? [],
    endpointCallsData:     endpointMetrics?.callsData     ?? [],
    endpointLatencyData:   endpointMetrics?.latencyData   ?? [],
    statusDistribution:    metrics?.statusDistribution    ?? [],
  };

  return (
    <div className="tab-content">
      {/* ── KPI Row ─────────────────────────────────────────── */}
      <div className="kpi-row">
        {DASHBOARD_CONFIG.kpis.map((kpi) => (
          <KPICard
            key={kpi.id}
            label={kpi.label}
            unit={kpi.unit}
            value={loading ? null : (kpiValues[kpi.field] ?? null)}
            status={loading ? 'unknown' : computeStatus(kpiValues[kpi.field], kpi.thresholds)}
          />
        ))}
      </div>

      {/* ── Charts: 3 rows × 2 columns ───────────────────────── */}
      {[1, 2, 3].map((row) => {
        const rowCharts = DASHBOARD_CONFIG.charts.filter((c) => c.row === row);

        // While loading or errored, render every chart card in the row.
        // Once data is available, skip charts that have no data — do not
        // render empty placeholder tiles.
        const visibleCharts = rowCharts.filter((chartDef) => {
          if (loading || error) return true;
          return (chartData[chartDef.dataKey] ?? []).length > 0;
        });

        // If no chart in this row has data (and not loading/errored),
        // skip the entire row — render nothing.
        if (!loading && !error && visibleCharts.length === 0) return null;

        return (
          <Grid fullWidth key={row} className="chart-row">
            {(loading || error ? rowCharts : visibleCharts).map((chartDef) => {
              const ChartComp = CHART_COMPONENTS[chartDef.component];
              const data      = chartData[chartDef.dataKey] ?? [];

              return (
                <Column sm={4} md={4} lg={8} key={chartDef.id} className="chart-column">
                  <ChartCard
                    title={chartDef.title}
                    isLoading={loading}
                    isError={!!error}
                    errorMessage={error}
                    chart={ChartComp ? <ChartComp data={data} /> : null}
                  />
                </Column>
              );
            })}
          </Grid>
        );
      })}
    </div>
  );
}
```

---

## `src/tabs/TraceDetails.jsx`

```jsx
import { useEffect, useState, useCallback, useRef } from 'react';
import { Grid, Column } from '@carbon/react';
import { DASHBOARD_CONFIG } from '../config/dashboardConfig';
import KPICard         from '../components/KPICard';
import TraceTable      from '../components/TraceTable';
import TraceDetailView from '../components/TraceDetailView';
import LoadingState    from '../components/LoadingState';
import ErrorState      from '../components/ErrorState';
import { fetchTraces, fetchTraceDetail } from '../services/instanaApi';
import { computeTraceKpis } from '../services/analysisService';

// Filter components — see carbon-components.md for full FilterBar implementation
import {
  Dropdown, NumberInput, Toggle, Grid as CGrid, Column as CColumn,
} from '@carbon/react';

export default function TraceDetails({ timeRange: globalTimeRange }) {
  // Filter state
  const [selectedTimeRange, setSelectedTimeRange] = useState(
    DASHBOARD_CONFIG.timeRangeOptions.find((o) => o.minutes === DASHBOARD_CONFIG.defaultTimeRange)
      ?? DASHBOARD_CONFIG.timeRangeOptions[2]
  );
  const [selectedService,  setSelectedService]  = useState(null);
  const [selectedEndpoint, setSelectedEndpoint] = useState(null);
  const [minLatency,       setMinLatency]        = useState(0);
  const [errorsOnly,       setErrorsOnly]        = useState(false);

  // Data state
  const [traces,       setTraces]       = useState([]);
  const [traceDetail,  setTraceDetail]  = useState(null);
  const [services,     setServices]     = useState([]);
  const [endpoints,    setEndpoints]    = useState([]);
  const [selectedTrace, setSelectedTrace] = useState(null);
  const [loading,       setLoading]     = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error,         setError]       = useState(null);
  const [detailError,   setDetailError] = useState(null);
  const abortRef = useRef(null);

  const loadTraces = useCallback(async () => {
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    setError(null);

    try {
      const result = await fetchTraces(
        DASHBOARD_CONFIG.applicationId,
        {
          timeRangeMinutes: selectedTimeRange.minutes,
          service:   selectedService?.name  ?? null,
          endpoint:  selectedEndpoint?.name ?? null,
          minLatency,
          errorsOnly,
        },
        controller.signal
      );

      if (!controller.signal.aborted) {
        setTraces(result.traces ?? []);
        setServices(result.services ?? []);
        setEndpoints(result.endpoints ?? []);
        setLoading(false);
      }
    } catch (err) {
      if (!controller.signal.aborted) {
        setError(err.message || 'Failed to load traces.');
        setLoading(false);
      }
    }
  }, [selectedTimeRange, selectedService, selectedEndpoint, minLatency, errorsOnly]);

  // Reload on filter change
  useEffect(() => { loadTraces(); }, [loadTraces]);

  // Load trace detail on selection
  const handleTraceSelect = async (trace) => {
    setSelectedTrace(trace);
    setTraceDetail(null);
    setDetailError(null);
    setDetailLoading(true);
    try {
      const detail = await fetchTraceDetail(trace.traceId);
      setTraceDetail(detail);
    } catch (err) {
      setDetailError(err.message || 'Failed to load trace detail.');
    } finally {
      setDetailLoading(false);
    }
  };

  const traceKpiValues = computeTraceKpis(traces, DASHBOARD_CONFIG.thresholds.slowTrace);

  return (
    <div className="tab-content">
      {/* ── Section 1: Trace Filters ─────────────────────────── */}
      <section className="tab-section">
        <CGrid fullWidth className="filter-bar">
          <CColumn sm={4} md={2} lg={3}>
            <Dropdown
              id="filter-time-range"
              titleText="Time Range"
              label="Select range"
              items={DASHBOARD_CONFIG.timeRangeOptions}
              itemToString={(item) => item?.label ?? ''}
              selectedItem={selectedTimeRange}
              onChange={({ selectedItem }) => setSelectedTimeRange(selectedItem)}
            />
          </CColumn>
          <CColumn sm={4} md={2} lg={3}>
            <Dropdown
              id="filter-service"
              titleText="Service"
              label="All services"
              items={[{ id: null, name: 'All services' }, ...services]}
              itemToString={(item) => item?.name ?? 'All services'}
              selectedItem={selectedService}
              onChange={({ selectedItem }) => setSelectedService(selectedItem?.id ? selectedItem : null)}
            />
          </CColumn>
          <CColumn sm={4} md={2} lg={3}>
            <Dropdown
              id="filter-endpoint"
              titleText="Endpoint"
              label="All endpoints"
              items={[{ id: null, name: 'All endpoints' }, ...endpoints]}
              itemToString={(item) => item?.name ?? 'All endpoints'}
              selectedItem={selectedEndpoint}
              onChange={({ selectedItem }) => setSelectedEndpoint(selectedItem?.id ? selectedItem : null)}
            />
          </CColumn>
          <CColumn sm={2} md={1} lg={2}>
            <NumberInput
              id="filter-min-latency"
              label="Min Latency (ms)"
              min={0} step={100}
              value={minLatency}
              onChange={(e, { value }) => setMinLatency(Number(value) || 0)}
            />
          </CColumn>
          <CColumn sm={2} md={1} lg={2} className="filter-bar__toggle">
            <Toggle
              id="filter-errors-only"
              labelText="Error Status"
              labelA="All"
              labelB="Errors Only"
              toggled={errorsOnly}
              onToggle={setErrorsOnly}
            />
          </CColumn>
        </CGrid>
      </section>

      {/* ── Section 2: Trace Summary KPIs ────────────────────── */}
      <section className="tab-section">
        <div className="kpi-row">
          {DASHBOARD_CONFIG.traceKpis.map((kpi) => (
            <KPICard
              key={kpi.id}
              label={kpi.label}
              unit={kpi.unit || ''}
              value={loading ? null : (traceKpiValues[kpi.field] ?? null)}
              status="unknown"
            />
          ))}
        </div>
      </section>

      {/* ── Section 3: Trace Table ───────────────────────────── */}
      <section className="tab-section">
        {loading && <LoadingState description="Loading traces…" />}
        {!loading && error && <ErrorState message={error} />}
        {!loading && !error && (
          <TraceTable
            traces={traces}
            onTraceSelect={handleTraceSelect}
          />
        )}
      </section>

      {/* ── Section 4: Trace Detail View (conditional) ───────── */}
      {selectedTrace && (
        <TraceDetailView
          trace={traceDetail}
          isLoading={detailLoading}
          isError={!!detailError}
          onClose={() => { setSelectedTrace(null); setTraceDetail(null); }}
        />
      )}
    </div>
  );
}
```

---

## `src/tabs/IntelligentAnalysis.jsx`

```jsx
// src/tabs/IntelligentAnalysis.jsx
import { useEffect, useState, useCallback, useRef } from 'react';
import { Tile, InlineNotification } from '@carbon/react';
import { DASHBOARD_CONFIG } from '../config/dashboardConfig';
import InsightPanel from '../components/InsightPanel';
import LoadingState from '../components/LoadingState';
import ErrorState   from '../components/ErrorState';
import {
  fetchMetrics,
  fetchServiceMetrics,
  fetchEndpointMetrics,
  fetchTraces,
} from '../services/instanaApi';
import {
  analyzeHealth,
  identifySlowServices,
  identifySlowEndpoints,
  analyzeErrors,
  identifyBottlenecks,
  generateRecommendations,
} from '../services/analysisService';

export default function IntelligentAnalysis({ timeRange }) {
  const [analysis, setAnalysis] = useState(null);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState(null);
  const abortRef = useRef(null);

  const loadAnalysis = useCallback(async () => {
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    // Keep existing data visible during re-fetch
    setError(null);
    if (!analysis) setLoading(true);

    try {
      const appId = DASHBOARD_CONFIG.applicationId;
      const [metrics, serviceMetrics, endpointMetrics, tracesResult] = await Promise.all([
        fetchMetrics(appId, timeRange, controller.signal),
        fetchServiceMetrics(appId, timeRange, controller.signal),
        fetchEndpointMetrics(appId, timeRange, controller.signal),
        fetchTraces(appId, { timeRangeMinutes: timeRange }, controller.signal),
      ]);

      if (controller.signal.aborted) return;

      const thresholds = DASHBOARD_CONFIG.analysisThresholds;
      const traces     = tracesResult?.traces ?? [];

      const analysisResult = {
        health:          analyzeHealth(metrics, serviceMetrics, endpointMetrics),
        slowServices:    identifySlowServices(serviceMetrics, thresholds),
        slowEndpoints:   identifySlowEndpoints(endpointMetrics, thresholds),
        errors:          analyzeErrors(metrics, serviceMetrics, endpointMetrics, thresholds),
        bottlenecks:     identifyBottlenecks(traces, serviceMetrics, endpointMetrics, thresholds),
        recommendations: generateRecommendations(
          { metrics, serviceMetrics, endpointMetrics, traces },
          thresholds
        ),
      };

      setAnalysis(analysisResult);
      setLoading(false);
    } catch (err) {
      if (!controller.signal.aborted) {
        setError(err.message || 'Failed to load analysis data.');
        setLoading(false);
      }
    }
  }, [timeRange]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    loadAnalysis();
    const interval = setInterval(loadAnalysis, DASHBOARD_CONFIG.refreshInterval);
    return () => {
      clearInterval(interval);
      if (abortRef.current) abortRef.current.abort();
    };
  }, [loadAnalysis]);

  if (loading)  return <LoadingState description="Analyzing application telemetry…" />;
  if (error)    return <ErrorState message={error} />;
  if (!analysis) return null;

  const { health, slowServices, slowEndpoints, errors, bottlenecks, recommendations } = analysis;

  return (
    <div className="tab-content">

      {/* ── Section 1: Application Health Summary ───────────── */}
      <section className="tab-section">
        <p className="section-title">Application Health Summary</p>
        <Tile className={`health-summary health-summary--${health.status}`}>
          <div className="health-summary__status">
            <span className={`health-badge health-badge--${health.status}`}>
              {health.status === 'healthy'
                ? '✓ Healthy'
                : health.status === 'degraded'
                ? '⚠ Degraded'
                : health.status === 'critical'
                ? '✗ Critical'
                : '— Unknown'}
            </span>
          </div>
          <p className="health-summary__narrative">{health.narrative}</p>
          <div className="health-summary__metrics">
            <HealthMetric label="Request Volume"  value={health.requestVolume} />
            <HealthMetric label="Latency"         value={health.latencyStatus} />
            <HealthMetric label="Error Rate"      value={health.errorStatus}   />
            <HealthMetric label="Active Services" value={health.serviceStatus} />
          </div>
        </Tile>
      </section>

      {/* ── Section 2: Performance Insights ─────────────────── */}
      <section className="tab-section">
        <p className="section-title">Performance Insights</p>
        {slowServices.length === 0 && slowEndpoints.length === 0 ? (
          <InlineNotification
            kind="info"
            title="All clear"
            subtitle="No performance degradation detected in the current time window."
            hideCloseButton
            lowContrast
          />
        ) : (
          [...slowServices, ...slowEndpoints].map((item, i) => (
            <InsightPanel
              key={i}
              finding={item.finding}
              evidence={item.evidence}
              impact={item.impact}
              action={item.action}
              severity={item.severity || 'warning'}
            />
          ))
        )}
      </section>

      {/* ── Section 3: Error Analysis ────────────────────────── */}
      <section className="tab-section">
        <p className="section-title">Error Analysis</p>
        {errors.length === 0 ? (
          <InlineNotification
            kind="info"
            title="All clear"
            subtitle="No elevated error rates detected in the current time window."
            hideCloseButton
            lowContrast
          />
        ) : (
          errors.map((item, i) => (
            <InsightPanel
              key={i}
              finding={item.finding}
              evidence={item.evidence}
              impact={item.impact}
              action={item.action}
              severity={item.severity || 'error'}
            />
          ))
        )}
      </section>

      {/* ── Section 4: Bottleneck Analysis ──────────────────── */}
      <section className="tab-section">
        <p className="section-title">Bottleneck Analysis</p>
        {bottlenecks.length === 0 ? (
          <InlineNotification
            kind="info"
            title="All clear"
            subtitle="No bottlenecks identified in the current time window."
            hideCloseButton
            lowContrast
          />
        ) : (
          bottlenecks.map((item, i) => (
            <InsightPanel
              key={i}
              finding={item.finding}
              evidence={item.evidence}
              impact={item.impact}
              action={item.action}
              severity={item.severity || 'warning'}
            />
          ))
        )}
      </section>

      {/* ── Section 5: Recommended Actions ──────────────────── */}
      <section className="tab-section">
        <p className="section-title">Recommended Actions</p>
        {recommendations.length === 0 ? (
          <InlineNotification
            kind="info"
            title="All clear"
            subtitle="No actionable recommendations at this time."
            hideCloseButton
            lowContrast
          />
        ) : (
          recommendations.map((rec, i) => (
            <InsightPanel
              key={i}
              finding={rec.finding}
              evidence={rec.evidence}
              impact={rec.impact}
              action={rec.action}
              severity={rec.severity || 'info'}
            />
          ))
        )}
      </section>

    </div>
  );
}

function HealthMetric({ label, value }) {
  return (
    <div className="health-metric">
      <span className="health-metric__label">{label}</span>
      <span className="health-metric__value">{value || '—'}</span>
    </div>
  );
}
```

---

## `src/App.jsx`

```jsx
import '@carbon/styles/css/styles.css';
import './App.css';
import { useState } from 'react';
import { Tabs, TabList, Tab, TabPanels, TabPanel } from '@carbon/react';
import AppHeader         from './components/AppHeader';
import ServiceOverview   from './tabs/ServiceOverview';
import TraceDetails      from './tabs/TraceDetails';
import IntelligentAnalysis from './tabs/IntelligentAnalysis';
import { DASHBOARD_CONFIG } from './config/dashboardConfig';

export default function App() {
  const defaultRange = DASHBOARD_CONFIG.defaultTimeRange;

  return (
    <>
      {/* Fixed application header — title and subtitle are mandatory */}
      <AppHeader />

      <div className="dashboard-content">
        {/* Fixed 3-tab navigation — order and labels are mandatory */}
        <Tabs>
          <TabList aria-label="Application Observability navigation" contained>
            {DASHBOARD_CONFIG.tabs.map((tab) => (
              <Tab key={tab.id}>{tab.label}</Tab>
            ))}
          </TabList>
          <TabPanels>
            <TabPanel>
              <ServiceOverview timeRange={defaultRange} />
            </TabPanel>
            <TabPanel>
              <TraceDetails timeRange={defaultRange} />
            </TabPanel>
            <TabPanel>
              <IntelligentAnalysis timeRange={defaultRange} />
            </TabPanel>
          </TabPanels>
        </Tabs>
      </div>
    </>
  );
}
```

---

## `src/App.css` (shared layout)

```css
/* Offset content below Carbon fixed header (3rem = 48px) */
.dashboard-content { padding-top: 3rem; }

/* Tab content wrapper */
.tab-content { padding: 1.5rem 1rem; }

/* KPI row */
.kpi-row { display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem; }
.kpi-row .cds--tile { flex: 1 1 160px; min-width: 140px; }

/* Chart rows */
.chart-row  { margin-bottom: 1rem; }
.chart-column > .cds--tile { height: 100%; }

/* Tab sections */
.tab-section { margin-bottom: 2rem; }
.section-title {
  font-size: 1rem; font-weight: 600; color: #161616;
  margin: 0 0 1rem; padding-bottom: 0.5rem;
  border-bottom: 1px solid #e0e0e0;
}

/* Filter bar */
.filter-bar { margin-bottom: 1rem; row-gap: 1rem; }
.filter-bar__toggle { display: flex; align-items: flex-end; padding-bottom: 0.25rem; }

/* Health summary */
.health-summary { padding: 1.25rem; }
.health-summary__status { margin-bottom: 0.75rem; }
.health-badge {
  display: inline-block; padding: 4px 12px;
  border-radius: 12px; font-size: 0.875rem; font-weight: 700;
}
.health-badge--healthy  { background: rgba(25,128,56,0.12);  color: #198038; }
.health-badge--degraded { background: rgba(241,194,27,0.15); color: #c77a00; }
.health-badge--critical { background: rgba(218,30,40,0.12);  color: #da1e28; }
.health-summary--healthy  { border-top: 3px solid #198038; }
.health-summary--degraded { border-top: 3px solid #f1c21b; }
.health-summary--critical { border-top: 3px solid #da1e28; }
.health-summary__narrative { font-size: 0.9375rem; color: #161616; margin: 0 0 1rem; line-height: 1.6; }
.health-summary__metrics { display: flex; flex-wrap: wrap; gap: 1.5rem; }
.health-metric { display: flex; flex-direction: column; }
.health-metric__label { font-size: 0.6875rem; color: #6f6f6f; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.health-metric__value { font-size: 0.875rem; font-weight: 500; color: #161616; margin-top: 2px; }

/* No issues message */
.no-issues { color: #6f6f6f; font-size: 0.875rem; font-style: italic; margin: 0; }
```

---

## `src/services/instanaApi.js` — Verified Correct Patterns

> ⚠️ **Verified against live Instana API (`unit0-techzone.150-240-162-27.nip.io`).** The patterns below fix five classes of silent failures that cause charts and trace columns to show no data.

### Bug class 1 — Wrong latency metric name (HTTP 400)

**Root cause:** Using `"latency.mean"` or `"latency.p95"` as the `metric` field value returns HTTP 400 `"Missing metrics"`. This applies to **every** metrics endpoint: `metrics/applications`, `metrics/services`, `metrics/endpoints`.

```js
// ❌ Wrong — HTTP 400
{ metric: 'latency.mean', aggregation: 'MEAN' }
{ metric: 'latency.p95',  aggregation: 'P95'  }

// ✅ Correct — metric is always "latency"; aggregation carries the statistic
{ metric: 'latency', aggregation: 'MEAN' }   // response key → latency.mean
{ metric: 'latency', aggregation: 'P95'  }   // response key → latency.p95
```

### Bug class 2 — Wrong response key for latency (returns undefined)

```js
// ❌ Wrong — these keys never exist
item.metrics?.['latency.mean.mean']
item.metrics?.['latency.p95.p95']

// ✅ Correct
item.metrics?.['latency.mean']
item.metrics?.['latency.p95']
```

### Bug class 3 — Wrong name field on service/endpoint objects (returns undefined)

```js
// ❌ Wrong — .name does not exist on service or endpoint objects
item.service?.name
item.endpoint?.name

// ✅ Correct — use .label
item.service?.label
item.endpoint?.label
```

### Bug class 4 — Mixing calls + latency in one request silently drops latency

Sending `calls` and `latency` metrics in one request to `metrics/services` or `metrics/endpoints` causes only `calls.sum` to appear in the response. Latency keys are silently absent — no error is returned.

```js
// ❌ Wrong — one request; latency keys missing in response
api.post('/api/application-monitoring/metrics/services', {
  ...commonBody,
  metrics: [
    { metric: 'calls',   aggregation: 'SUM'  },
    { metric: 'latency', aggregation: 'MEAN' },   // silently dropped
    { metric: 'latency', aggregation: 'P95'  },   // silently dropped
  ],
});

// ✅ Correct — two parallel requests
const [callsRes, latencyRes] = await Promise.all([
  api.post('/api/application-monitoring/metrics/services', {
    ...commonBody,
    metrics: [{ metric: 'calls', aggregation: 'SUM' }],
  }, { signal }),
  api.post('/api/application-monitoring/metrics/services', {
    ...commonBody,
    metrics: [
      { metric: 'latency', aggregation: 'MEAN' },
      { metric: 'latency', aggregation: 'P95'  },
    ],
  }, { signal }),
]);
```

### Bug class 5 — Traces response not unwrapped (all fields undefined)

Each item in `POST /api/application-monitoring/analyze/traces` is `{ trace: {...}, cursor: {...} }`. The trace data is **nested one level deep under `.trace`**. Accessing `item.traceId`, `item.serviceName`, or `item.endpoint` directly on the wrapper returns `undefined`.

```js
// ❌ Wrong — reading from wrapper object; all fields undefined
const traces = items.map((t) => ({
  traceId:     t.traceId,       // undefined
  serviceName: t.serviceName,   // undefined
  endpoint:    t.endpoint,      // null (wrong level)
  duration:    t.duration,      // undefined
}));

// ✅ Correct — unwrap .trace first
const traces = items.map((item) => {
  const t = item.trace ?? item;                           // unwrap
  const serviceName  = t.service?.label ?? '—';          // .label not .name
  const endpointName = t.endpoint?.label ?? t.label ?? '—'; // fall back to operation label
  return {
    traceId:      t.id        ?? t.traceId,              // field is 'id'
    timestamp:    t.startTime ?? Date.now(),
    service:      serviceName,
    serviceName,
    endpoint:     endpointName,
    duration:     t.duration  ?? 0,
    erroneous:    t.erroneous ?? false,
    errorMessage: t.errorMessage ?? null,
  };
});
```

### Complete corrected `instanaApi.js` — `fetchServiceMetrics` and `fetchEndpointMetrics`

```js
export async function fetchServiceMetrics(applicationId, timeRangeMinutes, signal) {
  const windowSize = timeRangeMinutes * 60 * 1000;
  const to         = Date.now();
  const commonBody = { applicationId, timeFrame: { windowSize, to }, pagination: { page: 1, pageSize: 25 } };

  const [callsRes, latencyRes] = await Promise.all([
    api.post('/api/application-monitoring/metrics/services',
      { ...commonBody, metrics: [{ metric: 'calls', aggregation: 'SUM' }] }, { signal }),
    api.post('/api/application-monitoring/metrics/services',
      { ...commonBody, metrics: [{ metric: 'latency', aggregation: 'MEAN' }, { metric: 'latency', aggregation: 'P95' }] }, { signal }),
  ]);

  const callsData = (callsRes.data?.items ?? []).map((item) => ({
    service: item.service?.label ?? 'Unknown',                         // ✅ .label
    calls:   sumMetric(item.metrics?.['calls.sum']) ?? 0,
  })).filter((d) => d.calls > 0);

  const latencyData = (latencyRes.data?.items ?? []).map((item) => ({
    service:     item.service?.label ?? 'Unknown',                     // ✅ .label
    meanLatency: Math.round(avgMetric(item.metrics?.['latency.mean']) ?? 0), // ✅ latency.mean
    p95Latency:  Math.round(avgMetric(item.metrics?.['latency.p95'])  ?? 0), // ✅ latency.p95
  })).filter((d) => d.meanLatency > 0 || d.p95Latency > 0);

  return { callsData, latencyData };
}

export async function fetchEndpointMetrics(applicationId, timeRangeMinutes, signal) {
  const windowSize = timeRangeMinutes * 60 * 1000;
  const to         = Date.now();
  const commonBody = { applicationId, timeFrame: { windowSize, to }, pagination: { page: 1, pageSize: 25 } };

  const [callsRes, latencyRes] = await Promise.all([
    api.post('/api/application-monitoring/metrics/endpoints',
      { ...commonBody, metrics: [{ metric: 'calls', aggregation: 'SUM' }] }, { signal }),
    api.post('/api/application-monitoring/metrics/endpoints',
      { ...commonBody, metrics: [{ metric: 'latency', aggregation: 'MEAN' }, { metric: 'latency', aggregation: 'P95' }] }, { signal }),
  ]);

  const callsData = (callsRes.data?.items ?? []).map((item) => ({
    endpoint: item.endpoint?.label ?? 'Unknown',                       // ✅ .label
    calls:    sumMetric(item.metrics?.['calls.sum']) ?? 0,
  })).filter((d) => d.calls > 0);

  const latencyData = (latencyRes.data?.items ?? []).map((item) => ({
    endpoint:    item.endpoint?.label ?? 'Unknown',                    // ✅ .label
    meanLatency: Math.round(avgMetric(item.metrics?.['latency.mean']) ?? 0),
    p95Latency:  Math.round(avgMetric(item.metrics?.['latency.p95'])  ?? 0),
  })).filter((d) => d.meanLatency > 0 || d.p95Latency > 0);

  return { callsData, latencyData };
}
```

---

### Bug class 6 — `fetchTraceDetail` wrong URL path (HTTP 404)

**Root cause:** The path `/api/application-monitoring/analyze/traces/{id}` returns HTTP **404**. The correct path adds `/v2/` before `analyze`.

```js
// ❌ Wrong — HTTP 404
api.get(`/api/application-monitoring/analyze/traces/${traceId}`)

// ✅ Correct
api.get(`/api/application-monitoring/v2/analyze/traces/${traceId}`)
```

### Bug class 7 — `fetchTraceDetail` wrong span field names (all undefined)

The `/v2/` endpoint returns `{ items: [...spans] }` with no top-level trace object. Span fields differ from what the original code expected:

| ❌ Wrong field | ✅ Correct field | Notes |
|---------------|----------------|-------|
| `s.spanId` | `s.id` | |
| `s.parentSpanId` | `s.parentId` | `null` on the root span |
| `s.serviceName` / `s.service?.name` | `s.destination?.service?.label` | |
| `s.erroneous` | `(s.errorCount ?? 0) > 0` | `errorCount` is an integer, not a boolean |
| `s.errorMessage` | `s.errorCount + ' error(s)'` if `errorCount > 0` | |
| `s.startTime` | `s.timestamp` | |
| *(top-level `data.traceId`)* | Passed-in `traceId` parameter | No top-level trace object exists |
| *(top-level `data.startTime`)* | `rootSpan.timestamp` | Derive from root span (`parentId === null`) |
| *(top-level `data.duration`)* | `rootSpan.duration` | Derive from root span |

### Complete corrected `fetchTraceDetail`

```js
export async function fetchTraceDetail(traceId, signal) {
  // ✅ /v2/ prefix is required — /analyze/traces/{id} without v2 returns 404
  const response = await safeRequest(() =>
    api.get(`/api/application-monitoring/v2/analyze/traces/${traceId}`, { signal })
  );

  // v2 returns { items: [...spans] } — no top-level trace object
  const rawSpans = response.data?.items ?? [];

  const spans = rawSpans.map((s) => {
    const erroneous = (s.errorCount ?? 0) > 0;
    return {
      spanId:       s.id                              ?? '',    // ✅ s.id not s.spanId
      parentSpanId: s.parentId                        ?? null,  // ✅ s.parentId not s.parentSpanId
      name:         s.name                            ?? '—',
      serviceName:  s.destination?.service?.label     ?? '—',  // ✅ destination.service.label
      duration:     s.duration                        ?? 0,
      erroneous,
      errorMessage: erroneous ? `${s.errorCount} error(s)` : null,
      startTime:    s.timestamp                       ?? null,  // ✅ s.timestamp not s.startTime
    };
  });

  // Derive trace metadata from the root span (parentId === null)
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
