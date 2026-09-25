# Mandatory Carbon Design System Component Patterns

All Application Observability dashboards must use IBM Carbon Design System (`@carbon/react`) exclusively for UI components. This document defines the required patterns. Use these exactly — do not improvise alternatives.

## Installation

```bash
npm install @carbon/react @carbon/icons-react
```

Add to `src/index.jsx` (must be the first import):
```jsx
import '@carbon/styles/css/styles.css';
```

---

## Application Header

```jsx
// src/components/AppHeader.jsx
import { Header, HeaderName } from '@carbon/react';
import { DASHBOARD_CONFIG } from '../config/dashboardConfig';

export default function AppHeader() {
  return (
    <Header aria-label={DASHBOARD_CONFIG.appTitle}>
      <HeaderName prefix="">
        {DASHBOARD_CONFIG.appTitle}
        <span className="app-subtitle">{DASHBOARD_CONFIG.appSubtitle}</span>
      </HeaderName>
    </Header>
  );
}
```

CSS (add to `src/App.css`):
```css
.app-subtitle {
  display: block;
  font-size: 0.75rem;
  font-weight: 400;
  color: #c6c6c6;
  margin-top: 2px;
}
/* Offset content below the fixed header */
.dashboard-content {
  padding-top: 3rem;
}
```

**The title and subtitle values must come from `dashboardConfig.js` — not be hard-coded in the component.**

---

## Tab Navigation (3 Fixed Tabs)

```jsx
// src/App.jsx (navigation section)
import { Tabs, TabList, Tab, TabPanels, TabPanel } from '@carbon/react';
import { DASHBOARD_CONFIG } from './config/dashboardConfig';
import ServiceOverview from './tabs/ServiceOverview';
import TraceDetails from './tabs/TraceDetails';
import IntelligentAnalysis from './tabs/IntelligentAnalysis';

// Inside App component render:
<Tabs>
  <TabList aria-label="Application Observability tabs" contained>
    {DASHBOARD_CONFIG.tabs.map((tab) => (
      <Tab key={tab.id}>{tab.label}</Tab>
    ))}
  </TabList>
  <TabPanels>
    <TabPanel><ServiceOverview /></TabPanel>
    <TabPanel><TraceDetails /></TabPanel>
    <TabPanel><IntelligentAnalysis /></TabPanel>
  </TabPanels>
</Tabs>
```

**Tab count (3) and tab labels are read from `dashboardConfig.js`. Never hard-code them in the component.**

---

## Grid Layout (2-Column Charts)

```jsx
// Chart grid for Service Overview rows
import { Grid, Column } from '@carbon/react';

// 2-column chart row (50/50 split on lg, 100% on sm)
<Grid fullWidth>
  <Column sm={4} md={4} lg={8}>
    <ChartCard title="..." chart={<CallsChart data={data} />} />
  </Column>
  <Column sm={4} md={4} lg={8}>
    <ChartCard title="..." chart={<LatencyChart data={data} />} />
  </Column>
</Grid>
```

Use Carbon 16-column grid:
- `sm={4}` — full width on small screens (4/4)
- `md={4}` — full width on medium screens (4/8)
- `lg={8}` — half width on large screens (8/16)

---

## KPI Card

```jsx
// src/components/KPICard.jsx
import { Tile } from '@carbon/react';

const STATUS_CLASSES = {
  healthy:  'kpi-card--healthy',
  degraded: 'kpi-card--degraded',
  error:    'kpi-card--error',
  unknown:  'kpi-card--unknown',
};

export default function KPICard({ label, value, unit = '', status = 'unknown', trend = null }) {
  const statusClass = STATUS_CLASSES[status] ?? STATUS_CLASSES.unknown;

  return (
    <Tile className={`kpi-card ${statusClass}`}>
      <p className="kpi-card__label">{label}</p>
      <p className="kpi-card__value">
        {value !== null && value !== undefined ? (
          <>{value}<span className="kpi-card__unit">{unit}</span></>
        ) : (
          <span className="kpi-card__empty">—</span>
        )}
      </p>
      {trend !== null && (
        <p className={`kpi-card__trend kpi-card__trend--${trend > 0 ? 'up' : trend < 0 ? 'down' : 'flat'}`}>
          {trend > 0 ? '↑' : trend < 0 ? '↓' : '→'} {Math.abs(trend).toFixed(1)}%
        </p>
      )}
    </Tile>
  );
}
```

