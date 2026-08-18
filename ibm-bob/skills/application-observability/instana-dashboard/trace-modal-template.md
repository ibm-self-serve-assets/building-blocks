# Trace Detail Modal — React Components

## `TraceDetailModal` (`src/components/TraceDetailModal.tsx`)

```tsx
import { useEffect } from 'react';
import { useTraceDetail } from '../hooks/useInstanaData';
import SpanTree from './SpanTree';

interface Props {
  traceId: string;
  onClose: () => void;
}

export default function TraceDetailModal({ traceId, onClose }: Props) {
  const { data: trace, isLoading, isError } = useTraceDetail(traceId);

  // Close on Escape key
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onClose]);

  const errorSpans = trace?.spans?.filter(s => s.erroneous) ?? [];

  return (
    <>
      {/* Backdrop */}
      <div className="modal-backdrop" onClick={onClose} />

      {/* Side drawer */}
      <aside className="trace-modal" role="dialog" aria-modal="true" aria-label={`Trace ${traceId}`}>
        {/* Header */}
        <div className="trace-modal__header">
          <span className="trace-modal__id">{traceId}</span>
          <button className="trace-modal__close" onClick={onClose} aria-label="Close">✕</button>
        </div>

        {/* Loading / error states */}
        {isLoading && <div className="spinner" style={{ margin: 32 }} />}
        {isError && <p className="error-text" style={{ padding: 16 }}>Failed to load trace detail.</p>}

        {/* Error banner */}
        {errorSpans.length > 0 && (
          <div className="error-banner">
            <strong>⚠ {errorSpans.length} erroneous span{errorSpans.length > 1 ? 's' : ''}</strong>
            <ul>
              {errorSpans.slice(0, 5).map(s => (
                <li key={s.spanId}>{s.errorMessage || s.name}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Span tree */}
        {trace && (
          <div className="trace-modal__body">
            <SpanTree spans={trace.spans} />
          </div>
        )}
      </aside>
    </>
  );
}
```

---

## `SpanTree` Component (`src/components/SpanTree.tsx`)

```tsx
interface Span {
  spanId: string;
  parentSpanId?: string;
  name: string;
  serviceName: string;
  duration: number;
  erroneous: boolean;
  errorMessage?: string;
  _children?: Span[];
}

/** Build a nested tree from a flat span list using parentSpanId linkage */
function buildSpanTree(spans: Span[]): Span[] {
  const byId = Object.fromEntries(spans.map(s => [s.spanId, { ...s, _children: [] as Span[] }]));
  const roots: Span[] = [];
  for (const span of Object.values(byId)) {
    if (span.parentSpanId && byId[span.parentSpanId]) {
      byId[span.parentSpanId]._children!.push(span);
    } else {
      roots.push(span);
    }
  }
  return roots;
}

export default function SpanTree({ spans }: { spans: Span[] }) {
  const roots = buildSpanTree(spans);
  return (
    <ul className="span-tree" role="tree">
      {roots.map(span => <SpanNode key={span.spanId} span={span} depth={0} />)}
    </ul>
  );
}

function SpanNode({ span, depth }: { span: Span; depth: number }) {
  const colour = span.erroneous ? 'var(--color-error)' : 'var(--color-healthy)';
  return (
    <li role="treeitem" style={{ paddingLeft: depth * 20 }}>
      <div className="span-row">
        <span className="span-dot" style={{ color: colour }}>●</span>
        <span className="span-name">{span.name}</span>
        <span className="span-service">{span.serviceName}</span>
        <span className="span-duration">{span.duration.toLocaleString()} ms</span>
      </div>
      {span.erroneous && span.errorMessage && (
        <p className="span-error-msg">{span.errorMessage}</p>
      )}
      {span._children && span._children.length > 0 && (
        <ul role="group">
          {span._children.map(child => (
            <SpanNode key={child.spanId} span={child} depth={depth + 1} />
          ))}
        </ul>
      )}
    </li>
  );
}
```

---

## Clickable Trace ID Cell (`src/components/TraceTable.tsx`)

