# Live Monitoring and Simulation — Requirement Spec

## 1. Overview

This spec covers the operational core of Factory Pulse: synthetic telemetry for 6 plants / 36 robots, fault-scenario injection, operator actions, real-time delivery to the browser via Server-Sent Events (SSE), the 3D digital-twin view, and the plant map. Behaviour is derived from `server/simulation.py`, `server/plants.py`, `server/app.py`, `frontend/src/App.jsx`, `frontend/src/sim/api.js` and `docs/digital-twin-explained.md`.

Key facts from the implementation:
- Plants: `DET` Detroit Assembly, `AUS` Austin Gigafactory, `SEA` Seattle Precision, `PHX` Phoenix Semicon, `CLT` Charlotte Manufacturing, `CHI` Chicago Distribution. Each models 6 robot roles (Welding robot, Pick & place, Quality scanner, Assembly cobot, AGV transporter, Packaging arm); asset ID format `{SITE}-R0{N}`.
- Signals per robot per tick: `temperature`, `vibration`, `rpm`, `energyKw`, `qualityScore`, `health`, `status`.
- Warning thresholds: temperature > 72 °C, vibration > 5.2 mm/s, quality < 86 %.
- Scenarios: `baseline`, `bearing`, `thermal`, `quality`, `surge`; severity 1–100 % (UI slider 20–100).
- Tick interval default 1700 ms (`SIM_INTERVAL_MS`, minimum 500 ms).
- Actions: `pause`, `resume`, `maintenance`, `acknowledge`.

## 2. Stakeholders

| Stakeholder | Interest |
|---|---|
| Plant Manager | Cross-plant OEE/throughput/health, acknowledge alerts, pause/resume lines |
| Maintenance Engineer | Per-robot sensor trends, early fault detection, simulated repair |
| Solutions Architect / Demo Presenter | Deterministic, controllable fault injection and reliable live updates |
| Frontend developer | Stable SSE/REST contract, offline fallback behaviour |
| Backend developer | Simulation engine correctness, bounded memory |

## 3. Functional Requirements