CSS:
```css
.kpi-card { min-width: 150px; flex: 1; }
.kpi-card__label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #6f6f6f;
  margin: 0 0 8px;
}
.kpi-card__value {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  line-height: 1.1;
}
.kpi-card__unit { font-size: 0.9rem; font-weight: 400; margin-left: 2px; }
.kpi-card__empty { color: #a8a8a8; }
.kpi-card__trend { font-size: 0.75rem; margin: 4px 0 0; }
.kpi-card__trend--up   { color: #da1e28; }  /* up = worse for error rate / latency */
.kpi-card__trend--down { color: #198038; }  /* down = better */
.kpi-card__trend--flat { color: #6f6f6f; }

.kpi-card--healthy  { border-top: 3px solid #198038; }
.kpi-card--degraded { border-top: 3px solid #f1c21b; }
.kpi-card--error    { border-top: 3px solid #da1e28; }
.kpi-card--unknown  { border-top: 3px solid #c6c6c6; }
.kpi-card__value .kpi-card--healthy  { color: #198038; }
.kpi-card__value .kpi-card--degraded { color: #f1c21b; }
.kpi-card__value .kpi-card--error    { color: #da1e28; }
```

---

## Chart Card (Plotly Wrapper)

```jsx
// src/components/ChartCard.jsx
import { Tile } from '@carbon/react';
import LoadingState from './LoadingState';
import ErrorState from './ErrorState';
import EmptyState from './EmptyState';

export default function ChartCard({ title, chart, isLoading = false, isError = false, isEmpty = false, errorMessage = '' }) {
  return (
    <Tile className="chart-card">
      <p className="chart-card__title">{title}</p>
      <div className="chart-card__body">
        {isLoading && <LoadingState />}
        {!isLoading && isError && <ErrorState message={errorMessage || 'Failed to load chart data.'} />}
        {!isLoading && !isError && isEmpty && <EmptyState />}
        {!isLoading && !isError && !isEmpty && chart}
      </div>
    </Tile>
  );
}
```

CSS:
```css
.chart-card { padding: 1rem; height: 100%; }
.chart-card__title {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #6f6f6f;
  margin: 0 0 0.75rem;
}
.chart-card__body { min-height: 220px; display: flex; align-items: stretch; }
.chart-card__body > * { flex: 1; }
```

---

## Loading State

```jsx
// src/components/LoadingState.jsx
import { InlineLoading } from '@carbon/react';

export default function LoadingState({ description = 'Loading data…' }) {
  return (
    <div className="state-container">
      <InlineLoading description={description} status="active" />
    </div>
  );
}
```

---

## Error State

```jsx
// src/components/ErrorState.jsx
import { InlineNotification } from '@carbon/react';

export default function ErrorState({ message = 'Failed to load data. Please try again.' }) {
  return (
    <div className="state-container">
      <InlineNotification
        kind="error"
        title="Data unavailable"
        subtitle={message}
        hideCloseButton
        lowContrast
      />
    </div>
  );
}
```

---

## Empty State

```jsx
// src/components/EmptyState.jsx
import { InlineNotification } from '@carbon/react';

export default function EmptyState({ message = 'No data available for the selected time range.' }) {
  return (
    <div className="state-container">
      <InlineNotification kind="info" title="No data" subtitle={message} hideCloseButton lowContrast />
    </div>
  );
}
```

CSS:
```css
/* Centers Carbon InlineNotification / InlineLoading inside chart cards */
.state-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 120px;
  padding: 1rem;
  width: 100%;
}
```

---

## Trace Table

```jsx
// src/components/TraceTable.jsx — see component-templates.md for full implementation
// Uses Carbon DataTable, Link (trace ID column), Tag (status column)
import {
  DataTable, Table, TableHead, TableRow, TableHeader,
  TableBody, TableCell, TableContainer,
  Link, Tag,
} from '@carbon/react';
```

- Trace ID column: Carbon `Link` with monospace class `.trace-id-link`
- Status column: Carbon `Tag` — `type="red"` for Error, `type="green"` for OK

Column headers are read from `dashboardConfig.js → traceColumns`. See `component-templates.md` for the full implementation.

---

## Trace Detail View (Modal)

```jsx
// src/components/TraceDetailView.jsx — see component-templates.md for full implementation
// Uses Carbon ComposedModal, InlineNotification (error spans), Tag (status), DataTable
import { ComposedModal, ModalHeader, ModalBody } from '@carbon/react';
```

