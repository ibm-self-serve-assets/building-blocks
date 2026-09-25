# Mandatory Reusable Component Implementations

These are the canonical implementations of all shared components. Every generated dashboard must use these exact implementations. Do not redesign, simplify, or merge them.

---

## `src/components/KPICard.jsx`

```jsx
import { Tile } from '@carbon/react';

const STATUS_BORDER_COLORS = {
  healthy:  '#198038',
  degraded: '#f1c21b',
  error:    '#da1e28',
  unknown:  '#c6c6c6',
};

const STATUS_VALUE_COLORS = {
  healthy:  '#198038',
  degraded: '#c77a00',
  error:    '#da1e28',
  unknown:  '#161616',
};

/**
 * @param {object} props
 * @param {string}           props.label      - KPI label (from dashboardConfig.kpis[].label)
 * @param {number|null}      props.value      - Numeric value; null = no data
 * @param {string}           [props.unit]     - Unit suffix ('ms', '%', etc.)
 * @param {'healthy'|'degraded'|'error'|'unknown'} [props.status]
 * @param {number|null}      [props.trend]    - % change vs previous window; null = hide
 */
export default function KPICard({ label, value, unit = '', status = 'unknown', trend = null }) {
  const borderColor = STATUS_BORDER_COLORS[status] ?? STATUS_BORDER_COLORS.unknown;
  const valueColor  = STATUS_VALUE_COLORS[status]  ?? STATUS_VALUE_COLORS.unknown;

  const formattedValue = (() => {
    if (value === null || value === undefined) return null;
    if (unit === '%') return value.toFixed(2);
    if (Number.isInteger(value)) return value.toLocaleString();
    return value.toLocaleString(undefined, { maximumFractionDigits: 0 });
  })();

  return (
    <Tile className="kpi-card" style={{ borderTop: `3px solid ${borderColor}` }}>
      <p className="kpi-card__label">{label}</p>
      <p className="kpi-card__value" style={{ color: valueColor }}>
        {formattedValue !== null ? (
          <>
            {formattedValue}
            {unit && <span className="kpi-card__unit">{unit}</span>}
          </>
        ) : (
          <span className="kpi-card__empty" title="No data available">—</span>
        )}
      </p>
      {trend !== null && (
        <p className={`kpi-card__trend kpi-card__trend--${trend > 0 ? 'up' : trend < 0 ? 'down' : 'flat'}`}>
          {trend > 0 ? '▲' : trend < 0 ? '▼' : '→'}&nbsp;{Math.abs(trend).toFixed(1)}%
        </p>
      )}
    </Tile>
  );
}
```

CSS (add to `src/App.css`):
```css
.kpi-card { min-width: 140px; flex: 1; padding: 1rem 1.25rem; }
.kpi-card__label {
  font-size: 0.6875rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.05em;
  color: #6f6f6f; margin: 0 0 0.5rem;
}
.kpi-card__value { font-size: 1.875rem; font-weight: 700; margin: 0; line-height: 1.1; }
.kpi-card__unit  { font-size: 0.875rem; font-weight: 400; margin-left: 2px; }
.kpi-card__empty { color: #a8a8a8; }
.kpi-card__trend { font-size: 0.75rem; margin: 0.25rem 0 0; }
.kpi-card__trend--up   { color: #da1e28; }
.kpi-card__trend--down { color: #198038; }
.kpi-card__trend--flat { color: #6f6f6f; }
```

---

## `src/components/ChartCard.jsx`

```jsx
import { Tile } from '@carbon/react';
import LoadingState from './LoadingState';
import ErrorState   from './ErrorState';

/**
 * Wraps a Plotly chart in a Carbon Tile with title, loading, and error states.
 * Charts with no data are NOT rendered — callers must filter them out before
 * passing to ChartCard (see ServiceOverview chart-row logic).
 *
 * @param {object}       props
 * @param {string}       props.title        - Chart title (from dashboardConfig.charts[].title)
 * @param {React.Node}   props.chart        - Plotly chart component instance
 * @param {boolean}      [props.isLoading]
 * @param {boolean}      [props.isError]
 * @param {string}       [props.errorMessage]
 */
export default function ChartCard({ title, chart, isLoading = false, isError = false, errorMessage = '' }) {
  const renderBody = () => {
    if (isLoading) return <LoadingState />;
    if (isError)   return <ErrorState message={errorMessage || 'Failed to load chart data.'} />;
    return chart;
  };

  return (
    <Tile className="chart-card">
      <p className="chart-card__title">{title}</p>
      <div className="chart-card__body">{renderBody()}</div>
    </Tile>
  );
}
```