| ID | Priority | Requirement |
|---|---|---|
| FR-201 | Must | The system SHALL simulate six plants (DET, AUS, SEA, PHX, CLT, CHI) with 6 robots each, exposing site metadata (name, city, state, lat/lng, type, lines, region) via `/api/bootstrap`. |
| FR-202 | Must | On every tick the system SHALL compute per robot: `temperature`, `vibration`, `rpm`, `energyKw`, `qualityScore`, `health`, `status` (`running`/`warning`/`stopped`). |
| FR-203 | Must | A robot SHALL be `warning` when temperature > 72 °C, or vibration > 5.2 mm/s, or quality < 86 %. |
| FR-204 | Must | The system SHALL compute per-plant `oee` (smoothed each tick) and `throughput` (units/min) and keep a rolling per-plant history of the last 55 points. |
| FR-205 | Must | `POST /api/simulate` SHALL accept `{siteId, scenario, intensity}`, apply scenario `baseline|bearing|thermal|quality|surge` with intensity clamped to 1–100 (default 75), clear any pause, and reject unknown site/scenario with HTTP 400. |
| FR-206 | Must | Injecting `baseline` SHALL clear any protective stop and restore healthy operation. |
| FR-207 | Must | Active scenario effects SHALL be: bearing → vibration ↑, health ↓, OEE ↓; thermal → temperature ↑, energy ↑, OEE ↓; quality → quality score ↓, OEE ↓; surge → throughput/rpm/energy ↑. |
| FR-208 | Must | While a non-baseline scenario with severity ≥ 35 % is active and the line is running, the system SHALL emit a maintenance alert every 5th tick with type `BEARING_RISK`/`OVERHEAT`/`QUALITY_DRIFT`/`CAPACITY_PRESSURE` and severity `critical` if intensity ≥ 70 else `warning`. |
| FR-209 | Should | For bearing/thermal scenarios at severity ≥ 60 % when a robot is in warning, the system SHALL trip a protective line stop (`stopped=true`), zeroing rpm and dropping energy to standby, until maintenance, resume, or baseline. |
| FR-210 | Must | `POST /api/control` SHALL accept `{siteId, action, robotId?}` with `action ∈ {pause, resume, maintenance, acknowledge}`; reject others with HTTP 400. |
| FR-211 | Must | `pause` SHALL hold the line (status `idle`, throughput 0); `resume` SHALL clear pause/stop and reset scenario to baseline; `maintenance` SHALL reset scenario to baseline, clear pause/stop and set robot health to 99; `acknowledge` SHALL mark all alerts of that site acknowledged. |
| FR-212 | Should | When `ACTION_WEBHOOK_URL` is set and action is `maintenance`, the system SHALL POST the action result as JSON to the HTTPS webhook (optional bearer from `ACTION_WEBHOOK_TOKEN`, 8 s timeout) and set `webhookDispatched=true`; non-HTTPS URLs SHALL be rejected. |
| FR-213 | Must | The system SHALL record each action (id `ACT-<ms>`, timestamp, siteId, action, robotId, `mode:"simulation"`), keeping the last 50, and alerts (last 45). |
| FR-214 | Must | `GET /api/events` SHALL stream SSE with events `snapshot` (sent immediately on connect and every tick), `alert`, `scenario`, `action`, `cloud`, `flink`, plus a `: heartbeat` comment every 18 s of idleness. |
| FR-215 | Must | `GET /api/bootstrap` SHALL return the initial snapshot, scenario catalogue, plant list, cloud status, MCP-configured flag and last derived record. |
| FR-216 | Must | The snapshot SHALL include per-site `status` (`healthy`/`warning`/`idle`), `oee`, `throughput`, `robots`, `history`, unacknowledged `alerts` (top 25), `actions` (top 20) and aggregate totals (including active alert count). |
| FR-217 | Must | The frontend SHALL keep working when the backend is unreachable by switching to the browser-side simulation (`sim/localBackend.js`), unless `VITE_LOCAL_SIM=false`; `VITE_LOCAL_SIM=true` SHALL force it. |
| FR-218 | Must | The **Command center** SHALL display, for all plants, OEE, health, events/second, throughput and active alerts, with a site picker to select a plant. |
| FR-219 | Must | The **Digital twin** view SHALL render an animated 3D six-station floor (robotic arms, conveyor, AGV) for the selected plant, colour robots by status (red on warning/fault), and reflect pause/trip state. |
| FR-220 | Must | The Digital twin side panel SHALL provide scenario selector, severity slider (20–100 %), "Inject scenario"/"Restore healthy state" button, "Pause/Resume line" and "Simulate repair" controls, and a live sensor list per robot. |
| FR-221 | Should | The **plant map** SHALL show six clickable plant markers; it SHALL use Google Maps JS when a browser key is configured, otherwise an offline labeled SVG fallback; clicking a marker SHALL select that plant. |
| FR-222 | Should | The system SHALL provide an Actions view with an event feed of recent alerts and actions and buttons for acknowledge, pause/resume and maintenance. |
| FR-223 | Should | In Kafka source mode (`POST /api/stream-mode {source:"kafka"}`) incoming telemetry/state/maintenance messages SHALL be merged into the live snapshot (alert IDs de-duplicated) and broadcast to clients. |
| FR-224 | Could | The UI MAY show a mode badge indicating UI-SIM vs. Kafka-sourced data and fallback state. |
| FR-225 | Won't | The system WILL NOT drive any real equipment; "maintenance" remains a simulated business action. |

## 4. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-201 | Performance | Server tick interval = `max(0.5 s, SIM_INTERVAL_MS)` (default 1.7 s); snapshot broadcast p95 latency from tick to client ≤ 250 ms on localhost. |
| NFR-202 | Scalability | Supports ≥ 20 concurrent SSE clients on a single instance with CPU ≤ 1 vCPU and memory ≤ 2 GB (Code Engine sizing). |
| NFR-203 | Reliability | A failure in one tick (e.g. publish error) SHALL NOT stop the simulation loop; the loop continues on the next interval. |
| NFR-204 | Resource bounds | In-memory alerts ≤ 45, actions ≤ 50, per-site history ≤ 55 points; memory use does not grow unbounded over 24 h. |
| NFR-205 | Latency | Fault injection visible in UI ≤ 2 ticks (≤ 3.4 s default); alert visible ≤ 5 ticks (≤ 8.5 s) for severity ≥ 35 %. |
| NFR-206 | Resilience | SSE clients reconnect automatically (EventSource); dead client queues are removed on failed enqueue/close. |
| NFR-207 | Rendering | 3D twin sustains ≥ 30 fps on a mid-range laptop with WebGL; disposes scene resources on unmount. |
| NFR-208 | Determinism | Simulation noise is deterministic per tick/site seed so tests can assert ranges (`tests/simulation.test.js`). |
| NFR-209 | Security | Webhook URL MUST be HTTPS; token never returned to browser; control endpoints are unauthenticated and documented as not for public exposure. |
| NFR-210 | Accessibility | Controls use labelled inputs and non-colour status text (status component shows text, not colour alone). |