See `component-templates.md` for the full implementation.

---

## Filter Bar (Trace Details Tab)

```jsx
// Inside TraceDetails.jsx
import { Dropdown, NumberInput, Toggle, Grid, Column } from '@carbon/react';

<Grid fullWidth className="filter-bar">
  <Column sm={4} md={2} lg={3}>
    <Dropdown
      id="filter-time-range"
      titleText="Time Range"
      label="Select range"
      items={DASHBOARD_CONFIG.timeRangeOptions}
      itemToString={(item) => item?.label ?? ''}
      selectedItem={selectedTimeRange}
      onChange={({ selectedItem }) => setSelectedTimeRange(selectedItem)}
    />
  </Column>
  <Column sm={4} md={2} lg={3}>
    <Dropdown
      id="filter-service"
      titleText="Service"
      label="All services"
      items={services}
      itemToString={(item) => item?.name ?? 'All services'}
      selectedItem={selectedService}
      onChange={({ selectedItem }) => setSelectedService(selectedItem)}
    />
  </Column>
  <Column sm={4} md={2} lg={3}>
    <Dropdown
      id="filter-endpoint"
      titleText="Endpoint"
      label="All endpoints"
      items={endpoints}
      itemToString={(item) => item?.name ?? 'All endpoints'}
      selectedItem={selectedEndpoint}
      onChange={({ selectedItem }) => setSelectedEndpoint(selectedItem)}
    />
  </Column>
  <Column sm={2} md={1} lg={2}>
    <NumberInput
      id="filter-min-latency"
      label="Min Latency (ms)"
      min={0}
      step={100}
      value={minLatency}
      onChange={(e, { value }) => setMinLatency(value)}
    />
  </Column>
  <Column sm={2} md={1} lg={2}>
    <Toggle
      id="filter-errors-only"
      labelText="Error Status"
      labelA="All"
      labelB="Errors Only"
      toggled={errorsOnly}
      onToggle={setErrorsOnly}
    />
  </Column>
</Grid>
```

---

## Insight Panel

```jsx
// src/components/InsightPanel.jsx
import { Tile } from '@carbon/react';
import { Warning, Information, CircleDash } from '@carbon/icons-react';

const SEVERITY_ICONS = {
  warning:  <Warning size={20} className="insight-icon insight-icon--warning" />,
  info:     <Information size={20} className="insight-icon insight-icon--info" />,
  none:     <CircleDash size={20} className="insight-icon insight-icon--none" />,
};

export default function InsightPanel({ finding, evidence, impact, action, severity = 'info' }) {
  return (
    <Tile className="insight-panel">
      <div className="insight-panel__header">
        {SEVERITY_ICONS[severity]}
        <p className="insight-panel__finding">{finding}</p>
      </div>
      {evidence && (
        <div className="insight-panel__row">
          <span className="insight-panel__field-label">Evidence:</span>
          <span className="insight-panel__field-value">{evidence}</span>
        </div>
      )}
      {impact && (
        <div className="insight-panel__row">
          <span className="insight-panel__field-label">Potential Impact:</span>
          <span className="insight-panel__field-value">{impact}</span>
        </div>
      )}
      {action && (
        <div className="insight-panel__row insight-panel__row--action">
          <span className="insight-panel__field-label">Recommended Action:</span>
          <span className="insight-panel__field-value">{action}</span>
        </div>
      )}
    </Tile>
  );
}
```

CSS:
```css
.insight-panel { margin-bottom: 0.5rem; }
.insight-panel__header { display: flex; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.75rem; }
.insight-panel__finding { font-weight: 600; font-size: 0.9rem; margin: 0; flex: 1; }
.insight-icon--warning { color: #f1c21b; }
.insight-icon--info    { color: #0043ce; }
.insight-icon--none    { color: #c6c6c6; }
.insight-panel__row { display: flex; gap: 0.5rem; margin-bottom: 0.4rem; font-size: 0.8rem; }
.insight-panel__field-label { font-weight: 600; color: #6f6f6f; white-space: nowrap; min-width: 130px; }
.insight-panel__field-value { color: #161616; flex: 1; }
.insight-panel__row--action .insight-panel__field-value { font-weight: 500; color: #0043ce; }
```

---

## IntelligentAnalysis — "No Issues" State

When an analysis section has no findings, use `InlineNotification kind="info"` rather than a plain `<p>` tag:

