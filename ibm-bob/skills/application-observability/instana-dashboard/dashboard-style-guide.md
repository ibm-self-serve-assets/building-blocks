# Dashboard Style Guide (Carbon Design System + Plotly)

> ⚠️ **This guide applies to new dashboards built with the Carbon Design System.**
> The colour tokens, typography, and component names all refer to `@carbon/react` / `@carbon/styles`.
> Do **not** use the dark-theme CSS custom properties (`--color-bg`, `--color-panel`, etc.) in the
> Carbon-based dashboard — Carbon provides its own design tokens and the light theme is used.

## Colour Palette

The Carbon dashboard uses IBM Carbon's built-in colour tokens for all UI states. Do not define a custom CSS colour palette for the dashboard shell or component backgrounds.

For status indicators on KPI cards and insight panels, use these IBM Carbon-aligned hex values:

| Purpose | Hex | Carbon token equivalent |
|---------|-----|------------------------|
| Healthy / OK | `#198038` | `$support-success` |
| Degraded / Warning | `#c77a00` (text) / `#f1c21b` (border) | `$support-warning` |
| Error / Critical | `#da1e28` | `$support-error` |
| Info / Unknown | `#0043ce` (text) / `#c6c6c6` (border) | `$support-info` / `$ui-03` |
| Muted / Secondary text | `#6f6f6f` | `$text-02` |
| Primary text | `#161616` | `$text-01` |
| Page background offset | `#f4f4f4` | `$ui-01` |

---

## Typography

Carbon's own type scale is used. Custom font-size overrides in `App.css` follow these conventions:

| Element | Size | Weight | Notes |
|---------|------|--------|-------|
| Body text | 0.875rem | 400 | Carbon default |
| KPI value | 1.875rem | 700 | Status colour applied via inline style |
| KPI label | 0.6875rem | 600 | Uppercase, `#6f6f6f` |
| Trace IDs | 0.75rem | 400 | `IBM Plex Mono`, Carbon `Link` component |
| Chart titles | 0.6875rem | 600 | Uppercase, `#6f6f6f` |
| Section headings | 1rem | 600 | `<p className="section-title">` styled in `App.css` |

---

## Status Colour Rules

Three-tier system using IBM Carbon-aligned hex values:

| State | Hex (border) | Hex (text/value) | When to apply |
|-------|-------------|-----------------|---------------|
| Healthy / OK | `#198038` | `#198038` | Error rate < 1%, latency within SLO |
| Degraded | `#f1c21b` | `#c77a00` | Error rate 1–5%, p95 latency SLO breach |
| Critical / Error | `#da1e28` | `#da1e28` | Error rate > 5%, p99 latency breach |
| Unknown | `#c6c6c6` | `#161616` | No data / not enough data to assess |

---

## Chart Rules (Plotly)

All charts use Plotly (`react-plotly.js`) with the shared defaults from `src/config/plotlyDefaults.js`:

1. **No 3D, gradients, or decorative fill** — flat stroke colours only.
2. **Transparent background:** `paper_bgcolor: 'transparent'`, `plot_bgcolor: 'transparent'` — the Carbon `Tile` wrapper provides the background.
3. **Grid lines:** `gridcolor: '#e0e0e0'`, both axes.
4. **Font:** `IBM Plex Sans, -apple-system, Segoe UI, system-ui, sans-serif`, size 11, colour `#6f6f6f`.
5. **Tooltip:** `bgcolor: '#262626'`, `bordercolor: '#393939'`, font `#f4f4f4`.
6. **Responsiveness:** always pass `useResizeHandler` and `style={{ width: '100%' }}` to `<Plot>`.
7. **No mode bar:** `displayModeBar: false`.

---

## Interaction Conventions

| Element | Rule |
|---------|------|
| Clickable trace IDs | Carbon `Link` component with class `.trace-id-link` (IBM Plex Mono, 0.75rem) |
| Status badges | Carbon `Tag` — `type="red"` for Error, `type="green"` for OK |
| Loading state | Carbon `InlineLoading` inside `.state-container` — never a CSS spinner |
| Error state | Carbon `InlineNotification kind="error"` inside the affected card/section |
| Empty / no data | Carbon `InlineNotification kind="info"` inside the affected card/section |
| "No issues" message | Carbon `InlineNotification kind="info"` with `title="All clear"` |
| Modal/detail view | Carbon `ComposedModal` — responds to Escape key via Carbon's built-in handler |

---

## Responsive Layout

Carbon `Grid` + `Column` handles responsive layout. The chart rows use 8/8 (50/50) split on large screens, collapsing to full-width on small screens.

```css
/* App.css — layout and spacing only; no colour palette overrides */
.dashboard-content { padding-top: 3rem; }   /* offset for Carbon fixed header */
.tab-content       { padding: 1.5rem 1rem; }
.kpi-row           { display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem; }
.chart-row         { margin-bottom: 1rem; }
.tab-section       { margin-bottom: 2rem; }
.section-title     { font-size: 1rem; font-weight: 600; color: #161616;
                     margin: 0 0 1rem; padding-bottom: 0.5rem;
                     border-bottom: 1px solid #e0e0e0; }
```