## 5. Acceptance Criteria

**FR-201**
- *Given* the server is running, *When* a client calls `GET /api/bootstrap`, *Then* `plants` contains exactly 6 entries with ids DET, AUS, SEA, PHX, CLT, CHI and each snapshot site has 6 robots with IDs matching `^[A-Z]{3}-R0[1-6]$`.

**FR-202**
- *Given* a baseline site, *When* one tick elapses, *Then* every robot has numeric temperature, vibration, rpm, energyKw, qualityScore, integer health 15–100 and a status from the allowed set.

**FR-203**
- *Given* a robot with vibration 6.0 mm/s, *When* the snapshot is built, *Then* its status is `warning` (likewise for temperature 73 °C or quality 85 %).

**FR-204**
- *Given* 60 ticks have elapsed, *When* the snapshot is read, *Then* each site `history` has ≤ 55 points and `oee`, `throughput` are numeric.

**FR-205**
- *Given* `POST /api/simulate {"siteId":"DET","scenario":"bearing","intensity":85}`, *When* sent, *Then* response is `{ok:true,result:{siteId:"DET",scenario:"bearing",intensity:85}}` and a `scenario` SSE event is broadcast.
- *Given* `{"siteId":"XXX","scenario":"bearing"}` or `{"siteId":"DET","scenario":"fire"}`, *When* sent, *Then* HTTP 400 with an `error` message ("Unknown factory" / "Invalid scenario").
- *Given* intensity 500, *When* sent, *Then* stored intensity is 100.

**FR-206**
- *Given* DET is protective-stopped, *When* `baseline` is injected, *Then* `stopped` clears and subsequent ticks show running robots and recovering OEE.

**FR-207**
- *Given* bearing at 85 % on DET, *When* 3 ticks pass, *Then* robot DET-R02 vibration exceeds 5.2 mm/s and DET OEE is lower than before injection.
- *Given* thermal at 85 %, *When* 3 ticks pass, *Then* a robot's temperature exceeds 72 °C and energyKw increases.
- *Given* quality at 85 %, *When* ticks pass, *Then* a robot's qualityScore falls below 86 %.
- *Given* surge at 85 %, *When* ticks pass, *Then* site throughput exceeds the baseline throughput.

**FR-208**
- *Given* bearing at 85 % on a running line, *When* the tick counter reaches a multiple of 5, *Then* an alert of type `BEARING_RISK`, severity `critical` is added and an `alert` SSE event is sent.
- *Given* intensity 30 %, *When* ticks pass, *Then* no alert is emitted. *Given* intensity 50 %, *Then* alerts have severity `warning`.

**FR-209**
- *Given* bearing at 60 % or higher with a robot in warning, *When* the tick evaluates, *Then* the site `stopped` is true, rpm is 0 for robots and site status is `warning`.
- *Given* the stopped line, *When* `maintenance` is sent, *Then* `stopped` is false.

**FR-210**
- *Given* `POST /api/control {"siteId":"DET","action":"explode"}`, *When* sent, *Then* HTTP 400 with `error:"Invalid action"`.
- *Given* a valid pause request, *When* sent, *Then* HTTP 200 `{ok:true,result:{...,mode:"simulation"}}`.

**FR-211**
- *Given* DET running, *When* `pause` is sent, *Then* snapshot shows `paused:true`, status `idle`, throughput 0.
- *Given* DET with bearing active, *When* `maintenance` is sent, *Then* scenario is `baseline`, `paused` and `stopped` are false and robot health is 99.
- *Given* 3 unacknowledged DET alerts, *When* `acknowledge` is sent, *Then* the DET snapshot alert list is empty and other sites' alerts are unchanged.

**FR-212**
- *Given* `ACTION_WEBHOOK_URL=https://example/hook`, *When* `maintenance` is sent and the hook returns 200, *Then* the response result has `webhookDispatched:true`.
- *Given* `ACTION_WEBHOOK_URL=http://…`, *When* `maintenance` is sent, *Then* HTTP 400 "Action webhook URL must be HTTPS" and the note states the local simulation may already have changed.