```jsx
import { InlineNotification } from '@carbon/react';

{items.length === 0 ? (
  <InlineNotification
    kind="info"
    title="All clear"
    subtitle="No issues detected in the current time window."
    hideCloseButton
    lowContrast
  />
) : (
  items.map((item, i) => <InsightPanel key={i} {...item} />)
)}
```

Section titles in `IntelligentAnalysis.jsx` use `<p className="section-title">` (styled via App.css)
so that the heading level stays correct in the Carbon page structure.

---

## KPI Row Layout

```jsx
// KPI row — used in Service Overview and Trace Details
<div className="kpi-row">
  {kpiItems.map((kpi) => (
    <KPICard key={kpi.id} {...kpi} />
  ))}
</div>
```

CSS:
```css
.kpi-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1rem 0;
}
.kpi-row .cds--tile {
  flex: 1 1 160px;
  min-width: 140px;
}
```

---

## Known API Gotchas (Instana call-groups endpoint)

### 3. `aggregation: 'MEAN'` does not exist — use `'P50'`

The `/api/application-monitoring/analyze/call-groups` endpoint accepts only these aggregations for `latency`:

| Valid | Invalid (returns 500) |
|-------|-----------------------|
| `"P50"` | `"MEAN"` ❌ |
| `"P95"` | `"MEAN"` ❌ |
| `"P99"` | |

**Wrong:**
```js
{ metric: 'latency', aggregation: 'MEAN' }  // ❌ → HTTP 500
```

**Correct:**
```js
{ metric: 'latency', aggregation: 'P50' }   // ✅ P50 = median ≈ mean
{ metric: 'latency', aggregation: 'P95' }   // ✅
```

The response key is `latency.p50` (not `latency.mean`). Read it as:
```js
latestMetric(item.metrics, 'latency.p50')   // ✅
latestMetric(item.metrics, 'latency.mean')  // ❌ always undefined
```

### 4. Traces pagination uses `retrievalSize` / `offset` — not `page` / `pageSize`

```js
// Wrong — causes 400 or silent empty results:
pagination: { page: 1, pageSize: 100 }       // ❌

// Correct:
pagination: { retrievalSize: 100, offset: 0 } // ✅
```

### 5. Traces response is nested under `item.trace.*`

Each item returned by `POST /api/application-monitoring/analyze/traces` wraps the trace under a `trace` key:

```json
{ "trace": { "id": "...", "label": "...", "startTime": 0, "duration": 0,
             "erroneous": false, "service": { "label": "..." }, "endpoint": null },
  "cursor": { ... } }
```

**Wrong — fields do not exist at the item level:**
```js
item.traceId   // ❌ undefined
item.id        // ❌ undefined
item.timestamp // ❌ undefined
```

**Correct mapper:**
```js
const t = item.trace ?? item; // guard for future API changes
return {
  traceId:   t.id,
  timestamp: t.startTime,
  service:   t.service?.label  || '—',
  endpoint:  t.endpoint?.label || t.label || '—',
  duration:  t.duration,
  erroneous: t.erroneous,
};
```

### 6. Time-series charts empty despite API returning data — bucket pre-seeding required

When merging per-service time-series data into a single `bucketMap`, Instana returns `null` (not `0`) for empty metric buckets. If you seed the `bucketMap` only from `calls.sum` data points, then guard all other metrics with `if (bucketMap[ts])`, latency and error values at timestamps where calls happened to be `null` are silently skipped.

This causes `callsTimeSeries`, `latencyTimeSeries`, and `errorRateTimeSeries` to appear empty or incomplete in the charts even though the API returned data.

**Fix:** pre-seed all timestamps from **all four** metric arrays before accumulating any values. See `instana-api-client/api-patterns.md` → **Time-Series Bucket Merge Pattern** for the complete correct implementation.

### 8. `rollupWindow` must use a fixed ladder — dynamic division returns `Array(1)`

Instana enforces server-side minimum granularity constraints. Computing `rollupWindow = Math.round(windowMs / 30)` produces a value the server silently rounds **up** to the full `windowSize`, collapsing all time-series data into a single bucket (`Array(1)` per metric). A single-point line chart renders as invisible in Plotly.

**Wrong:**
```js
rollupWindow: Math.max(Math.round(windowMs / 30), 60_000)  // ❌ → Array(1) for short windows
```

