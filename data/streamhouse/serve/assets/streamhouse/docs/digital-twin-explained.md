# Factory Pulse — Digital Twin Explained

A plain-language and technical reference for every term, component, and concept used to build the Factory Pulse manufacturing digital twin. Aimed at engineers, solutions architects, and technical evaluators who want to understand *how* the simulation works end-to-end.

---

## Table of contents

1. [What is a digital twin?](#1-what-is-a-digital-twin)
2. [Physical world — the simulated factory network](#2-physical-world--the-simulated-factory-network)
3. [Sensor signals and telemetry](#3-sensor-signals-and-telemetry)
4. [Fault scenarios — injecting anomalies](#4-fault-scenarios--injecting-anomalies)
5. [The streaming backbone — Kafka topics](#5-the-streaming-backbone--kafka-topics)
6. [Schema governance — JSON Schema Registry](#6-schema-governance--json-schema-registry)
7. [Stream processing — Apache Flink SQL](#7-stream-processing--apache-flink-sql)
8. [Serving the twin — the backend server](#8-serving-the-twin--the-backend-server)
9. [UI component reference](#9-ui-component-reference)
   - 9.1 [App shell & global layout](#91-app-shell--global-layout)
   - 9.2 [Global state & data flow](#92-global-state--data-flow)
   - 9.3 [Shared primitive components](#93-shared-primitive-components)
   - 9.4 [Overview tab](#94-overview-tab)
   - 9.5 [Digital twin tab](#95-digital-twin-tab)
   - 9.6 [Streamhouse architecture tab](#96-streamhouse-architecture-tab)
   - 9.7 [Flink SQL tab](#97-flink-sql-tab)
   - 9.8 [Actions tab](#98-actions-tab)
   - 9.9 [AI context / MCP tab](#99-ai-context--mcp-tab)
   - 9.10 [Demo playbook tab](#910-demo-playbook-tab)
10. [FactoryTwin — 3D scene component](#10-factorytwin--3d-scene-component)
    - 10.1 [Scene primitives](#101-scene-primitives)
    - 10.2 [Robot kinematics](#102-robot-kinematics)
    - 10.3 [Lighting & shadows](#103-lighting--shadows)
    - 10.4 [Camera & controls](#104-camera--controls)
11. [PlantMap — geography component](#11-plantmap--geography-component)
12. [AI context and MCP](#12-ai-context-and-mcp)
13. [Analytical path — Tableflow and Apache Iceberg](#13-analytical-path--tableflow-and-apache-iceberg)
14. [Operations path — RTCE and MCP](#14-operations-path--rtce-and-mcp)
15. [Deployment modes](#15-deployment-modes)
16. [Glossary of all terms](#16-glossary-of-all-terms)

---

## 1. What is a digital twin?

A **digital twin** is a continuously updated software model of a physical object or system. In Factory Pulse, the twin represents a network of six fictional US manufacturing facilities — each with robots, conveyors, automated guided vehicles (AGVs), and production lines.

The twin has three layers:

| Layer | What it does | Technology |
|---|---|---|
| **Simulation** | Generates synthetic but physically plausible sensor readings on every clock tick | Python `FactorySimulation` class |
| **Event stream** | Transports every reading from the simulator to consumers | Confluent Kafka or local in-memory queue |
| **Visualization** | Renders the live state as an interactive 3D factory floor and dashboard | React, Three.js, Recharts |

---

## 2. Physical world — the simulated factory network

### Factory sites

Six fictional US plants are declared in [`server/plants.py`](../server/plants.py). Their city coordinates are real, but the facilities are invented for this demonstration.

| ID | Name | Type | Lines | Robots | Region |
|---|---|---|---|---|---|
| `DET` | Detroit Assembly | Automotive assembly | 8 | 12 | Midwest |
| `AUS` | Austin Gigafactory | Battery / robotics | 6 | 14 | South |
| `SEA` | Seattle Precision | Precision components | 5 | 10 | West |
| `PHX` | Phoenix Semicon | Electronics | 7 | 16 | West |
| `CLT` | Charlotte Manufacturing | Industrial machinery | 6 | 11 | East |
| `CHI` | Chicago Distribution | Packaging / fulfillment | 4 | 9 | Midwest |

### Robot types

Each site models six robot roles (indices 0–5):

| Index | Role |
|---|---|
| 0 | Welding robot |
| 1 | Pick & place |
| 2 | Quality scanner |
| 3 | Assembly cobot |
| 4 | AGV transporter |
| 5 | Packaging arm |

Each robot carries a live asset ID in the format `{SITE_ID}-R0{N}` (e.g., `DET-R01`).

### Other physical assets in the 3D scene

- **Conveyor belt** — a three-lane belt carrying parts between robot stations; modeled in [`FactoryTwin.jsx`](../frontend/src/components/FactoryTwin.jsx) as the `Conveyor` component.
- **AGV (Automated Guided Vehicle)** — a wheeled cart that moves continuously along the factory floor; modeled as the `AGV` component.
- **Structural beams and gantry** — the building skeleton rendered with `Beam` primitives.

---

## 3. Sensor signals and telemetry

Every simulation tick the [`FactorySimulation.step()`](../server/simulation.py) method computes the following physical signals for each robot, influenced by the active scenario and a sinusoidal noise function:

| Signal | Unit | Normal range | Description |
|---|---|---|---|
| `temperature` | °C | 35–45 | Surface / motor temperature of the asset |
| `vibration` | mm/s | 1.1–2.0 | Spindle or bearing vibration amplitude |
| `rpm` | RPM | 1 750–1 850 | Motor shaft rotation speed |
| `energyKw` | kW | 12–15 | Instantaneous power draw |
| `qualityScore` | % | 97–99.3 | First-pass yield or inspection pass rate |
| `health` | % (integer) | 85–100 | Composite asset condition index |
| `status` | enum | `running` / `warning` / `stopped` | Derived from threshold checks |

### Alert thresholds (defined in `simulation.py`)

A robot moves to `warning` when **any** of these conditions is true:
- `temperature > 72 °C`
- `vibration > 5.2 mm/s`
- `qualityScore < 86 %`

### OEE — Overall Equipment Effectiveness

`OEE` is the headline performance metric per site. It is computed as a **smoothed exponential average** on every tick:

```
site_oee = site_oee × 0.67 + target_oee × 0.33
```

The target OEE depends on the active scenario and severity:

| Scenario | OEE impact |
|---|---|
| `baseline` | ~96 % |
| `bearing` | −17 × severity |
| `thermal` | −23 × severity |
| `quality` | −21 × severity |
| `surge` | +2 × severity (throughput bonus) |

### Throughput

`throughput` is the number of units per minute produced by a site, calculated as:

```
throughput = lines × 16 × (oee / 98)
```

Multiplied by 1.25 during `surge` mode. Zero when the site is paused.

---

## 4. Fault scenarios — injecting anomalies

The `inject()` method on the simulation accepts one of five scenarios, each with a `severity` (0–100 %) that scales the signal distortion.

| Scenario ID | Display name | Primary signals affected | Alert type emitted |
|---|---|---|---|
| `baseline` | Healthy operations | All nominal | None |
| `bearing` | Bearing wear | Vibration ↑, OEE ↓, health ↓ | `BEARING_RISK` |
| `thermal` | Thermal excursion | Temperature ↑, energy ↑ | `OVERHEAT` |
| `quality` | Quality drift | Quality score ↓, OEE ↓ | `QUALITY_DRIFT` |
| `surge` | Demand surge | Throughput ↑, RPM ↑, energy ↑ | `CAPACITY_PRESSURE` |

Alerts are emitted every 5 ticks when the scenario is active and `severity ≥ 35 %`. They appear in the event trace and are published to the `factory-maintenance-events` Kafka topic.

---

## 5. The streaming backbone — Kafka topics

Three **source topics** are produced by the local simulator on every tick. In Kafka mode they carry real schema-encoded messages; in simulation mode they are queued in memory.

### `factory-iot-telemetry`

One record per robot per tick (two robots are selected per tick per site using a round-robin index). Contains the full sensor snapshot plus scenario metadata.

**Key:** `{ "id": "<assetId>" }`  
**Value fields:** `eventId`, `timestamp`, `siteId`, `siteName`, `assetId`, `assetType`, `lineId`, `scenario`, `temperature`, `vibration`, `rpm`, `energyKw`, `qualityScore`, `health`, `status`, `batchId`

### `factory-asset-state`

Published every 3 ticks for the first three robots of each site. Designed for **RTCE compaction** (latest-state store).

**Key:** `{ "id": "<assetId>" }`  
**Value fields:** `assetId`, `siteId`, `timestamp`, `status`, `health`, `temperature`, `vibration`, `qualityScore`, `scenario`

### `factory-maintenance-events`

Emitted when an alert is generated (every 5 ticks under a fault scenario with severity ≥ 35 %).

**Key:** `{ "id": "<alertId>" }`  
**Value fields:** `eventId`, `timestamp`, `siteId`, `assetId`, `eventType`, `severity`, `message`, `acknowledged`

### Flink-derived topics (output)

Created and populated by the Flink SQL recipes. They are read back by the optional derived Kafka consumer.

| Topic | Produced by | Content |
|---|---|---|
| `factory-risk-signals` | `02-risk-signal.sql` | Per-event risk classification |
| `factory-shift-kpis` | `03-shift-kpis.sql` | 1-minute aggregated KPIs per site |
| `factory-quality-alerts` | `04-quality-alerts.sql` | Inspection/quarantine decisions |

---

## 6. Schema governance — JSON Schema Registry

When running in Kafka mode (`STREAM_MODE=kafka`), the backend registers **JSON Schema** contracts for every topic's key and value subjects in Confluent Schema Registry before producing any messages.

Schemas are defined in [`server/schemas.py`](../server/schemas.py). The key schema is shared across all topics:

```json
{ "type": "object", "properties": { "id": { "type": "string" } } }
```

Each value schema is strict (`additionalProperties: false`), enforcing contract compliance for all downstream consumers including Flink, Tableflow, and RTCE.

Schema subject naming follows the **TopicNameStrategy** convention:
- `factory-iot-telemetry-key`
- `factory-iot-telemetry-value`
- …and so on for each topic.

Each message is wire-format encoded with the schema ID, ensuring every consumer can retrieve the correct schema version from the registry.

---

## 7. Stream processing — Apache Flink SQL

Four SQL files in [`flink/`](../flink/) implement the **TRANSFORM** layer of the Streamhouse architecture. They run on a provisioned **Confluent Cloud Flink compute pool** — not embedded locally.

### `01-create-tables.sql` — Schema & sources

Declares the three output tables (`factory-risk-signals`, `factory-shift-kpis`, `factory-quality-alerts`). The *source* tables (`factory-iot-telemetry`, etc.) are **inferred** by Confluent Flink from the Schema Registry schemas — no `CREATE TABLE` is needed for them.

### `02-risk-signal.sql` — Predictive risk detection

A **per-event** `INSERT INTO … SELECT` statement that classifies every sensor reading into a risk type using `CASE WHEN` threshold logic:

| Condition | Risk type | Severity |
|---|---|---|
| `vibration > 5.2` | `BEARING_RISK` | `critical` if > 6.5, else `warning` |
| `temperature > 72` | `THERMAL_RISK` | `critical` if > 85, else `warning` |
| `qualityScore < 86` (default) | `QUALITY_RISK` | `critical` if < 80, else `warning` |

Risk score is a numeric value derived from the raw sensor reading scaled to a comparable magnitude.

### `03-shift-kpis.sql` — Tumbling window KPIs

Aggregates `factory-iot-telemetry` over **1-minute tumbling windows** using Confluent's built-in `$rowtime` attribute:

- `sampleCount` — number of sensor readings in the window
- `meanTemperature`, `meanVibration`, `meanQuality` — per-site averages
- `energyKwhEstimate` — total energy kW summed and divided by 60 (converting kW readings to kWh)

Results are grouped by `siteId`, `window_start`, and `window_end`.

### `04-quality-alerts.sql` — Inspection routing

Filters events where `qualityScore < 86` and assigns a downstream action:

| Quality score | Action |
|---|---|
| < 78 | `QUARANTINE_BATCH` |
| 78–86 | `REQUEST_INSPECTION` |

---

## 8. Serving the twin — the backend server

The Python/Flask backend in [`server/app.py`](../server/app.py) is the central nervous system of the digital twin. It:

1. Runs a **background simulation loop** (`_publisher_loop`) on a configurable interval (default 1.7 s) that calls `sim.step()` and publishes the resulting batch to Kafka.
2. Pushes state updates to all connected browser clients via **Server-Sent Events (SSE)** on `/api/events`.
3. Exposes REST routes for UI interactions.

### Key server modules

| Module | Responsibility |
|---|---|
| [`simulation.py`](../server/simulation.py) | All synthetic physics: sensor math, fault injection, OEE, alerts, actions |
| [`plants.py`](../server/plants.py) | Static site metadata, robot types, scenario definitions |
| [`kafka.py`](../server/kafka.py) | Confluent Kafka producer, Schema Registry registration, optional derived consumer |
| [`schemas.py`](../server/schemas.py) | JSON Schema objects for all three source topic values |
| [`context.py`](../server/context.py) | Rule-based, transparent demo answers for AI context questions |
| [`mcp.py`](../server/mcp.py) | Real Confluent RTCE MCP connector using streamable-HTTP transport |

### Server-Sent Events (SSE)

The browser subscribes to `/api/events` and receives named events pushed over a persistent HTTP connection:

| Event name | Payload | Trigger |
|---|---|---|
| `snapshot` | Full factory network state | Every simulation tick |
| `alert` | A newly generated maintenance alert | On threshold breach |
| `scenario` | Current scenario change | On `inject()` call |
| `action` | Control action taken | On `act()` call |
| `cloud` | Kafka transport status | After each publish batch |
| `flink` | Derived Flink topic record | When derived consumer is active |

### REST API summary

| Route | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Server, Kafka transport, cloud status, and MCP configuration |
| `/api/bootstrap` | GET | Initial snapshot, sites, scenarios, and cloud status |
| `/api/events` | GET | SSE stream (`snapshot`, `alert`, `scenario`, `action`, `cloud`, `flink`) |
| `/api/simulate` | POST | Inject a fault scenario (bearing, thermal, quality, surge) with intensity |
| `/api/control` | POST | Pause, resume, maintenance, acknowledge; optional webhook dispatch |
| `/api/context` | POST | Rule-based AI Q&A (maintenance, quality, energy, operations briefing) |
| `/api/mcp/tools` | GET | List real RTCE MCP tools via remote streamable-HTTP proxy |
| `/api/mcp/call` | POST | Call a real RTCE MCP tool with validated JSON arguments |
| `/api/stream` | GET | Kafka status, published counts, and last derived record |
| `/api/stream-mode` | POST | Toggle stream mode between `kafka` (live Confluent) and `sim` (local) |

---

## 9. UI component reference

All UI source lives under [`frontend/src/`](../frontend/src/). The entry point is [`main.jsx`](../frontend/src/main.jsx), which mounts [`App.jsx`](../frontend/src/App.jsx). Styles are in [`styles.scss`](../frontend/src/styles.scss), which imports Carbon React tokens and IBM Plex fonts.

---

### 9.1 App shell & global layout

**File:** [`frontend/src/App.jsx`](../frontend/src/App.jsx)

The shell is a three-zone CSS layout rendered at all times regardless of the active tab:

```
┌──────────────────────────────────────────────────────┐
│  .global-header  (fixed, height 56 px, z-index 120)  │
├────────────┬─────────────────────────────────────────┤
│  .sidebar  │  .main-content > .main-inner            │
│  (fixed,   │  (scrollable, margin-left matches       │
│  220 px)   │   sidebar width)                        │
└────────────┴─────────────────────────────────────────┘
```

#### `.global-header`

| Sub-element | CSS class | Content |
|---|---|---|
| Brand mark | `.brand` | `◈` symbol + "Factory**Pulse**" wordmark + divider + subtitle |
| Simulation clock | `.header-clock` | Blinking `Radio` icon + "SIMULATION CLOCK" + formatted time from `data.timestamp` |
| Connection badge | `DataBadge` component | Cloud / simulation mode pill |
| Avatar | `.avatar` | Static "FP" initials block |

**To change the brand name or logo:** edit the `.brand` JSX block in `App.jsx` (lines ~42–43) and the `.brand-symbol`, `.brand-text`, `.brand-divider` CSS rules in `styles.scss`.

#### `.sidebar`

A fixed left navigation column. On screens ≤ 1050 px it collapses to 60 px (icon-only) and hides labels.

| Sub-element | CSS class | Content |
|---|---|---|
| Section label | `.nav-label` | "WORKSPACE" uppercase label |
| Nav buttons | `sidebar nav button` | One per entry in the `NAV` array; active tab gets `.active` class + chevron |
| Version footer | `.side-version` | "IBM + CONFLUENT" + version text |
| Copyright | `.side-copyright` | "© 2026 Factory Pulse" |

**To add a new tab:** add an object to the `NAV` array in `App.jsx` (line 8) with `{ id, label, icon }`, then add a corresponding `{tab==='<id>'&&<>…</>}` block in the render section.

#### `.main-content` / `.main-inner`

Scrollable right region. Every tab renders inside `.main-inner`, which has padding `30px 30px 0`. Contains:
- `.page-top` — breadcrumb + page `<h1>` + streaming tick counter
- A toast notification band (`notice` state) with `.toast` class
- Tab-specific content blocks

---

### 9.2 Global state & data flow

**File:** [`frontend/src/App.jsx`](../frontend/src/App.jsx), `App()` function (line 28 onward)

All application state is held in a single `useState` set at the top of `App`. No external state library is used.

| State variable | Type | Initial value | Updated by |
|---|---|---|---|
| `tab` | `string` | `'overview'` | Sidebar nav clicks, story step buttons |
| `data` | `object\|null` | `null` | `/api/bootstrap` then SSE `snapshot` events |
| `cloud` | `object\|null` | `null` | `/api/bootstrap` then SSE `cloud` events |
| `selected` | `string` | `'DET'` | `SitePicker`, `PlantMap` marker clicks |
| `scenario` | `string` | `'baseline'` | Scenario `<select>` in twin tab |
| `intensity` | `number` | `85` | Range slider in twin tab |
| `playing` | `boolean` | `true` | Pause/resume button in twin tab |
| `notice` | `string` | `''` | Any API call success/error; cleared by toast × button |
| `script` | `string` | `'risk'` | SQL sidebar selection in Flink tab |
| `focusBlock` | `string` | `'transform'` | Architecture node clicks |
| `question` | `string` | `QUESTIONS[0]` | Prompt chip clicks, chat input |
| `answer` | `object\|null` | `null` | `/api/context` response |
| `thinking` | `boolean` | `false` | While `/api/context` is in-flight |
| `tools` | `array\|null` | `null` | `/api/mcp/tools` response |
| `mcpStatus` | `string` | `'idle'` | `'idle'` / `'loading'` / `'connected'` / `'error'` |
| `toolName` | `string` | `''` | MCP tool `<select>` |
| `toolArgs` | `string` | `'{}'` | MCP arguments `<textarea>` |
| `toolResult` | `object\|null` | `null` | `/api/mcp/call` response |
| `derived` | `object\|null` | `null` | `/api/bootstrap` then SSE `flink` events |
| `busy` | `boolean` | `false` | While any mutation API call is in-flight |

**Data helpers defined in `App.jsx`:**

| Helper | Signature | What it does |
|---|---|---|
| `call` | `call(path, body?)` | Fetch wrapper: GET if no body, POST with JSON body otherwise; throws on non-2xx |
| `inject` | `inject(sc, value)` | Calls `POST /api/simulate`; sets `scenario`, emits notice |
| `control` | `control(action)` | Calls `POST /api/control`; emits notice including webhook dispatch confirmation |
| `ask` | `ask(q)` | Calls `POST /api/context`; sets `answer` |
| `discover` | `discover()` | Calls `GET /api/mcp/tools`; populates `tools`, sets `toolName` to first |
| `invoke` | `invoke()` | Calls `POST /api/mcp/call`; sets `toolResult` |
| `copy` | `copy(text)` | Writes text to clipboard; shows notice |

---

### 9.3 Shared primitive components

These small components are defined inline at the top of [`App.jsx`](../frontend/src/App.jsx) and reused across all tabs.

#### `Dot`

```jsx
<Dot status="healthy|warning|idle" />
```

Renders a colored `<span>` with class `status-dot {status}`. Colors defined in `styles.scss`:
- `healthy` → teal `#42be65`
- `warning` → amber/red
- `idle` → gray

**To change status colors:** edit the `.status-dot.healthy`, `.status-dot.warning`, `.status-dot.idle` rules in `styles.scss`.

#### `Status`

```jsx
<Status status="healthy|warning|idle" />
```

Wraps a `Dot` inside a `<span className="site-status {status}">` with a human-readable label ("Operational" / "Attention" / "Paused"). Used in panel headings to show per-site health at a glance.

#### `PanelHeading`

```jsx
<PanelHeading eyebrow="SECTION LABEL" title="Panel title" action={<ReactNode />} />
```

Renders a two-row heading with a small-caps eyebrow label, an `<h3>` title, and an optional right-aligned action slot (typically a status badge or link button). CSS class: `.panel-heading`.

#### `MetricCard`

```jsx
<MetricCard
  icon={LucideIcon}
  label="Card label"
  value={numericOrString}
  unit="units/min"
  trend="↗ live"
  detail="supporting text"
/>
```

A standalone KPI tile. Structure:
- `.metric-head` — label + icon row
- `.metric-value` — large value + unit
- `.metric-foot` — trend string (`.positive`) + detail text

CSS class: `.metric-card`. Used in the 4-column `.metrics-grid` on the Overview tab.

**To add a new KPI card:** add a `<MetricCard>` to the `.metrics-grid` div and feed it a value from the `data.summary` object.

#### `MiniTrends`

```jsx
<MiniTrends
  history={site.history}   // array of tick objects
  keyName="oee"            // which field to plot (default: 'oee')
  stroke="#25b3bd"         // line/fill color
  height={95}              // container height in px
/>
```

Renders a Recharts `AreaChart` inside a `ResponsiveContainer`. The chart shows up to 55 data points (the rolling history buffer). Uses a `linearGradient` fill and a custom dark `Tooltip`. Animation is disabled (`isAnimationActive={false}`) to prevent jitter on live updates.

**Supported `keyName` values in the history buffer:** `oee`, `output`, `temp`, `vibration`, `quality`.

**To add a new trend line:** add the desired field to the simulation's `history.append(…)` call in `simulation.py` and pass the new key name as `keyName`.

#### `SitePicker`

```jsx
<SitePicker sites={sites} selected={selected} onSelect={choose} />
```

A horizontal row of `<button>` elements, one per factory site. The active site gets class `.selected` (blue border + background). Each button shows a `Dot`, the city name, and the site ID in monospace. CSS class: `.site-picker`.

#### `DataBadge`

```jsx
<DataBadge cloud={cloud} />
```

The cloud connection status pill in the global header. Two variants:
- `.cloud-live` — green pill: "CONFLUENT CLOUD CONNECTED" (when `cloud.mode === 'kafka'` and `cloud.status === 'connected'`)
- `.mock` — gray pill: one of "SIMULATION MODE" / "CLOUD CONNECTION ERROR" / "CLOUD CONFIG REQUIRED"

CSS class: `.connection-tag`.

#### `Bar`

```jsx
<Bar value={72} color="#0f62fe" />
```

A simple CSS progress bar. `.bar-track` wraps `.bar-fill`, whose `width` is clamped to `[0, 100]%`. Used inline for OEE and throughput indicators on the twin side panel and overview.

---

### 9.4 Overview tab

**Tab ID:** `overview` | **Label:** "Command center"

Rendered when `tab === 'overview'`. Layout (top to bottom):

#### Hero banner — `.hero`

Full-width promotional block with a headline, sub-copy, and a CTA button ("Explore live digital twin"). The right side shows an animated orbital decoration (`.big-orbit`, `.orbit-core`, `.orbit-label`) with three floating tags: STREAM / TRANSFORM / SERVE.

**To change the headline or CTA text:** edit the `<h2>` and `<button>` inside the `.hero` JSX block (around line 48 in `App.jsx`).

#### KPI strip — `.metrics-grid`

Four `MetricCard` instances in a 4-column grid:

| Card | Value source | Unit |
|---|---|---|
| Total throughput | `data.summary.throughput` | units / min |
| Network OEE | `data.summary.oee` | % |
| Active incidents | `data.summary.activeAlerts` | open |
| Telemetry rate | `data.summary.eventsPerSecond` | ev / sec |

CSS: `grid-template-columns: repeat(4, 1fr)` on large screens; collapses to 2 columns below 730 px.

#### Overview grid — `.overview-grid`

Two-column grid (`1.7fr 1fr`) containing:

1. **Network panel** (`.network-panel`) — `PanelHeading` + `PlantMap` + `.plant-strip` (mini buttons for quick site switching showing city name + OEE %).
2. **Pulse panel** (`.pulse-panel`) — selected site detail: type, lines, OEE bar, live insight text, two quick scenario buttons, and a full-width Carbon `Button` to open the twin.

**To add a new quick-inject scenario button:** add a `<button>` to the `.scenario-mini-grid` div and call `inject('scenarioId', severity)`.

#### Flow steps — `.under-flow`

The end-to-end architecture strip. Renders the 5 items in the `FLOW` array as clickable `.flow-step` blocks separated by `ArrowRight` icons. Clicking a block sets `focusBlock` and switches to the architecture tab.

**To edit flow step copy:** update the corresponding object in the `FLOW` constant (lines 9–9 in `App.jsx`). Fields: `id`, `step`, `tag`, `name`, `product`, `desc`, `detail`.

---

### 9.5 Digital twin tab

**Tab ID:** `twin` | **Label:** "Digital twin"

Rendered when `tab === 'twin'`. Layout:

#### Twin toolbar — `.twin-toolbar`

Full-width bar with:
- Left: `SitePicker` for switching the active plant
- Right: running/total robot count badge (`.twin-meta`) + Pause/Resume animation toggle button (`.outlined-action`)

#### Twin layout — `.twin-layout`

Two-column grid (`1.8fr 0.8fr`):

**Left — `.twin-stage`**

Contains the `FactoryTwin` 3D canvas (see section 10) plus:
- `.twin-stage-header` — eyebrow breadcrumb + 3 tally badges (robots, lines, "3D SCENE")
- `.stage-bottom` — asset name + orbit hint

**Right — `.twin-side` (condition monitoring panel)**

| Sub-section | What it shows | How to change |
|---|---|---|
| `.twin-kpi-row` | OEE % + `Bar` / throughput value | Reads `site.oee`, `site.throughput` |
| Fault injection lab | Scenario `<select>`, severity `<input type="range">`, inject `Button`, pause/resume + simulate-repair row | `scenario` / `intensity` state; calls `inject()` / `control()` |
| `.sensor-list` | Scrollable list of all robots: name, status `Dot`, vibration bar, temperature, quality | Iterates `site.robots`; each row is `.sensor-item` |

**Scenario `<select>` options** (hardcoded in JSX):

| Value | Label |
|---|---|
| `baseline` | Healthy operations |
| `bearing` | Predictive bearing wear |
| `thermal` | Thermal excursion |
| `quality` | Quality drift |
| `surge` | Demand surge |

**To add a new scenario option:** add an `<option>` to the `<select>` and add the corresponding case to `simulation.py`'s `inject()` method and `step()` physics.

#### Twin bottom grid — `.twin-bottom-grid`

Two trend charts side by side (`1fr 1fr`):

| Chart | `keyName` | Stroke |
|---|---|---|
| Vibration / last 55 ticks | `vibration` | `#36afc6` |
| OEE / last 55 ticks | `oee` | `#8f77d3` |

Both use `MiniTrends` at `height={145}`.

---

### 9.6 Streamhouse architecture tab

**Tab ID:** `architecture` | **Label:** "Streamhouse"

Rendered when `tab === 'architecture'`. Layout:

#### Intro block — `.architecture-intro`

Large heading with italic blue accent text and a description paragraph. Static copy — edit directly in the JSX (around line 61).

#### Architecture surface — `.arch-surface`

Dark-background interactive node diagram. Five nodes (one per `FLOW` entry) rendered as `.arch-node` buttons connected by `.arch-join` arrows. The focused node (matching `focusBlock` state) gets class `.arch-node.focused` (blue top-border accent).

Below the nodes, two outcome cards (`.arch-outcomes` grid) show:
- **Analytical path** — Tableflow → Apache Iceberg
- **Operational path** — RTCE → MCP → AI agents

**To change a node's icon or copy:** update the corresponding `FLOW` object in `App.jsx` (line 9). The icon array `[Cpu, RadioTower, Workflow, ShieldCheck, Layers3]` maps by index position.

#### Deep-dive panel — `.arch-detail`

Shows the full `detail` text of the currently focused block, its step number, and a link button to IBM reference docs.

#### Principles strip — `.arch-principles`

Three equal columns with icon + heading + description. Static content — edit the JSX inline (around line 64).

---

### 9.7 Flink SQL tab

**Tab ID:** `flink` | **Label:** "Flink SQL"

Rendered when `tab === 'flink'`. Layout:

#### Studio header — `.studio-top`

Headline + description on the left; a teal badge (`.studio-tag`) on the right showing "4 SQL recipes".

#### SQL studio — `.sql-studio`

Two-column panel (`235px sidebar + flex main`):

**Left — `.sql-sidebar`**

A list of script buttons, one per entry in `SCRIPTS` (imported from [`sql.js`](../frontend/src/sql.js)). Active script gets `.active` class (blue left border). Below the list, a help callout describes Flink compute pool prerequisites.

**Right — `.sql-main`**

- Header with script title, description, and a "Copy SQL" button (calls `copy(activeScript.code)`)
- `<pre className="code-view">` — monospace code display, dark background, max-height 520 px, scrollable
- Status footer with a dot + label and a link to the Confluent Flink guide

**To add a new SQL script:** add a raw-import entry in [`sql.js`](../frontend/src/sql.js) and a corresponding `.sql` file under `flink/`.

#### Derived topic monitor — `.flink-output`

Shows the last received Flink output record (`derived` state) as pretty-printed JSON in a `<pre>`. If no derived data is available, shows an empty-state block explaining how to enable the Kafka consumer.

---

### 9.8 Actions tab

**Tab ID:** `actions` | **Label:** "Actions"

Rendered when `tab === 'actions'`. Layout:

#### Intro block — `.page-intro`

Static heading + paragraph distinguishing Flink Topic Actions from business workflow actions. Edit the JSX inline (around line 72).

#### Actions grid — `.actions-grid`

Two equal-width panels side by side:

**Left — Flink Topic Actions panel**

Three static `.action-option` rows:

| Action name | Detail |
|---|---|
| Deduplicate records | Remove repeated IoT events before downstream scoring |
| Mask sensitive fields | Produce governed streams for safe analytics sharing |
| Transform topic | Change keys, field names, and serialization format |

Each row has a blue icon box (`.action-symbol`), a name/detail block, and a `FLINK ACTION` label. A link button at the bottom opens the Confluent Flink Topic Actions docs.

**To add a new Flink Topic Action row:** extend the inline array of `{ icon, name, detail, tag }` objects in the JSX (around line 73).

**Right — Business actions panel**

- `.action-status-card` — three status rows: plant state, unacknowledged alerts count, Kafka producer status
- `.action-cta-list` — three action buttons:

| Button | Action sent | Effect |
|---|---|---|
| Schedule maintenance | `maintenance` | Resets wear; optional webhook dispatch |
| Acknowledge incidents | `acknowledge` | Clears open alert count for the site |
| Generate critical event | Injects `bearing` at 90 % | Drives fault to the alert topic |

All three call `control()` or `inject()` and are disabled while `busy === true`.

**To add a new business action button:** add a `<button>` to `.action-cta-list` that calls `control('newAction')`, and add the case in `simulation.py`'s `act()` method.

#### Event feed — `.event-feed`

A table of the last 9 alerts from `data.alerts`. Columns: TIME / PLANT / EVENT / SEVERITY. Severity uses a Carbon `Tag` component: red for unacknowledged critical, warm-gray for warning, gray for acknowledged.

---

### 9.9 AI context / MCP tab

**Tab ID:** `context` | **Label:** "AI context / MCP"

Rendered when `tab === 'context'`. Layout:

#### Context header — `.context-top`

Headline + description on the left. On larger screens, a rotated diamond badge (`.context-chip`) on the right.

#### Context grid — `.context-grid`

Two panels side by side (`1.1fr 0.9fr`):

**Left — Ask Factory Pulse (`.chat-panel`)**

| Sub-element | Class | Purpose |
|---|---|---|
| Context indicator | `.chat-selected` | Shows active site + "latest sensor snapshot" |
| Prompt chips | `.prompt-chips` | Four preset question buttons from the `QUESTIONS` array |
| Answer area | `.answer-space` | Shows answer card or placeholder |
| Chat input | `.chat-form` | Text `<input>` + send `<button>`; Enter key submits |

Answer card structure (when `answer` is set):
- `.answer-source` — "LOCAL DEMO RULES — NOT MCP/LLM" label
- `<h4>` — answer title
- `<p>` — answer body text
- `.answer-evidence` — evidence chip spans
- `.answer-next` — suggested next action

**To add or change preset questions:** edit the `QUESTIONS` array constant (line 10 in `App.jsx`).

**Right — MCP tool explorer (`.mcp-panel`)**

| Sub-element | Purpose |
|---|---|
| Description paragraph | Explains that RTCE credentials stay server-side |
| `.mcp-outline` | Three static feature rows: RTCE / governed records / agent-readable responses |
| "Discover remote MCP tools" button | Calls `discover()`; sets `mcpStatus` |
| Tool selector + args `<textarea>` | Shown once `tools` is populated |
| "Invoke tool" button | Calls `invoke()`; sets `toolResult` |
| `.mcp-result` `<pre>` | Pretty-printed `toolResult` JSON |
| `.mcp-note` | Prerequisites callout |

---

### 9.10 Demo playbook tab

**Tab ID:** `story` | **Label:** "Demo playbook"

Rendered when `tab === 'story'`. Layout:

#### Story hero — `.story-hero`

Dark-background full-width banner. Contains headline, persona description, and three tag pills (`.story-tags`) identifying the persona, trigger, and outcome. Static content — edit the JSX inline (around line 83).

#### Story steps — `.story-steps`

A 2-column grid of 6 clickable step buttons. Each renders from the `STEPS` array. Clicking a step:
1. Switches `tab` to `step.tab`
2. If step `03`, also calls `inject('bearing', 85)` to automatically inject the fault scenario

**`STEPS` array structure** (defined in `App.jsx`, lines 11–18):

| Field | Type | Purpose |
|---|---|---|
| `no` | string | Step number displayed in large monospace font |
| `title` | string | Bold step heading |
| `body` | string | Descriptive paragraph |
| `tab` | string | Tab to navigate to when clicked |

**To add a step or change copy:** edit the `STEPS` array.

#### Business outcome panel — `.final-story`

Static concluding panel with a heading, paragraph, and three `.value-row` outcome chips (green checkmarks). Edit directly in the JSX.

---

## 10. FactoryTwin — 3D scene component

**File:** [`frontend/src/components/FactoryTwin.jsx`](../frontend/src/components/FactoryTwin.jsx)

Renders a WebGL scene using **React Three Fiber** (a React renderer for Three.js) and **@react-three/drei** utility components.

**Props of the exported `FactoryTwin` component:**

| Prop | Type | Default | Purpose |
|---|---|---|---|
| `site` | object | — | The currently selected site from the snapshot; drives robot states |
| `playing` | boolean | `true` | When `false`, freezes all `useFrame` animations |

The outer wrapper is `<div className="twin-canvas">` (height 495 px, `position: relative`, dark background). Two `.twin-overlay` labels float over the canvas: top-left shows site ID; bottom shows orbit hint and kinematic state.

### 10.1 Scene primitives

| Component | File | Props | What it renders |
|---|---|---|---|
| `Beam` | `FactoryTwin.jsx` | `position`, `size` ([w,h,d]), `color` | `<boxGeometry>` structural element — used for structural beams, rails, and panels |
| `Robot` | `FactoryTwin.jsx` | `position`, `index`, `state` (robot obj), `active` | A 4-joint articulated arm: base cylinder → shoulder → forearm → gripper jaw |
| `Conveyor` | `FactoryTwin.jsx` | `z` (Z offset), `reverse` | Double-rail belt with 5 animated cargo blocks sliding along X-axis |
| `AGV` | `FactoryTwin.jsx` | `active` | Wheeled cart oscillating along X, rotating 180° at each end |
| `Scene` | `FactoryTwin.jsx` | `site`, `playing` | Root assembly: lights, floor, grid, 6 robot cells, Conveyor, AGV, `ContactShadows`, `OrbitControls` |

### 10.2 Robot kinematics

Each `Robot` uses `useFrame` to animate four `useRef` joints every frame via sine functions phase-shifted by `index * 1.7`:

| Joint ref | Animated property | Expression |
|---|---|---|
| `base` | `rotation.y` | `sin(t × 0.55 + s) × 0.7` |
| `shoulder` | `rotation.z` | `0.37 + sin(t × 0.87 + s) × 0.30` |
| `forearm` | `rotation.z` | `−0.75 + sin(t × 1.14 + s + 0.8) × 0.36` |
| `jaw` | `position.y` | `sin(t × 1.7 + s) × 0.07` |

Animation is skipped entirely when `active === false` (site paused or robot stopped).

**Status indicator colors** (defined by `state.status`):

| Status | LED color | Floor ring color |
|---|---|---|
| `running` | `#24d7b4` (teal) | `#5ea0ba` (blue-teal) |
| `warning` | `#ff6b5a` (red) | `#ff6b5a` (red) |
| `stopped` | `#888fa1` (gray) | `#5ea0ba` (blue-teal, no warning) |

**To add a new robot joint or change arm proportions:** modify the nested `<group>` / `<mesh>` hierarchy inside the `Robot` component.

### 10.3 Lighting & shadows

| Light | Three.js type | Position | Key props |
|---|---|---|---|
| Ambient | `ambientLight` | Global | intensity `1.12` |
| Hemisphere | `hemisphereLight` | Sky/ground | sky `#d8f0ff`, ground `#1c2b3d`, intensity `1.3` |
| Directional | `directionalLight` | `[4, 12, 6]` | intensity `3.3`, `castShadow`, shadow map `2048×2048` |
| Point (blue) | `pointLight` | `[−6, 6, −5]` | intensity `23`, color `#0f9aeb`, distance `20` |
| Point (orange) | `pointLight` | `[6, 5, 2]` | intensity `15`, color `#ffa953`, distance `18` |

`ContactShadows` at position `[0, 0.006, 0]` with `opacity=0.38`, `scale=20`, `blur=2.8`.

**To change the industrial color temperature:** adjust the two `pointLight` colors and the `hemisphereLight` sky/ground args.

### 10.4 Camera & controls

- **Canvas** — `dpr={[1, 1.65]}`, `shadows`, `antialias`, initial `camera={{ position:[12,12,15], fov:43, near:0.1, far:90 }}`
- **`OrbitControls`** — `enablePan=false`, `minDistance=10`, `maxDistance=28`, `maxPolarAngle=π/2.25`, `minPolarAngle=0.35`, `target=[0,1,0]`

**To change the default camera angle or zoom range:** update the `camera` prop on `<Canvas>` and the `minDistance`/`maxDistance` props on `<OrbitControls>`.

---

## 11. PlantMap — geography component

**File:** [`frontend/src/components/PlantMap.jsx`](../frontend/src/components/PlantMap.jsx)

**Props:**

| Prop | Type | Purpose |
|---|---|---|
| `sites` | array | All factory site objects from the snapshot |
| `selected` | string | Currently active site ID |
| `onSelect` | function | Callback `(siteId) => void` fired on marker click |

The component decides at render time which mode to use based on the `VITE_GOOGLE_MAPS_API_KEY` env variable:

### Google Maps mode

Activated when `import.meta.env.VITE_GOOGLE_MAPS_API_KEY` is defined. The Google Maps JS API is loaded dynamically via a `<script>` tag appended to `<head>`. A dark custom style array sets the map background to `#12283a` and hides roads and POIs.

Each site becomes a `google.maps.Marker` with a `SymbolPath.CIRCLE` icon:
- Selected site: `scale=12`
- Unselected: `scale=9`
- Color follows the same status palette as the SVG fallback

### SVG fallback mode

Used when no API key is configured (or if Maps fails to load).

Coordinate projection from geographic to SVG space:

```
bounds: lon [−125, −66], lat [24, 50]
svgX = 64 + (lng − lonMin) / (lonMax − lonMin) × 836
svgY = 55 + (latMax − lat) / (latMax − latMin) × 395
```

Each site marker is a group of two `<circle>` elements (outer ring with animated pulse on selected, inner fill dot) and a `<text>` label showing the site ID.

**Status colors:**

| Status | Hex |
|---|---|
| `healthy` | `#24d7b4` |
| `warning` | `#ff867a` |
| `idle` | `#9aabbc` |

A `.map-key` legend strip below the map shows all three states.

**To add a new factory site to the map:** add its entry to `PLANTS` in [`server/plants.py`](../server/plants.py) with a `lat`/`lng`. The map renders it automatically on the next snapshot.

---

## 12. AI context and MCP

### Rule-based demo context (`context.py`)

The `POST /api/context` endpoint calls [`server/context.py`](../server/context.py), which uses **regex keyword matching** on the user's question and returns a deterministic, transparently labeled response. It is **not** an LLM call or a Confluent RTCE query.

Pattern matching categories:

| Regex pattern | Response topic |
|---|---|
| `maintenance\|failure\|risk\|bearing\|critical` | Maintenance risk — lists robots above threshold |
| `quality\|reject\|yield` | Quality and yield — average quality score |
| `energy\|power\|consumption` | Energy — total modeled kW load |
| _(default)_ | Live operations briefing — OEE, throughput, robot count |

### Real Confluent RTCE MCP connector (`mcp.py`)

[`server/mcp.py`](../server/mcp.py) provides a real integration with Confluent **Real-Time Context Engine (RTCE)** via the **Model Context Protocol (MCP)** over a streamable-HTTP transport. It activates only when both `RTCE_MCP_ENDPOINT` and `RTCE_MCP_BASIC_TOKEN` are set.

The `with_mcp(operation)` helper:
1. Opens an async streamable-HTTP connection to the RTCE endpoint.
2. Initializes an MCP `ClientSession`.
3. Executes the provided `operation` lambda (either `list_tools` or `call_tool`).
4. Returns the result synchronously to the Flask route via `anyio.run()`.

Credentials never leave the server — the browser calls `/api/mcp/tools` and `/api/mcp/call`, not the RTCE endpoint directly.

---

## 13. Analytical path — Tableflow and Apache Iceberg

**Tableflow** is a Confluent Cloud feature that materializes governed Kafka topics as **Apache Iceberg** tables. In the Factory Pulse reference architecture:

1. Schema-bearing topics (`factory-iot-telemetry`, `factory-asset-state`, `factory-maintenance-events`) become Iceberg tables.
2. Iceberg tables land in object storage (S3 / GCS / ADLS) managed by Confluent or pointed to custom storage.
3. **IBM watsonx.data** connects to the Iceberg catalog for governed SQL analytical queries.

This path enables historical queries over all factory telemetry without a separate ETL pipeline.

---

## 14. Operations path — RTCE and MCP

**Real-Time Context Engine (RTCE)** materializes the latest value of each schema-bearing Kafka record as a queryable, low-latency context store. In this demo the `factory-asset-state` topic is the primary candidate (compacted, latest-state semantics).

RTCE exposes tools via **Model Context Protocol (MCP)** on a streamable-HTTP endpoint. AI agents (e.g., **IBM watsonx Orchestrate**) call these tools to read current robot state, site OEE, or active alerts without polling a database.

The MCP Tool Explorer panel in the `context` tab demonstrates this integration when configured.

---

## 15. Deployment modes

| Mode | How to enable | What is real |
|---|---|---|
| **Local simulation** | Default; no `.env` changes | Everything is synthetic in-process |
| **Kafka mode** | `STREAM_MODE=kafka` + all Kafka/Schema Registry env vars | Real Kafka messages, real schema subjects, real ACKs |
| **Flink mode** | Deploy SQL files to a Flink compute pool; set `KAFKA_CONSUME_DERIVED=true` | Actual Flink risk/KPI/quality output in the UI |
| **Tableflow** | Enable in Confluent Cloud Data Portal | Iceberg tables populate from live topics |
| **RTCE / MCP** | Configure `RTCE_MCP_ENDPOINT` + `RTCE_MCP_BASIC_TOKEN` | Real tool discovery and invocation |
| **Maintenance webhook** | Set `ACTION_WEBHOOK_URL` | Repair events dispatched to an external system |
| **Google Maps** | Set `VITE_GOOGLE_MAPS_API_KEY` | Interactive tile map instead of SVG |
| **Container** | `deploy/deploy-local.sh` (podman build + run) | Single-image deploy of compiled frontend + backend |

---

## 16. Glossary of all terms

| Term | Definition |
|---|---|
| **AGV** | Automated Guided Vehicle. A wheeled robot that transports parts along the factory floor. Modeled in the 3D scene as the `AGV` Three.js component. |
| **Alert** | A structured event emitted when a sensor crosses a threshold during a fault scenario. Severity is either `warning` or `critical`. |
| **Apache Flink** | A distributed stream-processing framework. Factory Pulse uses Confluent Cloud for Apache Flink to run SQL queries continuously over Kafka topics. |
| **Apache Iceberg** | An open table format for large analytical datasets. Used in the analytical path to provide SQL-queryable history from Kafka via Tableflow. |
| **Asset ID** | The unique identifier for a robot, e.g., `DET-R01`. Composed of site ID + role index. |
| **Bearing wear** | A fault scenario that increases vibration to simulate progressive mechanical degradation of a spindle bearing. |
| **batchId** | A production batch identifier in the telemetry record. Increments every 12 simulation ticks. |
| **Cobot** | Collaborative robot. An Assembly cobot in Factory Pulse works alongside humans on the production line. |
| **Compute pool** | A managed Flink resource in Confluent Cloud on which SQL statements run. Must be provisioned before deploying the Flink SQL files. |
| **ContactShadows** | A @react-three/drei utility that adds soft drop shadows beneath objects in the 3D scene without per-mesh shadow receivers. |
| **Confluent Schema Registry** | A central repository for Avro, JSON Schema, or Protobuf schemas. Factory Pulse registers JSON Schema for each Kafka topic subject before producing messages. |
| **Confluent Streamhouse** | IBM and Confluent's reference architecture for streaming data integration, comprising Kafka, Flink, Stream Governance, Tableflow, and RTCE. |
| **Derived topic** | A Kafka topic whose data is produced by a Flink SQL transformation rather than directly by the simulator (e.g., `factory-risk-signals`). |
| **Digital twin** | A continuously updated software model of a physical system. In Factory Pulse, each factory site has a digital twin maintained by the simulation loop. |
| **energyKw** | Instantaneous electrical power draw of a robot in kilowatts. Increases during thermal excursion and surge scenarios. |
| **Event** | A single record published to a Kafka topic. In this demo, events carry sensor readings, state snapshots, or maintenance alerts. |
| **EventSource** | The browser Web API used to receive Server-Sent Events from `/api/events`. |
| **Fault injection** | The deliberate introduction of an anomaly (bearing wear, thermal, quality drift, or surge) via the UI to demonstrate the detection and response pipeline. |
| **Flink Topic Action** | A Confluent Data Portal feature that applies built-in Flink transformations (deduplicate, mask, transform) to a topic without writing SQL. |
| **health** | A composite integer score (0–100) representing the overall condition of a robot asset. Degrades under fault scenarios. |
| **history** | A rolling 55-tick buffer of `{ t, output, oee, temp, vibration, quality }` per site, used to render the `MiniTrends` area charts. |
| **Intensity** | The severity parameter (0–100 %) of an injected fault scenario. Higher intensity causes larger signal deviations. |
| **IoT** | Internet of Things. Refers to the sensor-equipped industrial equipment whose readings are modeled by the simulation. |
| **JSON Schema** | A vocabulary for annotating and validating JSON documents. Used as the contract format for all Kafka topics in this demo. |
| **KafkaJS** | A JavaScript Kafka client library. The original Node.js implementation used KafkaJS; the Python rewrite uses `confluent_kafka`. |
| **lineId** | Identifies which production line a robot belongs to within a site. Values cycle as `LINE-1`, `LINE-2`, `LINE-3`. |
| **MCP (Model Context Protocol)** | An open protocol for connecting AI agents to live data tools. Confluent RTCE exposes factory context via MCP; the backend proxies calls via `mcp.py`. |
| **MES** | Manufacturing Execution System. A category of existing plant software (alongside SCADA and ERP) that Factory Pulse is conceptually augmenting, not replacing. |
| **mock mode** | The default operational mode when `STREAM_MODE` is not set to `kafka`. Events are queued in memory; no Confluent Cloud credentials are required. |
| **OEE** | Overall Equipment Effectiveness. A manufacturing KPI (target ≥ 95 %) that combines availability, performance, and quality. In this demo it is a smoothed computed value, not a real OEE measurement. |
| **OrbitControls** | A @react-three/drei control that lets users drag to orbit and scroll to zoom the 3D factory view. |
| **Partition** | A Kafka concept. Source topics are created with 3 partitions each in cloud mode. |
| **qualityScore** | The simulated first-pass yield percentage for a robot. Drops significantly during a quality drift scenario. |
| **React Three Fiber (R3F)** | A React renderer for Three.js. `<Canvas>` creates a WebGL context; components like `<mesh>` map to Three.js objects. |
| **Recharts** | A React charting library used for the area trend charts in the twin overview panels. |
| **rpm** | Revolutions Per Minute. The simulated motor speed of a robot's drive shaft. |
| **RTCE** | Confluent Real-Time Context Engine. Materializes the latest Kafka record per key as a queryable context store, exposed via MCP. |
| **SASL_SSL** | Security protocol used to authenticate the Confluent Kafka producer: SASL (Simple Authentication and Security Layer) over TLS/SSL. |
| **scenario** | One of five operation modes: `baseline`, `bearing`, `thermal`, `quality`, `surge`. Each modifies the sensor physics applied during the simulation step. |
| **Schema subject** | A named versioned schema registration in Schema Registry. Each topic has a `-key` subject and a `-value` subject. |
| **seed** | A per-site integer (0–5) used as a phase offset in sinusoidal noise functions to differentiate site signals. |
| **Severity** | Either the intensity of an injected scenario (0–100 %) or the level of a generated alert (`warning` / `critical`). |
| **siteId** | Two or three-character plant code (`DET`, `AUS`, `SEA`, `PHX`, `CLT`, `CHI`). |
| **Snapshot** | The full serialized state of the simulation at a given tick, broadcast to all SSE clients on every step. |
| **SSE (Server-Sent Events)** | A unidirectional HTTP streaming protocol used to push live factory state from the backend to the browser. |
| **status** | Per-robot state: `running` (nominal), `warning` (threshold exceeded), `stopped` (site paused). Per-site: `healthy`, `warning`, `idle`. |
| **Tableflow** | A Confluent Cloud feature that materializes Kafka topic records as Apache Iceberg tables stored in object storage. |
| **temperature** | Simulated surface/motor temperature of a robot asset in degrees Celsius. Rises sharply during a thermal excursion. |
| **Three.js** | A JavaScript 3D rendering library. React Three Fiber wraps it for use inside React components. |
| **throughput** | The number of units produced per minute by a factory site. |
| **tick** | A single simulation step. Increments on every `sim.step()` call, which fires every `SIM_INTERVAL_MS` milliseconds (default 1 700 ms). |
| **Tumbling window** | A Flink windowing pattern that groups events into fixed, non-overlapping intervals. Used in `03-shift-kpis.sql` with a 1-minute interval. |
| **useFrame** | A React Three Fiber hook that registers a callback executed on every animation frame. Used for robot kinematics and conveyor animation. |
| **vibration** | Simulated bearing/spindle vibration in millimetres per second. The primary signal for bearing wear detection. |
| **watsonx.data** | IBM's open lakehouse data platform. Connects to Iceberg tables produced by Tableflow for governed historical analytics. |
| **watsonx Orchestrate** | IBM's AI agent orchestration platform. A downstream consumer of RTCE MCP tools for automated factory operations. |
| **Webhook** | An optional HTTPS POST called by the backend when a maintenance action is triggered, dispatching the event to an external service desk or workflow system. |
| **Wire format** | The binary encoding applied to each Kafka message. Confluent's wire format prepends a magic byte and 4-byte schema ID before the JSON payload. |

---

*This document was generated from a full review of the Factory Pulse source code. All data, factory names, asset identifiers, and sensor readings are synthetic and intended for demonstration purposes only.*
