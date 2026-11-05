# Factory Pulse Streamhouse — Product Overview — Requirement Spec

> Numbering convention across the requirement set: `FR-1xx/NFR-1xx` = this document, `FR-2xx/NFR-2xx` = [`live-monitoring-and-simulation.spec.md`](live-monitoring-and-simulation.spec.md), `FR-3xx/NFR-3xx` = [`streaming-analytics-and-ai.spec.md`](streaming-analytics-and-ai.spec.md), `FR-4xx/NFR-4xx` = [`deployment-and-operations.spec.md`](deployment-and-operations.spec.md).
> Priority tags use MoSCoW: **Must / Should / Could / Won't**. Statements are reverse-engineered from `README.md`, `docs/*.md`, `server/app.py`, `server/context.py`, `frontend/src/App.jsx` and `frontend/src/components/Login.jsx`.

## 1. Overview

**Factory Pulse** is a full-stack manufacturing showcase for the IBM **Streamhouse** building blocks on Confluent Cloud: **Stream → Transform → Govern → Serve**, plus open Iceberg analytics delivery and current-state AI context. It is a *demonstration/reference*, not a production plant-control system.

- A Python Flask backend (`server/`) simulates **6 fictional US plants, 36 modeled robots** (6 roles per plant) and emits synthetic telemetry continuously.
- A React 18 + IBM Carbon frontend (`frontend/`) provides a "control tower" with seven views: *Command center, Digital twin, Streamhouse, Flink SQL, Actions, AI context / MCP, Demo playbook*.
- In **simulation mode** (default, `STREAM_MODE=mock`) everything works with no credentials. In **Kafka mode** (`STREAM_MODE=kafka`) every tick publishes Schema-Registry-encoded events to Confluent Cloud; Flink SQL, Tableflow/Iceberg and RTCE/MCP are optional cloud-side extensions.
- All data is synthetic; the product must be honest about which capabilities are live vs. simulated (a recurring product principle: *"truth in demos"*).

**Product vision.** Show a manufacturing executive that a robot event is not another silo but a *governed asset signal* that is simultaneously usable by operators (live UI), analysts (Iceberg), and AI agents (RTCE/MCP) — with no rip-and-replace of existing MES/SCADA/ERP.

### 1.1 Personas

| Persona | Description | Primary goals | Key views |
|---|---|---|---|
| **Plant Manager** (e.g. fictional "Maya Chen, VP Operations of six US plants") | Owns throughput/OEE across plants; needs one current operational picture | See OEE, throughput, health, active alerts per plant; decide pause/resume; acknowledge alerts | Command center, Digital twin, Actions |
| **Maintenance Engineer** | Responsible for asset condition at one plant | Detect bearing/thermal/quality drift early; inspect sensor trends per robot; dispatch (simulated) maintenance; ask "which robot needs maintenance?" | Digital twin, Actions, AI context |
| **Solutions Architect / Demo Presenter** | Delivers the 15-minute "The machine that warned us first" story to CIO/COO/architects | Inject faults on demand, trace event through Streamhouse layers, prove what is live vs. simulated, deploy/destroy cloud stack | Streamhouse, Flink SQL, AI context / MCP, Demo playbook, deploy scripts |

### 1.2 End-to-end user journey

1. **Sign in** (demo gate) → **Command center** shows six plants, OEE, health and events/sec.
2. **Select a plant** (site picker or clickable plant map) → open **Digital twin** (animated 3D six-station floor).
3. **Inject a fault** (bearing / thermal / quality / surge, severity slider) → sensors drift, robot turns red, OEE/output fall, an alert appears within a few ticks.
4. **Trace the event** through **Streamhouse** (Capture → Stream → Transform → Govern → Serve); in cloud mode verify `stream.sent` increases at `/api/health`; read **Flink SQL** recipes and any derived output.
5. **Ask for context** in **AI context / MCP**: local rule-based answer (explicitly labeled) and, when configured, discover/call real Confluent RTCE MCP tools.
6. **Respond** in **Actions**: acknowledge alerts, pause/resume the line, "Schedule maintenance / Simulate repair" (optional HTTPS webhook), observe recovery.
7. **Close**: Tableflow→Iceberg→watsonx.data story; optionally `destroy` billable cloud resources.

### 1.3 Success criteria

