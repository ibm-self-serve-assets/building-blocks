# Reusable Chart Components (Recharts)

All charts are React components using `recharts`. Install: `npm install recharts`.
Shared theme constants live in `src/lib/theme.ts`.

```ts
// src/lib/theme.ts
export const COLORS = {
  error:    '#ef4444',
  degraded: '#f59e0b',
  healthy:  '#22c55e',
  accent:   '#3b82f6',
  p50:      '#22c55e',
  p95:      '#f59e0b',
  p99:      '#ef4444',
  panel:    '#16213e',
  grid:     '#2a2a4a',
  text:     '#e0e0e0',
  muted:    '#aaaaaa',
};
```

---

## Error Rate Over Time (`src/components/charts/ErrorRateChart.tsx`)

```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { COLORS } from '../../lib/theme';

interface DataPoint { time: string; errorRate: number; }

interface ErrorRateChartProps { data: DataPoint[]; }

export default function ErrorRateChart({ data }: ErrorRateChartProps) {
  return (
    <div className="chart-panel">
      <h3 className="chart-title">Error Rate (%)</h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} vertical={false} />
          <XAxis dataKey="time" tick={{ fill: COLORS.muted, fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: COLORS.muted, fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `${v}%`} />
          <Tooltip
            contentStyle={{ background: COLORS.panel, border: `1px solid ${COLORS.grid}`, color: COLORS.text }}
            formatter={(v: number) => [`${v.toFixed(2)}%`, 'Error Rate']}
          />
          <Line type="monotone" dataKey="errorRate" stroke={COLORS.error} strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
```

---

## Latency Distribution — p50 / p95 / p99 (`src/components/charts/LatencyChart.tsx`)

```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { COLORS } from '../../lib/theme';

interface DataPoint { time: string; p50: number; p95: number; p99: number; }

export default function LatencyChart({ data }: { data: DataPoint[] }) {
  return (
    <div className="chart-panel">
      <h3 className="chart-title">Latency (ms)</h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} vertical={false} />
          <XAxis dataKey="time" tick={{ fill: COLORS.muted, fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: COLORS.muted, fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `${v}ms`} />
          <Tooltip
            contentStyle={{ background: COLORS.panel, border: `1px solid ${COLORS.grid}`, color: COLORS.text }}
            formatter={(v: number, name: string) => [`${v} ms`, name]}
          />
          <Legend wrapperStyle={{ color: COLORS.muted, fontSize: 12 }} />
          <Line type="monotone" dataKey="p50" stroke={COLORS.p50} strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="p95" stroke={COLORS.p95} strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="p99" stroke={COLORS.p99} strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
```

---

## Call Volume Bar Chart (`src/components/charts/CallVolumeChart.tsx`)

```tsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { COLORS } from '../../lib/theme';

interface DataPoint { time: string; calls: number; }

export default function CallVolumeChart({ data }: { data: DataPoint[] }) {
  return (
    <div className="chart-panel">
      <h3 className="chart-title">Call Volume</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} vertical={false} />
          <XAxis dataKey="time" tick={{ fill: COLORS.muted, fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: COLORS.muted, fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip contentStyle={{ background: COLORS.panel, border: `1px solid ${COLORS.grid}`, color: COLORS.text }} />
          <Bar dataKey="calls" fill={COLORS.accent} radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
```

---

## Service Error Breakdown — Horizontal Bar (`src/components/charts/ServiceErrorChart.tsx`)

```tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { COLORS } from '../../lib/theme';

interface DataPoint { service: string; errors: number; }

export default function ServiceErrorChart({ data }: { data: DataPoint[] }) {
  return (
    <div className="chart-panel">
      <h3 className="chart-title">Errors by Service</h3>
      <ResponsiveContainer width="100%" height={Math.max(180, data.length * 36)}>
        <BarChart data={data} layout="vertical" margin={{ top: 8, right: 16, bottom: 0, left: 100 }}>
          <XAxis type="number" tick={{ fill: COLORS.muted, fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis type="category" dataKey="service" tick={{ fill: COLORS.muted, fontSize: 11 }} axisLine={false} tickLine={false} width={96} />
          <Tooltip contentStyle={{ background: COLORS.panel, border: `1px solid ${COLORS.grid}`, color: COLORS.text }} />
          <Bar dataKey="errors" fill={COLORS.error} radius={[0, 2, 2, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
```

---

## CSS Layout Variables (add to `src/index.css`)

```css
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

.chart-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  padding: 0 24px;
}

.chart-panel {
  background: var(--color-panel);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 16px;
}

.chart-title {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-muted);
  margin: 0 0 12px;
}

@media (max-width: 768px) {
  .chart-grid { grid-template-columns: 1fr; }
}
```
