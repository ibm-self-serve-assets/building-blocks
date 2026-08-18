# Dashboard Style Guide (React + CSS Custom Properties)

## Colour Palette

Define all colours as CSS custom properties in `src/index.css` so every component inherits them consistently.

| Custom Property | Hex | Usage |
|-----------------|-----|-------|
| `--color-bg` | `#0d0d1a` | Page background (`<body>`) |
| `--color-panel` | `#16213e` | Cards, chart panels, table |
| `--color-surface` | `#1a1a2e` | Table row alternates, inputs, secondary surfaces |
| `--color-border` | `#2a2a4a` | Grid lines, dividers, card borders |
| `--color-text` | `#e0e0e0` | Primary body text |
| `--color-muted` | `#aaaaaa` | Labels, timestamps, secondary text |
| `--color-healthy` | `#22c55e` | OK status, p50 latency line, healthy KPI |
| `--color-degraded` | `#f59e0b` | Warning, p95 latency line, degraded KPI |
| `--color-error` | `#ef4444` | Errors, p99 latency line, error rate |
| `--color-accent` | `#3b82f6` | Call volume bars, links, highlights |
| `--color-trace-id` | `#7dd3fc` | Monospace trace IDs |

```css
/* src/index.css */
:root {
  --color-bg:       #0d0d1a;
  --color-panel:    #16213e;
  --color-surface:  #1a1a2e;
  --color-border:   #2a2a4a;
  --color-text:     #e0e0e0;
  --color-muted:    #aaaaaa;
  --color-healthy:  #22c55e;
  --color-degraded: #f59e0b;
  --color-error:    #ef4444;
  --color-accent:   #3b82f6;
  --color-trace-id: #7dd3fc;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--color-bg);
  color: var(--color-text);
  font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
  font-size: 14px;
  line-height: 1.5;
}
```

---

## Typography

| Element | Rule |
|---------|------|
| Body text | 14px, `var(--color-text)` |
| KPI value | 28px, weight 700, status colour variable |
| Trace IDs | `font-family: monospace`, 12px, `var(--color-trace-id)`, `cursor: pointer` |
| Chart labels | 11px, `var(--color-muted)` |
| Section headings | 11px, weight 600, uppercase, letter-spacing 0.06em, `var(--color-muted)` |

---

## Status Colour Rules

Always apply the three-tier system via CSS custom properties:

| State | Property | When to apply |
|-------|----------|---------------|
| Healthy / OK | `var(--color-healthy)` | Error rate < 1%, latency within SLO |
| Degraded | `var(--color-degraded)` | Error rate 1–5%, p95 latency SLO breach |
| Critical / Error | `var(--color-error)` | Error rate > 5%, p99 latency breach, active incidents |

```tsx
// Utility function — use everywhere status needs to drive colour
export function statusColor(status: 'healthy' | 'degraded' | 'error') {
  return `var(--color-${status})`;
}
```

---

## Chart Rules

1. **No 3D, gradients, or decorative fill** — flat stroke colours only.
2. **Consistent background:** all chart panels use `var(--color-panel)` with `var(--color-border)` borders.
3. **Grid lines:** horizontal only (`vertical={false}` in Recharts `CartesianGrid`), stroke `var(--color-border)` / `#2a2a4a`.
4. **Axis ticks:** `fill: var(--color-muted)`, fontSize 11, no axis lines or tick lines.
5. **Tooltip:** `background: var(--color-panel)`, `border: 1px solid var(--color-border)`, `color: var(--color-text)`.
6. **Legend:** `color: var(--color-muted)`, fontSize 12.

---

## Interaction Conventions

| Element | Rule |
|---------|------|
| Clickable trace IDs | `cursor: pointer`, `text-decoration: underline`, colour `var(--color-trace-id)` |
| Hover on trace IDs | Lighten to `#bae6fd` |
| Loading state | CSS spinner via `border` animation — never freeze the UI or block the main thread |
| Inline error messages | `color: var(--color-error)` directly below the failed component — not in a modal |
| Filters | Always above the data they affect; include a "Clear" button that resets to `initialFilterState` |
| Modal/side drawer | Slides in from the right, max-width `min(680px, 95vw)`, always has a visible `✕` close button and responds to `Escape` key |

---

## Responsive Layout

```css
/* Dashboard grid — two columns on wide screens */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  padding: 16px 24px;
}

@media (max-width: 768px) {
  .dashboard-grid { grid-template-columns: 1fr; }
}

/* KPI row — wrap naturally */
.kpi-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 16px 24px;
}

.kpi-card {
  background: var(--color-panel);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 12px 20px;
  min-width: 140px;
  flex: 1 1 140px;
}

.kpi-label {
  display: block;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-muted);
  margin-bottom: 4px;
}

.kpi-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
}
```

---

## CSS Spinner

```css
.spinner {
  width: 28px; height: 28px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
```