CSS:
```css
.chart-card { padding: 1rem; height: 100%; }
.chart-card__title {
  font-size: 0.6875rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.05em;
  color: #6f6f6f; margin: 0 0 0.75rem;
}
.chart-card__body { min-height: 220px; display: flex; align-items: stretch; }
.chart-card__body > * { flex: 1; min-width: 0; }
```

---

## `src/components/LoadingState.jsx`

```jsx
import { InlineLoading } from '@carbon/react';

/**
 * @param {{ description?: string }} props
 */
export default function LoadingState({ description = 'Loading data…' }) {
  return (
    <div className="state-container">
      <InlineLoading description={description} status="active" />
    </div>
  );
}
```

---

## `src/components/ErrorState.jsx`

```jsx
import { InlineNotification } from '@carbon/react';

/**
 * @param {{ message?: string }} props
 */
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

## `src/components/EmptyState.jsx`

```jsx
import { InlineNotification } from '@carbon/react';

/**
 * @param {{ message?: string }} props
 */
export default function EmptyState({ message = 'No data available for the selected time range.' }) {
  return (
    <div className="state-container">
      <InlineNotification kind="info" title="No data" subtitle={message} hideCloseButton lowContrast />
    </div>
  );
}
```

CSS (shared):
```css
/* Centers Carbon InlineNotification / InlineLoading inside chart cards */
.state-container {
  display: flex; align-items: center; justify-content: center;
  min-height: 120px; padding: 1rem; width: 100%;
}
```

---

## `src/components/TraceTable.jsx`

```jsx
import { useState } from 'react';
import {
  DataTable, Table, TableHead, TableRow, TableHeader,
  TableBody, TableCell, TableContainer, TableToolbar,
  TableToolbarContent, TableToolbarSearch,
  Link, Tag,
} from '@carbon/react';
import { DASHBOARD_CONFIG } from '../config/dashboardConfig';
import EmptyState from './EmptyState';

const columns = DASHBOARD_CONFIG.traceColumns;

/**
 * @param {object} props
 * @param {Array}    props.traces          - Array of trace objects
 * @param {Function} props.onTraceSelect   - Called with trace object when row is clicked
 * @param {boolean}  [props.isLoading]
 * @param {boolean}  [props.isError]
 */