| ID | Criterion | Measure |
|---|---|---|
| SC-1 | Zero-credential first run | App usable after `cp .env.example .env; npm install; npm run dev` with no cloud accounts |
| SC-2 | Fault-to-visibility latency | Injected fault visible in UI snapshot ≤ 2 simulation ticks (≤ 3.4 s at default 1700 ms) |
| SC-3 | Honest labeling | 100% of non-live answers/maps/data carry an explicit source/mode label |
| SC-4 | Cloud proof | In Kafka mode, `/api/health.stream.status == "connected"` and `sent` strictly increasing |
| SC-5 | Full demo script | A presenter can complete Acts 1–4 of `docs/demo-script.md` in ≤ 15 minutes |
| SC-6 | Clean teardown | `python scripts/deploy.py destroy` removes billable Confluent resources after typed confirmation |

### 1.4 Requirement groups

| Group | Summary | Detailed spec |
|---|---|---|
| G1 Product framing & honesty | Demo-only positioning, synthetic data, source labeling, access gate | this document |
| G2 Live monitoring & simulation | Telemetry, faults, actions, SSE, twin, map | live-monitoring-and-simulation.spec.md |
| G3 Streaming analytics & AI | Kafka, Flink, governance, Tableflow, RTCE/MCP, context Q&A, Orchestrate agent | streaming-analytics-and-ai.spec.md |
| G4 Deployment & operations | Local/Docker/Code Engine/Terraform, config, security, observability, backup | deployment-and-operations.spec.md |

## 2. Stakeholders

| Stakeholder | Role | Interest / Concern |
|---|---|---|
| Plant Manager (persona) | End user | Cross-plant operational picture, OEE, safe actions |
| Maintenance Engineer (persona) | End user | Early fault detection, evidence-based answers |
| Solutions Architect / Demo Presenter (persona) | Primary operator of the product | Reliable demo, honest claims, quick deploy/teardown |
| Customer CIO/COO, reliability leads, data/AI owners | Audience | Business outcome: avoid unplanned stoppage without replacing systems |
| IBM / Confluent field teams | Sponsor | Showcase of Streamhouse capabilities |
| Platform/DevOps engineer | Deployer | Reproducible local/container/cloud deployment, secret handling |
| Security reviewer | Governance | Backend ships without auth; must not be exposed publicly |
| Maintainer/developer | Builder | Traceability from requirement to design/test |

## 3. Functional Requirements

| ID | Priority | Requirement |
|---|---|---|
| FR-101 | Must | The product SHALL present itself as a technical demonstration using synthetic data, and SHALL NOT claim connection to real plant equipment, PLCs or safety controllers. |
| FR-102 | Must | The product SHALL work end-to-end in a no-credential **simulation mode** with 6 plants (DET, AUS, SEA, PHX, CLT, CHI) and 36 robots. |
| FR-103 | Must | The product SHALL provide seven navigable views: Command center, Digital twin, Streamhouse, Flink SQL, Actions, AI context / MCP, Demo playbook. |
| FR-104 | Must | Every non-live data source or answer (local rules, SVG map fallback, simulated actions, browser-side simulation) SHALL carry a visible label identifying its source/mode. |
| FR-105 | Must | The frontend SHALL gate access behind a client-side demo sign-in (default user `admin`, overridable via `VITE_DEMO_USER`/`VITE_DEMO_PASS`), persisting the session in `sessionStorage` key `fp-session`. |
| FR-106 | Should | The product SHALL support an optional Kafka mode in which live Confluent Cloud transport status is observable in the UI and via `/api/health`. |
| FR-107 | Should | The product SHALL embed a demo playbook (the four-act story) and a Streamhouse architecture walkthrough in the UI. |
| FR-108 | Should | The product SHALL include the documentation set (README, architecture, capabilities, feature matrix, demo script, digital-twin guide) describing real vs. simulated behaviour. |
| FR-109 | Could | The product MAY provide a downloadable/visible Flink SQL source viewer for each deployable recipe. |
| FR-110 | Won't | The product WILL NOT provide production-grade authentication/RBAC, multi-tenancy, or actuation of physical equipment in this release. |

## 4. Non-Functional Requirements