**FR-213**
- *Given* 60 actions were issued, *When* actions are read, *Then* at most 50 are retained, newest first, each with an `ACT-` id and `mode:"simulation"`.

**FR-214**
- *Given* a client opens `/api/events`, *When* connected, *Then* the first message is `event: snapshot`; *and* when idle for 18 s a `: heartbeat` comment is received; *and* the response header is `Cache-Control: no-cache, no-transform`.

**FR-215**
- *Given* `GET /api/bootstrap`, *When* called, *Then* the JSON includes `snapshot`, `scenarios` (5), `plants` (6), `cloud`, `mcpConfigured`, `lastDerived`.

**FR-216**
- *Given* a site with `paused:true`, *When* the snapshot is read, *Then* status is `idle`; *Given* any robot in warning or `stopped`, *Then* status is `warning`; otherwise `healthy`.

**FR-217**
- *Given* the backend is down and `VITE_LOCAL_SIM` is unset, *When* the first API call fails to connect, *Then* the UI continues with the browser simulation and logs a console message; *and* when the backend returns, the UI switches back to remote mode.
- *Given* `VITE_LOCAL_SIM=false` and backend down, *When* the app loads, *Then* the real error is shown and no silent fallback occurs.

**FR-218**
- *Given* the Command center, *When* loaded, *Then* six plant cards with OEE and status are visible and selecting one updates the global selected-site context for all views.

**FR-219**
- *Given* DET selected and bearing active, *When* the Digital twin opens, *Then* the faulted robot appears red and the AGV/conveyor animation halts when the line is paused or tripped.

**FR-220**
- *Given* the scenario "Bearing wear" and severity 85 %, *When* the user clicks "Inject scenario", *Then* a `/api/simulate` request is sent with `intensity:85` and the button is disabled while busy.
- *Given* scenario "Healthy operations" selected, *When* viewed, *Then* the button reads "Restore healthy state".
- *Given* the line is paused, *When* viewed, *Then* the control reads "Resume line".

**FR-221**
- *Given* no Google Maps key, *When* the map renders, *Then* the offline SVG map with six labelled markers is shown and clicking Detroit selects DET.
- *Given* a restricted key configured, *When* the map renders, *Then* Google Maps loads with the six markers.

**FR-222**
- *Given* alerts and actions exist, *When* the Actions view opens, *Then* the event feed lists them newest first and each button triggers its `/api/control` action for the selected site.

**FR-223**
- *Given* Kafka connected and source mode set to kafka, *When* a `factory-maintenance-events` message with an already-known `eventId` arrives, *Then* no duplicate alert is added.
- *Given* a telemetry message for DET-R01 arrives, *When* merged, *Then* the robot's fields update and a `snapshot` event is broadcast.

**FR-224**
- *Given* source mode `kafka` but Kafka not connected, *When* ticks run, *Then* snapshots still broadcast directly and the UI badge reflects the fallback state.

**FR-225**
- *Given* any control action, *When* executed, *Then* the recorded `mode` is `simulation` and no outbound call occurs except the opt-in webhook.

## 6. Out of Scope

- Physical sensor ingestion, OPC-UA/MQTT gateways, real MES/SCADA integration.
- Persistent storage of telemetry history beyond in-memory rolling buffers (long-term history is the Iceberg path, see streaming spec).
- Per-robot targeted fault injection (faults apply per plant; `robotId` is recorded but not used to isolate effects).
- User-level authorization of control actions.
- Multi-plant simultaneous scenario scripting/scheduling.
- Mobile-optimized layouts.

## 7. Open Questions

| # | Question | Owner |
|---|---|---|
| 1 | `docs/digital-twin-explained.md` states alert types for thermal as `OVERHEAT` while Flink emits `THERMAL_RISK`; should event vocabularies be harmonized? | Backend dev / TBD |
| 2 | Event/second figure on Command center — computed client-side or server-side? Define authoritative source. | Frontend dev / TBD |
| 3 | The browser simulation (`localBackend.js`) and server simulation may diverge numerically; what tolerance is acceptable? | Maintainer / TBD |
| 4 | Should `acknowledge` support per-alert IDs rather than whole-site acknowledgement? | Product / TBD |
| 5 | Thermal-fault Flink classification thresholds (>72 / >85) vs. simulation severity mapping — verify end-to-end with tests. | QA / TBD |
