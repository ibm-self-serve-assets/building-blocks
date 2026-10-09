---
name: ttm-dashboard
description: Scaffold a self-contained TTM forecast dashboard.html — visualises 96-step predictions, risk score, time-to-breach, and inference path badge using Apache ECharts. Works by opening directly in a browser with no server required. Also covers wiring to a live forecast API and file placement conventions.
---

# TTM Dashboard — Forecast Visualisation

## When to Generate `dashboard.html`

Generate this file when the user says any of:
- "build a dashboard", "visualise the forecast", "show me the chart"
- "create a forecast UI", "I want to see the predictions", "plot the temperature forecast"

<Steps>
<Step>
Scaffold `dashboard.html` using the template below. The file must work by opening directly in a browser — no server required.
</Step>

<Step>
Place the file in the correct location (see **File Location Convention** below).
</Step>

<Step>
If the user wants live data, replace the `FORECAST = null` stub with a `fetch()` call to their API endpoint (see **Wiring to Live API**).
</Step>
</Steps>

---

## `dashboard.html` Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>TTM Forecast Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
  <style>
    body { margin: 0; font-family: -apple-system, "Segoe UI", sans-serif;
           background: #f7f8fa; color: #1f2328; }
    header { background: #1f2328; color: #fff; padding: 16px 24px;
             display: flex; align-items: center; gap: 12px; }
    header h1 { margin: 0; font-size: 18px; font-weight: 600; }
    .badge { background: #3b82d4; color: #fff; font-size: 11px;
             padding: 2px 8px; border-radius: 4px; }
    .cards { display: flex; gap: 16px; padding: 20px 24px 0; flex-wrap: wrap; }
    .card { background: #fff; border: 1px solid #e5e7eb; border-radius: 8px;
            padding: 16px 20px; min-width: 160px; }
    .card .label { font-size: 11px; color: #57606a; text-transform: uppercase;
                   letter-spacing: .05em; }
    .card .value { font-size: 24px; font-weight: 700; margin-top: 4px; }
    .card .value.risk-high   { color: #dc2626; }
    .card .value.risk-medium { color: #d97706; }
    .card .value.risk-low    { color: #16a34a; }
    #chart { width: 100%; height: 420px; padding: 24px; box-sizing: border-box; }
    footer { text-align: center; font-size: 11px; color: #57606a;
             border-top: 1px solid #e5e7eb; padding: 12px; margin-top: 16px; }
  </style>
</head>
<body>

<header>
  <h1>TTM Forecast Dashboard</h1>
  <span class="badge" id="pathBadge">native api</span>
  <span style="margin-left:auto;font-size:13px;color:#9ca3af" id="metaLine"></span>
</header>

<div class="cards">
  <div class="card">
    <div class="label">Risk Score</div>
    <div class="value" id="riskScore">—</div>
  </div>
  <div class="card">
    <div class="label">Action</div>
    <div class="value" style="font-size:16px" id="riskAction">—</div>
  </div>
  <div class="card">
    <div class="label">Time to Breach</div>
    <div class="value" id="timeToBreach">—</div>
  </div>
  <div class="card">
    <div class="label">Predictions</div>
    <div class="value" id="predCount">—</div>
  </div>
</div>

<div id="chart"></div>

<footer>Made with IBM Bob · IBM Granite TTM · ibm/granite-ttm-512-96-r2</footer>

<script>
// ── Paste your forecast API response here ────────────────────────────────────
const FORECAST = /* INJECT_FORECAST_JSON */ null;
// ─────────────────────────────────────────────────────────────────────────────

// Or fetch from the live API — see "Wiring to Live API" section in SKILL.md
// fetch('http://localhost:5001/api/forecast/temperature-breach/TRUCK-001')
//   .then(r => r.json()).then(renderDashboard);

function renderDashboard(data) {
  if (!data) {
    document.getElementById('chart').innerHTML =
      '<p style="padding:40px;color:#57606a">Paste your forecast JSON into the FORECAST variable above.</p>';
    return;
  }

  const preds  = data.predictions || [];
  const risk   = data.risk_assessment || {};
  const meta   = data.metadata || {};
  const path   = data.inference_path || 'unknown';

  // Cards
  const score = risk.risk_score ?? '—';
  const scoreEl = document.getElementById('riskScore');
  scoreEl.textContent = typeof score === 'number' ? score + '%' : score;
  scoreEl.className = 'value ' +
    (score > 70 ? 'risk-high' : score > 40 ? 'risk-medium' : 'risk-low');

  document.getElementById('riskAction').textContent   = risk.action || '—';
  document.getElementById('timeToBreach').textContent =
    risk.time_to_breach != null ? risk.time_to_breach + ' min' : '—';
  document.getElementById('predCount').textContent    = preds.length;
  document.getElementById('pathBadge').textContent    = path.replace('_', ' ');
  document.getElementById('metaLine').textContent     =
    `${data.frequency || ''} · ${data.context_length || 512} ctx · ` +
    `${meta.inference_time_ms != null ? meta.inference_time_ms + ' ms' : ''}`;

  // Chart
  const timestamps = preds.map(p => p.timestamp.replace('T', ' ').slice(0, 16));
  const values     = preds.map(p => parseFloat(p.value.toFixed(3)));
  const threshold  = data.threshold ?? null;

  const series = [{
    name: 'Forecast', type: 'line', data: values,
    smooth: true, symbol: 'none',
    lineStyle: { color: '#3b82d4', width: 2 },
    areaStyle: { color: 'rgba(59,130,212,0.08)' },
  }];

  if (threshold !== null) {
    series.push({
      name: 'Threshold', type: 'line',
      data: new Array(values.length).fill(threshold),
      symbol: 'none',
      lineStyle: { color: '#dc2626', type: 'dashed', width: 1.5 },
    });
  }

  const chart = echarts.init(document.getElementById('chart'));
  chart.setOption({
    backgroundColor: '#ffffff',
    tooltip: { trigger: 'axis', formatter: params =>
      params.map(p => `${p.seriesName}: <b>${p.value}</b>`).join('<br>') },
    legend: { top: 8, right: 16, textStyle: { fontSize: 12 } },
    grid: { left: 56, right: 20, top: 40, bottom: 60 },
    xAxis: {
      type: 'category', data: timestamps, boundaryGap: false,
      axisLabel: { rotate: 30, fontSize: 11, color: '#57606a' },
      axisLine: { lineStyle: { color: '#e5e7eb' } },
    },
    yAxis: {
      type: 'value', name: 'Value',
      nameTextStyle: { color: '#57606a', fontSize: 11 },
      axisLabel: { color: '#57606a', fontSize: 11 },
      splitLine: { lineStyle: { color: '#f3f4f6' } },
    },
    series,
  });
  window.addEventListener('resize', () => chart.resize());
}

renderDashboard(FORECAST);
</script>
</body>
</html>
```

---

## Wiring to Live API

Replace the `FORECAST = null` stub with a `fetch` call to the running forecast backend:

```javascript
fetch('http://localhost:5001/api/forecast/temperature-breach/TRUCK-001')
  .then(r => r.json())
  .then(renderDashboard);
```

To generate a static JSON snapshot from the command line:

```bash
curl http://localhost:5001/api/forecast/temperature-breach/TRUCK-001 \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2))"
# Paste the output into the FORECAST variable in dashboard.html
```

---

## File Location Convention

Always place `dashboard.html` **inside the project subfolder** — never at the workspace root.

| Scenario | Path |
|---|---|
| Standalone new project | `<project_name>/dashboard.html` |
| Existing per-service visualisation | `forecast-backend/dashboard.html` |
| Embedded in existing main UI | `FleetOps/public/forecast-dashboard.html` |