**Correct — use a fixed ladder keyed on window duration in minutes:**
```js
function buildRollupWindow(windowMinutes) {
  if (windowMinutes <= 30)   return  1 * 60 * 1000;   //  1 min → up to 30 pts
  if (windowMinutes <= 180)  return  5 * 60 * 1000;   //  5 min → up to 36 pts
  if (windowMinutes <= 720)  return 15 * 60 * 1000;   // 15 min → up to 48 pts
  if (windowMinutes <= 1440) return 30 * 60 * 1000;   // 30 min → up to 48 pts
  return                     60 * 60 * 1000;           // 60 min
}
```

### 9. Use `mode: 'lines+markers'` for Plotly line charts — not `mode: 'lines'`

When only 1–2 data points are returned (e.g. short time windows), `mode: 'lines'` renders nothing visible because there is no line segment to draw. `mode: 'lines+markers'` always renders a visible dot at every data point, making single-point series visible.

**Wrong:**
```js
mode: 'lines'         // ❌ invisible when only 1 data point
```

**Correct:**
```js
mode: 'lines+markers' // ✅ always visible — dot shown even for a single point
```

Apply to all three time-series line charts: `CallsChart`, `LatencyChart`, `ErrorRateChart`.

---

## Known Gotchas (CRA / Babel)

### 1. `??` mixed with `||` — must use explicit parentheses

Babel (used by CRA / react-scripts) requires explicit parentheses when mixing the nullish coalescing operator `??` with logical operators `||` or `&&`. Failing to parenthesise causes a **compile error**:

```
SyntaxError: Nullish coalescing operator(??) requires parens
when mixing with logical operators.
```

**Wrong:**
```js
const x = a ?? b || null;          // ❌ SyntaxError
const x = (a?.length) ?? b || null; // ❌ SyntaxError
```

**Correct — wrap the entire `??` expression in parens:**
```js
const x = (a ?? b) || null;         // ✅
const x = (a?.length ?? b) || null; // ✅
```

Rule: whenever `??` and `||` (or `&&`) appear in the same expression, the `??` sub-expression must be enclosed in its own set of parentheses.

---

### 2. `role="treeitem"` requires `aria-selected`

The ARIA spec requires that every element with `role="treeitem"` has an explicit `aria-selected` attribute. Omitting it triggers an `jsx-a11y/role-has-required-aria-props` ESLint error (warning in CRA, error in strict configs).

**Wrong:**
```jsx
<li role="treeitem">…</li>  // ❌ ESLint warning
```

**Correct:**
```jsx
<li role="treeitem" aria-selected={false}>…</li>  // ✅
```

Use `aria-selected={false}` as the default (unselected) state. Update it to `true` if you implement keyboard-navigable tree selection.

### 7. Do not render charts that have no data — omit them from the DOM entirely

When a chart's data array is empty after a successful fetch, **do not render** the chart card or its `Column` wrapper. Rendering an empty `Tile` with placeholder text wastes space and degrades the user experience.

**Wrong — always renders all 8 chart tiles regardless of data:**
```jsx
// ❌ Renders an "EmptyState" tile for charts with no data
const isEmpty = !loading && !error && data.length === 0;
return (
  <Column ...>
    <ChartCard isEmpty={isEmpty} ... />
  </Column>
);
```

**Correct — filter out empty charts at the row level, skip the row entirely if all charts are empty:**
```jsx
// ✅ Only render charts that have data
const visibleCharts = rowCharts.filter((chartDef) => {
  if (loading || error) return true;           // show skeleton during load/error
  return (chartData[chartDef.dataKey] ?? []).length > 0;
});

if (!loading && !error && visibleCharts.length === 0) return null; // skip empty row

return (
  <Grid fullWidth key={row} className="chart-row">
    {(loading || error ? rowCharts : visibleCharts).map((chartDef) => {
      const data = chartData[chartDef.dataKey] ?? [];
      return (
        <Column sm={4} md={4} lg={8} key={chartDef.id} className="chart-column">
          <ChartCard
            title={chartDef.title}
            isLoading={loading}
            isError={!!error}
            errorMessage={error}
            chart={<ChartComp data={data} />}
          />
        </Column>
      );
    })}
  </Grid>
);
```

**`ChartCard` has no `isEmpty` prop.** The component only handles `isLoading` and `isError`. Empty-data filtering is the caller's responsibility (the tab component), not `ChartCard`'s.

**During loading and errors**, all chart positions are rendered normally (with `LoadingState` / `ErrorState` inside) so the layout does not jump.