```tsx
interface Trace {
  traceId: string;
  serviceName: string;
  endpoint: string;
  duration: number;
  erroneous: boolean;
  timestamp: number;
}

interface TraceTableProps {
  traces: Trace[];
  onTraceClick: (traceId: string) => void;
}

export default function TraceTable({ traces, onTraceClick }: TraceTableProps) {
  return (
    <table className="trace-table">
      <thead>
        <tr>
          <th>Trace ID</th>
          <th>Service</th>
          <th>Endpoint</th>
          <th>Duration</th>
          <th>Status</th>
          <th>Time</th>
        </tr>
      </thead>
      <tbody>
        {traces.map(trace => (
          <tr key={trace.traceId} className={trace.erroneous ? 'row--error' : ''}>
            <td>
              <button
                className="trace-id-btn"
                onClick={() => onTraceClick(trace.traceId)}
                title="Open trace detail"
              >
                {trace.traceId.slice(0, 8)}…
              </button>
            </td>
            <td>{trace.serviceName}</td>
            <td>{trace.endpoint}</td>
            <td>{trace.duration.toLocaleString()} ms</td>
            <td>
              <span className={`status-badge status-badge--${trace.erroneous ? 'error' : 'ok'}`}>
                {trace.erroneous ? 'Error' : 'OK'}
              </span>
            </td>
            <td>{new Date(trace.timestamp).toLocaleTimeString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

---

## CSS for Modal and Span Tree (add to `src/index.css`)

```css
/* Backdrop */
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 99;
}

/* Side drawer */
.trace-modal {
  position: fixed; top: 0; right: 0;
  width: min(680px, 95vw); height: 100vh;
  background: var(--color-panel);
  border-left: 1px solid var(--color-border);
  z-index: 100;
  display: flex; flex-direction: column;
  overflow: hidden;
}

.trace-modal__header {
  display: flex; align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.trace-modal__id {
  font-family: monospace; font-size: 12px;
  color: var(--color-trace-id); flex: 1;
}

.trace-modal__close {
  background: none; border: none;
  color: var(--color-error); cursor: pointer;
  font-size: 16px; padding: 4px 8px;
}

.trace-modal__body {
  overflow-y: auto; flex: 1; padding: 16px;
}

/* Error banner */
.error-banner {
  background: #3a1a1a; border: 1px solid var(--color-error);
  border-radius: 4px; padding: 10px 16px; margin: 12px;
  color: #fca5a5; font-size: 13px;
}
.error-banner ul { padding-left: 18px; margin: 4px 0 0; }

/* Span tree */
.span-tree, .span-tree ul { list-style: none; padding: 0; margin: 0; }
.span-row {
  display: flex; align-items: baseline;
  gap: 8px; padding: 5px 0;
  border-bottom: 1px solid var(--color-surface);
  font-size: 13px;
}
.span-dot { flex-shrink: 0; }
.span-name { font-weight: 600; color: var(--color-text); }
.span-service { color: var(--color-muted); font-size: 12px; }
.span-duration { margin-left: auto; font-family: monospace; color: var(--color-degraded); font-size: 12px; }
.span-error-msg { font-size: 12px; color: #fca5a5; padding: 2px 0 6px 20px; margin: 0; }

/* Trace table */
.trace-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.trace-table th {
  text-align: left; padding: 8px 12px;
  font-size: 11px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--color-muted);
  border-bottom: 2px solid var(--color-border);
  background: var(--color-surface);
}
.trace-table td { padding: 8px 12px; border-bottom: 1px solid var(--color-surface); }
.trace-table .row--error td { background: rgba(239,68,68,0.06); }

/* Trace ID button */
.trace-id-btn {
  background: none; border: none; padding: 0;
  font-family: monospace; font-size: 12px;
  color: var(--color-trace-id); cursor: pointer;
  text-decoration: underline;
}
.trace-id-btn:hover { color: #bae6fd; }

/* Status badge */
.status-badge {
  display: inline-block; padding: 2px 8px;
  border-radius: 10px; font-size: 11px; font-weight: 600;
}
.status-badge--ok    { background: rgba(34,197,94,0.15);  color: var(--color-healthy); }
.status-badge--error { background: rgba(239,68,68,0.15); color: var(--color-error); }
```