| ID | Category | Requirement (measurable) |
|---|---|---|
| NFR-101 | Usability | A new user reaches the Command center in ≤ 2 minutes from cloning the repo (2 documented commands + `npm install`). |
| NFR-102 | Performance | Default simulation tick interval is 1700 ms (`SIM_INTERVAL_MS`), floor 500 ms; UI updates on each tick without full-page reload. |
| NFR-103 | Honesty / Compliance | All README/UI claims about Kafka, Flink, Tableflow, RTCE are conditional on observable state (e.g. `stream.status`, `mcpConfigured`); 0 unconditional "live" claims in simulation mode. |
| NFR-104 | Security | Cloud credentials appear in 0 browser-delivered bundles or API responses; `VITE_`-prefixed variables contain no secrets. |
| NFR-105 | Compatibility | Runs on Node.js 20+ and Python 3.11+; 3D view requires a WebGL-capable modern browser. |
| NFR-106 | Maintainability | Each requirement group maps to ≥ 1 design spec section (see §8 traceability). |
| NFR-107 | Accessibility | UI built on IBM Carbon components; form controls have associated labels (e.g. scenario selector `label for="scenario"`). |

## 5. Acceptance Criteria

**FR-101**
- *Given* any view of the application, *When* the user reads the login footer, Streamhouse/Demo views or README, *Then* the data is described as "synthetic" and no control path to physical equipment exists.

**FR-102**
- *Given* a fresh clone with `.env` copied from `.env.example` (`STREAM_MODE=mock`), *When* the user runs `npm run dev` and opens http://localhost:5173, *Then* six plants and 36 robots show live changing values without any cloud account.
- *Given* the backend is unreachable, *When* the frontend loads (and `VITE_LOCAL_SIM` is not `false`), *Then* it switches to the browser simulation and remains usable.

**FR-103**
- *Given* a signed-in user, *When* they click each sidebar item, *Then* the seven views (`overview, twin, architecture, flink, actions, context, story`) render with their labels exactly as listed.

**FR-104**
- *Given* the user asks a question in AI context, *When* the backend answers locally, *Then* the response shows `source: "LOCAL DEMO RULES — NOT MCP/LLM"`.
- *Given* no Google Maps key is configured, *When* the plant map renders, *Then* it is labeled as an illustrative offline SVG map.

**FR-105**
- *Given* the login page, *When* the user submits empty fields, *Then* the message "Enter your username and password." appears and no session is stored.
- *Given* wrong credentials, *When* submitted, *Then* "Invalid username or password." is shown and `fp-session` is not set.
- *Given* correct credentials, *When* submitted, *Then* `sessionStorage['fp-session']` equals the username and the app shell is shown; closing the tab clears it.

**FR-106**
- *Given* `STREAM_MODE=kafka` with valid secrets, *When* the server starts, *Then* `/api/health.stream.status` becomes `connected` and `stream.sent` increases each tick.
- *Given* `STREAM_MODE=kafka` with missing secrets, *When* the server starts, *Then* status is `configuration_required` and `lastError` lists the missing variable names.

**FR-107**
- *Given* the Demo playbook and Streamhouse views, *When* opened, *Then* they present the Capture→Stream→Transform→Govern→Serve flow and the four demo acts.

**FR-108**
- *Given* the repository, *When* a reviewer opens `docs/`, *Then* architecture, capabilities, feature matrix, demo script and digital-twin documents exist and state which components are simulated.

**FR-109**
- *Given* the Flink SQL view, *When* the user opens a recipe, *Then* the SQL source text from `flink/*.sql` is displayed.

**FR-110**
- *Given* the security section of `docs/architecture.md`, *When* a shared deployment is planned, *Then* the documented guidance states the backend has no authentication and must not be publicly exposed.

## 6. Out of Scope

- Real plant, PLC, SCADA or safety-critical control; connection to physical robots.
- Production-grade identity (OIDC), RBAC, audit trails, rate limiting, CSRF (documented as prerequisites for shared environments, not delivered).
- Real MES/SCADA/ERP connectors (conceptual extension points only).
- Automatic watsonx.data catalog wiring, Maximo/ServiceNow work-order mapping.
- Live-verified Terraform/Confluent provisioning claims (not executed in the authoring environment).
- Multi-user persistence, historical database inside the app.

## 7. Open Questions

| # | Question | Owner |
|---|---|---|
| 1 | Should the client-side demo credential gate be replaced by server-side auth before any shared deployment (Code Engine)? | Security reviewer / TBD |
| 2 | The README says "Python Flask"; some docs (`docs/architecture.md`) and tests still reference earlier Node/Express heritage — confirm canonical runtime story. | Maintainer / TBD |
| 3 | Which frontend directory is canonical (`frontend/` vs. `frontend_1/` present at repo root)? | Maintainer / TBD |
| 4 | Is the watsonx Orchestrate agent (draft in `docs/watsonx-orchestrate-agent-spec.md`) in release scope? Its routes are not in `server/app.py`. | Product / TBD |
| 5 | Target audience size/performance for concurrent SSE clients in shared demos. | Demo team / TBD |