export default function TraceTable({ traces = [], onTraceSelect, isLoading = false, isError = false }) {
  const [searchText, setSearchText] = useState('');

  const filtered = traces.filter((t) => {
    if (!searchText) return true;
    const q = searchText.toLowerCase();
    return (
      (t.traceId   || '').toLowerCase().includes(q) ||
      (t.service   || '').toLowerCase().includes(q) ||
      (t.endpoint  || '').toLowerCase().includes(q)
    );
  });

  const rows = filtered.map((t) => ({
    id:        t.traceId,
    traceId:   t.traceId,
    timestamp: new Date(t.timestamp).toLocaleString(),
    service:   t.service   || t.serviceName || '—',
    endpoint:  t.endpoint  || '—',
    duration:  `${(t.duration || 0).toLocaleString()} ms`,
    status:    t.erroneous ? 'Error' : 'OK',
    error:     t.errorMessage || '—',
    _erroneous: t.erroneous,
  }));

  return (
    <DataTable rows={rows} headers={columns.map((c) => ({ key: c.id, header: c.header }))}>
      {({ rows: tableRows, headers, getHeaderProps, getRowProps, getTableProps, onInputChange }) => (
        <TableContainer>
          <TableToolbar>
            <TableToolbarContent>
              <TableToolbarSearch
                placeholder="Search by trace ID, service, or endpoint…"
                onChange={(e) => {
                  setSearchText(e.target.value);
                  onInputChange(e);
                }}
              />
            </TableToolbarContent>
          </TableToolbar>

          {tableRows.length === 0 ? (
            <EmptyState message="No traces match the current filters." />
          ) : (
            <Table {...getTableProps()} size="sm">
              <TableHead>
                <TableRow>
                  {headers.map((header) => (
                    <TableHeader {...getHeaderProps({ header })} key={header.key}>
                      {header.header}
                    </TableHeader>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {tableRows.map((row) => {
                  const original = filtered.find((t) => t.traceId === row.id);
                  return (
                    <TableRow
                      {...getRowProps({ row })}
                      key={row.id}
                      className={original?._erroneous ? 'trace-row--error' : ''}
                      onClick={() => onTraceSelect && onTraceSelect(original)}
                      style={{ cursor: onTraceSelect ? 'pointer' : 'default' }}
                    >
                      {row.cells.map((cell) => (
                       <TableCell key={cell.id}>
                         {cell.info.header === 'traceId' ? (
                           <Link
                             href="#"
                             className="trace-id-link"
                             onClick={(e) => {
                               e.preventDefault();
                               e.stopPropagation();
                               onTraceSelect && onTraceSelect(original);
                             }}
                             title={cell.value}
                           >
                             {(cell.value || '').slice(0, 8)}…
                           </Link>
                         ) : cell.info.header === 'status' ? (
                           <Tag type={cell.value === 'Error' ? 'red' : 'green'} size="sm">
                             {cell.value}
                           </Tag>
                         ) : (
                           cell.value
                         )}
                       </TableCell>
                     ))}
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </TableContainer>
      )}
    </DataTable>
  );
}
```

CSS:
```css
/* Error row background — Carbon Tag handles status colours */
.trace-row--error td { background: rgba(218,30,40,0.04); }
/* Monospace link style for trace ID — uses Carbon Link base */
.trace-id-link { font-family: 'IBM Plex Mono', 'Courier New', monospace; font-size: 0.75rem; }
```

---

## `src/components/TraceDetailView.jsx`

```jsx
import { useEffect, useState } from 'react';
import {
  ComposedModal, ModalHeader, ModalBody,
  DataTable, Table, TableHead, TableRow, TableHeader,
  TableBody, TableCell, TableContainer,
  InlineNotification, Tag,
} from '@carbon/react';
import LoadingState from './LoadingState';
import ErrorState   from './ErrorState';

/**
 * @param {object}    props
 * @param {object}    props.trace      - Full trace detail object (with .spans array)
 * @param {boolean}   props.isLoading
 * @param {boolean}   props.isError
 * @param {Function}  props.onClose
 */
export default function TraceDetailView({ trace, isLoading = false, isError = false, onClose }) {
  const [open, setOpen] = useState(true);

  useEffect(() => { setOpen(true); }, [trace]);

  const handleClose = () => {
    setOpen(false);
    onClose();
  };

  const spans    = trace?.spans ?? [];
  const services = [...new Set(spans.map((s) => s.serviceName).filter(Boolean))];
  const slowestSpans = [...spans].sort((a, b) => (b.duration || 0) - (a.duration || 0)).slice(0, 5);
  const errorSpans   = spans.filter((s) => s.erroneous);
  const roots        = buildSpanTree(spans);

  return (
    <ComposedModal open={open} onClose={handleClose} size="lg">
      <ModalHeader
        title="Trace Detail"
        subtitle={<span className="trace-detail__id">{trace?.traceId || 'Loading…'}</span>}
      />
      <ModalBody>
        {isLoading && <LoadingState description="Loading trace spans…" />}
        {!isLoading && isError && <ErrorState message="Failed to load trace detail." />}
        {!isLoading && !isError && trace && (
          <>
            {/* Metadata row */}
            <div className="trace-detail__meta">
              <MetaField label="Start Time"         value={new Date(trace.startTime || 0).toLocaleString()} />
              <MetaField label="Total Duration"     value={`${(trace.duration || 0).toLocaleString()} ms`} />
              <MetaField label="Spans"              value={(spans.length).toString()} />
              <MetaField label="Services Involved"  value={services.join(', ') || '—'} />
              <MetaField label="Error Status"       value={trace.erroneous ? 'Error' : 'OK'} isError={trace.erroneous} />
            </div>

            {/* Error spans notification */}
            {errorSpans.length > 0 && (
              <InlineNotification
                kind="error"
                title={`${errorSpans.length} erroneous span${errorSpans.length !== 1 ? 's' : ''}`}
                subtitle={errorSpans.slice(0, 5).map((s) => s.errorMessage || s.name || s.spanId).join(' · ')}
                hideCloseButton
                lowContrast
                style={{ marginBottom: '1rem' }}
              />
            )}

            {/* Span hierarchy */}
            <p className="trace-detail__section-title">Span Hierarchy</p>
            <div className="trace-detail__span-tree">
              <SpanTree roots={roots} />
            </div>

            {/* Slowest spans table */}
            {slowestSpans.length > 0 && (
              <>
                <p className="trace-detail__section-title">Slowest Spans</p>
                <DataTable
                  rows={slowestSpans.map((s) => ({
                    id:       s.spanId,
                    name:     s.name || '—',
                    service:  s.serviceName || '—',
                    duration: `${(s.duration || 0).toLocaleString()} ms`,
                    status:   s.erroneous ? 'Error' : 'OK',
                  }))}
                  headers={[
                    { key: 'name',     header: 'Span' },
                    { key: 'service',  header: 'Service' },
                    { key: 'duration', header: 'Duration' },
                    { key: 'status',   header: 'Status' },
                  ]}
                >
                  {({ rows, headers, getHeaderProps, getRowProps, getTableProps }) => (
                    <TableContainer>
                      <Table {...getTableProps()} size="sm">
                        <TableHead>
                          <TableRow>
                            {headers.map((h) => <TableHeader {...getHeaderProps({ header: h })} key={h.key}>{h.header}</TableHeader>)}
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {rows.map((row) => (
                            <TableRow {...getRowProps({ row })} key={row.id}
                              className={row.cells.find(c => c.info.header === 'status')?.value === 'Error' ? 'trace-row--error' : ''}>
                              {row.cells.map((cell) => (
                                <TableCell key={cell.id}>
                                  {cell.info.header === 'status' ? (
                                   <Tag type={cell.value === 'Error' ? 'red' : 'green'} size="sm">{cell.value}</Tag>
                                 ) : cell.value}
                                </TableCell>
                              ))}
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  )}
                </DataTable>
              </>
            )}
          </>
        )}
      </ModalBody>
    </ComposedModal>
  );
}

function MetaField({ label, value, isError = false }) {
  return (
    <div className="trace-meta-field">
      <span className="trace-meta-field__label">{label}</span>
      <span className={`trace-meta-field__value${isError ? ' trace-meta-field__value--error' : ''}`}>{value}</span>
    </div>
  );
}

/** Build nested span tree from flat array using parentSpanId linkage */
function buildSpanTree(spans) {
  const byId = {};
  spans.forEach((s) => { byId[s.spanId] = { ...s, _children: [] }; });
  const roots = [];
  Object.values(byId).forEach((span) => {
    if (span.parentSpanId && byId[span.parentSpanId]) {
      byId[span.parentSpanId]._children.push(span);
    } else {
      roots.push(span);
    }
  });
  return roots;
}

function SpanTree({ roots }) {
  return (
    <ul className="span-tree" role="tree">
      {roots.map((s) => <SpanNode key={s.spanId} span={s} depth={0} />)}
    </ul>
  );
}

function SpanNode({ span, depth }) {
  return (
    <li role="treeitem" aria-selected={false} style={{ paddingLeft: depth * 20 }}>
      <div className={`span-row${span.erroneous ? ' span-row--error' : ''}`}>
        <span className="span-dot" aria-hidden="true">●</span>
        <span className="span-name">{span.name || '—'}</span>
        <span className="span-service">{span.serviceName || '—'}</span>
        <span className="span-duration">{(span.duration || 0).toLocaleString()} ms</span>
      </div>
      {span.erroneous && span.errorMessage && (
        <p className="span-error-msg">{span.errorMessage}</p>
      )}
      {span._children?.length > 0 && (
        <ul role="group">
          {span._children.map((child) => <SpanNode key={child.spanId} span={child} depth={depth + 1} />)}
        </ul>
      )}
    </li>
  );
}
```

CSS:
```css
.trace-detail__id { font-family: 'IBM Plex Mono', monospace; font-size: 0.8125rem; color: #0043ce; }
.trace-detail__meta {
  display: flex; flex-wrap: wrap; gap: 1rem;
  margin-bottom: 1.25rem; padding: 0.75rem;
  background: #f4f4f4; border-radius: 4px;
}
.trace-meta-field { display: flex; flex-direction: column; min-width: 120px; }
.trace-meta-field__label { font-size: 0.6875rem; color: #6f6f6f; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.trace-meta-field__value { font-size: 0.875rem; font-weight: 500; color: #161616; margin-top: 2px; }
.trace-meta-field__value--error { color: #da1e28; font-weight: 700; }
.trace-detail__section-title { font-size: 0.875rem; font-weight: 600; color: #161616; margin: 1rem 0 0.5rem; }
.trace-detail__span-tree { max-height: 320px; overflow-y: auto; border: 1px solid #e0e0e0; border-radius: 4px; padding: 0.5rem; }
.span-tree, .span-tree ul { list-style: none; padding: 0; margin: 0; }
.span-row { display: flex; align-items: baseline; gap: 6px; padding: 4px 0; border-bottom: 1px solid #f4f4f4; font-size: 0.8125rem; }
.span-row--error .span-name { color: #da1e28; }
.span-dot { color: #0043ce; font-size: 0.5rem; flex-shrink: 0; }
.span-row--error .span-dot { color: #da1e28; }
.span-name     { font-weight: 600; color: #161616; }
.span-service  { color: #6f6f6f; font-size: 0.75rem; }
.span-duration { margin-left: auto; font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: #0043ce; }
.span-error-msg { font-size: 0.75rem; color: #da1e28; margin: 0 0 4px 20px; }
```

---

## `src/components/InsightPanel.jsx`

```jsx
import { Tile } from '@carbon/react';
import { Warning, Information, Checkmark } from '@carbon/icons-react';

const SEVERITY_CONFIG = {
  warning:  { icon: Warning,     iconClass: 'insight-icon--warning',  borderColor: '#f1c21b' },
  error:    { icon: Warning,     iconClass: 'insight-icon--error',    borderColor: '#da1e28' },
  info:     { icon: Information, iconClass: 'insight-icon--info',     borderColor: '#0043ce' },
  success:  { icon: Checkmark,   iconClass: 'insight-icon--success',  borderColor: '#198038' },
};

/**
 * @param {object}  props
 * @param {string}  props.finding     - What was observed
 * @param {string}  [props.evidence]  - Specific metric or trace ID
 * @param {string}  [props.impact]    - Potential impact if not addressed
 * @param {string}  [props.action]    - Recommended action
 * @param {'warning'|'error'|'info'|'success'} [props.severity]
 */
export default function InsightPanel({ finding, evidence, impact, action, severity = 'info' }) {
  const config = SEVERITY_CONFIG[severity] ?? SEVERITY_CONFIG.info;
  const IconComponent = config.icon;

  return (
    <Tile className="insight-panel" style={{ borderLeft: `3px solid ${config.borderColor}` }}>
      <div className="insight-panel__header">
        <IconComponent size={18} className={`insight-icon ${config.iconClass}`} />
        <p className="insight-panel__finding">{finding}</p>
      </div>
      {evidence && (
        <div className="insight-panel__row">
          <span className="insight-panel__field-label">Evidence</span>
          <span className="insight-panel__field-value">{evidence}</span>
        </div>
      )}
      {impact && (
        <div className="insight-panel__row">
          <span className="insight-panel__field-label">Potential Impact</span>
          <span className="insight-panel__field-value">{impact}</span>
        </div>
      )}
      {action && (
        <div className="insight-panel__row insight-panel__row--action">
          <span className="insight-panel__field-label">Recommended Action</span>
          <span className="insight-panel__field-value">{action}</span>
        </div>
      )}
    </Tile>
  );
}
```

CSS:
```css
.insight-panel { margin-bottom: 0.5rem; padding: 0.875rem 1rem; }
.insight-panel__header { display: flex; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.625rem; }
.insight-panel__finding { font-weight: 600; font-size: 0.875rem; margin: 0; flex: 1; color: #161616; line-height: 1.4; }
.insight-icon { flex-shrink: 0; margin-top: 1px; }
.insight-icon--warning { color: #c77a00; }
.insight-icon--error   { color: #da1e28; }
.insight-icon--info    { color: #0043ce; }
.insight-icon--success { color: #198038; }
.insight-panel__row {
  display: flex; gap: 0.75rem; margin-bottom: 0.3rem;
  font-size: 0.8125rem; padding-left: 1.5rem;
}
.insight-panel__field-label {
  font-weight: 600; color: #6f6f6f;
  white-space: nowrap; min-width: 130px; flex-shrink: 0;
}
.insight-panel__field-value { color: #161616; flex: 1; line-height: 1.5; }
.insight-panel__row--action .insight-panel__field-value { color: #0043ce; font-weight: 500; }
```

---

## `src/components/AppHeader.jsx`

```jsx
import { Header, HeaderName } from '@carbon/react';
import { DASHBOARD_CONFIG } from '../config/dashboardConfig';

export default function AppHeader() {
  return (
    <Header aria-label={DASHBOARD_CONFIG.appTitle}>
      <HeaderName prefix="">
        <span className="app-header__title">{DASHBOARD_CONFIG.appTitle}</span>
        <span className="app-header__subtitle">{DASHBOARD_CONFIG.appSubtitle}</span>
      </HeaderName>
    </Header>
  );
}
```

CSS:
```css
.app-header__title { font-weight: 600; font-size: 0.9375rem; }
.app-header__subtitle {
  display: block; font-size: 0.6875rem;
  font-weight: 400; color: #c6c6c6; margin-top: 1px;
}
```