## 8. Glossary

| Term | Definition |
|---|---|
| **Streamhouse** | IBM architecture unifying streaming (Kafka/Flink), governance and lakehouse/AI serving into one governed backbone: Stream → Transform → Govern → Serve. |
| **OEE** | Overall Equipment Effectiveness. In this product a per-plant percentage smoothed each tick as `oee = oee×0.67 + target×0.33`, reduced by active fault severity. |
| **Throughput** | Units per minute per plant; derived from lines × rate × OEE; zero when paused/tripped. |
| **Digital twin** | Animated 3D representation of a plant floor driven by simulated sensor state; not connected to physical assets. |
| **Scenario** | Injected operating condition: `baseline`, `bearing`, `thermal`, `quality`, `surge`. |
| **SSE** | Server-Sent Events; one-way server push over HTTP at `/api/events` (events: snapshot, alert, scenario, action, cloud, flink). |
| **Kafka / Confluent Cloud** | Event streaming platform hosting the three source and several derived topics. |
| **Schema Registry / Wire format** | Confluent service storing JSON Schema (Draft-07); messages are encoded as magic byte `0x00` + 4-byte schema ID + payload. |
| **Flink SQL / CTAS** | Confluent-managed stream processing; `CREATE TABLE AS SELECT` jobs produce risk, KPI, quality and governed topics. |
| **Topic Actions** | Confluent Flink ready-made transforms (deduplicate, mask, transform); distinct from business actions and agent tool calls. |
| **Tableflow** | Confluent feature materializing Kafka topics as Apache **Iceberg** tables in object storage (zero-ETL). |
| **Iceberg / watsonx.data** | Open table format / IBM lakehouse that can query Iceberg tables when integrated. |
| **RTCE** | Confluent **Real-Time Context Engine**; materializes latest state (here from `factory-asset-state`) for low-latency AI context. |
| **MCP** | **Model Context Protocol**; RTCE exposes tools over streamable HTTP; backend proxies `/api/mcp/tools` and `/api/mcp/call`. |
| **watsonx Orchestrate** | IBM agent platform; planned (draft spec) to answer questions via factory MCP tools. |
| **AGV** | Automated Guided Vehicle (wheeled cart in the 3D scene and robot role R05). |
| **Protective stop** | Simulated line trip (`stopped`) when bearing/thermal severity ≥ 60%. |
| **Code Engine** | IBM Cloud serverless container service used by `deploy/deploy-ce.sh`. |

## 9. Traceability to Design Specs

| Requirement group / IDs | Design spec | API spec |
|---|---|---|
| G1 — FR-101..110, NFR-101..107 | [`specs/design/frontend-ui.design.md`](../design/frontend-ui.design.md) (Login, shell, tabs) · [`specs/design/backend-server.design.md`](../design/backend-server.design.md) | [`factory-pulse.openapi.yaml`](../api/factory-pulse.openapi.yaml) `/api/health`, `/api/bootstrap` |
| G2 — FR-201..FR-2xx (telemetry, faults, actions, SSE, twin, map) | [`digital-twin-simulation.design.md`](../design/digital-twin-simulation.design.md) · [`frontend-ui.design.md`](../design/frontend-ui.design.md) · [`backend-server.design.md`](../design/backend-server.design.md) | `/api/events`, `/api/simulate`, `/api/control`, `/api/bootstrap` |
| G3 — FR-301..FR-3xx (Kafka, Flink, governance, Tableflow, RTCE/MCP, context, Orchestrate) | [`streaming-platform.design.md`](../design/streaming-platform.design.md) · [`backend-server.design.md`](../design/backend-server.design.md) · [`watsonx-orchestrate-agent.design.md`](../design/watsonx-orchestrate-agent.design.md) | `/api/stream`, `/api/stream-mode`, `/api/context`, `/api/mcp/tools`, `/api/mcp/call` |
| G4 — FR-401..FR-4xx (local run, Docker, Code Engine, Terraform, backup, config, security, observability) | [`deployment-ops.design.md`](../design/deployment-ops.design.md) · [`streaming-platform.design.md`](../design/streaming-platform.design.md) | `/api/health` |

> Note: `deployment-ops.design.md` and `watsonx-orchestrate-agent.design.md` were not yet present when this table was authored; links are the agreed target filenames.
