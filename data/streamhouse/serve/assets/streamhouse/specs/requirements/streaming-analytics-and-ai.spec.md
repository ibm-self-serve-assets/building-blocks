# Streaming Analytics and AI — Requirement Spec

## 1. Overview

This spec covers the Streamhouse data path and AI context layer of Factory Pulse: Kafka source topics and Schema Registry contracts, the Flink SQL derivation of risk/quality/shift-KPI/governed streams, governance, Tableflow → Iceberg → watsonx.data, Confluent RTCE exposed over MCP, the rule-based context Q&A, and the planned watsonx Orchestrate agent. Basis: `server/kafka.py`, `server/schemas.py`, `server/mcp.py`, `server/context.py`, `server/app.py`, `flink/*.sql`, `infra/terraform/**`, `docs/streamhouse-capabilities.md`, `docs/confluent-feature-matrix.md`, `docs/watsonx-orchestrate-agent-spec.md`.

**Topics.**

| Topic | Origin | Key | Notes |
|---|---|---|---|
| `factory-iot-telemetry` | Simulator | `{id: assetId}` | Per-robot sensor records, Tableflow source |
| `factory-asset-state` | Simulator (every 3rd tick, first 3 robots/site) | `{id: assetId}` | RTCE source (latest state) |
| `factory-maintenance-events` | Simulator (on alert) | `{id: eventId}` | Incidents |
| `factory-risk-signals` | Flink | derived | `BEARING_RISK`/`THERMAL_RISK`/`QUALITY_RISK`, severity `warning`/`critical` |
| `factory-shift-kpis` | Flink | derived | 1-minute tumbling window per site |
| `factory-quality-alerts` | Flink | derived | `QUARANTINE_BATCH` / `REQUEST_INSPECTION` |
| `factory-governed-telemetry` | Flink (Terraform) | derived | Masked telemetry for sharing |

Truthfulness constraints (from `docs/architecture.md`): the UI shows locally computed values unless derived/source consumption is enabled; Flink, Tableflow and RTCE are cloud-side and must not be implied to run when not provisioned.

## 2. Stakeholders

| Stakeholder | Interest |
|---|---|
| Solutions Architect / Demo Presenter | Credible, verifiable Streamhouse story with honest live/simulated labeling |
| Data / streaming engineer | Schema contracts, Flink recipes, topic definitions |
| Data governance owner | Schema compatibility, masking, lineage |
| Data & AI owner / AI agent developer | RTCE state + MCP tools; watsonx Orchestrate agent |
| Analytics / lakehouse engineer | Iceberg tables via Tableflow, watsonx.data integration |
| Maintenance Engineer / Plant Manager | Risk signals, quality decisions, grounded Q&A |
| Confluent Cloud account admin | Entitlements for Flink, Tableflow, RTCE; costs |

## 3. Functional Requirements

| ID | Priority | Requirement |
|---|---|---|
| FR-301 | Must | In `STREAM_MODE=kafka` the backend SHALL produce telemetry, asset-state and maintenance-event records to the three source topics using SASL_SSL/PLAIN with server-side credentials. |
| FR-302 | Must | Before producing, the backend SHALL register JSON Schema (Draft-07) key and value subjects named `<topic>-key` / `<topic>-value` in Schema Registry and SHALL cache the schema IDs. |
| FR-303 | Must | Key schema SHALL be `{id:string}`; value schemas SHALL be strict (`additionalProperties:false`) per topic as defined in `server/schemas.py`. |
| FR-304 | Must | The transport SHALL report `mode` (`kafka`/`mock`), `status` (`mock`, `configuration_required`, `connecting`, `connected`, `error`, `disconnected`), `sent`, `failed`, `lastError`, `lastAck`, `topics`, `derivedConnected`, `sourceConnected` via `/api/stream` and `/api/health`. |
| FR-305 | Must | With `STREAM_MODE=mock` or missing credentials the backend SHALL NOT attempt cloud connections and SHALL report `mock` / `configuration_required` with the missing variable names. |
| FR-306 | Should | On failure (`status` `error`/`disconnected`) in kafka mode the backend SHALL retry connection every 15 s and broadcast the updated `cloud` event. |
| FR-307 | Could | When `KAFKA_AUTO_CREATE_TOPICS=true` the backend MAY create missing source topics (3 partitions, replication 3). |
| FR-308 | Must | The repository SHALL provide deployable Flink SQL for: risk detection (vibration > 5.2 → `BEARING_RISK` critical if > 6.5; temperature > 72 → `THERMAL_RISK` critical if > 85; quality < 86 → `QUALITY_RISK` critical if < 80), quality routing (< 78 → `QUARANTINE_BATCH`, 78–86 → `REQUEST_INSPECTION`), 1-minute tumbling shift KPIs per `siteId` (`sampleCount`, `meanTemperature`, `meanVibration`, `meanQuality`, `energyKwhEstimate = SUM(energyKw)/60`) and a masked governed stream. |
| FR-309 | Should | With `KAFKA_CONSUME_DERIVED=true` the backend SHALL consume `KAFKA_RISK_TOPIC` (default `factory-risk-signals`) and `KAFKA_KPI_TOPIC` (default `factory-shift-kpis`), store the last record, and push it to clients as SSE `flink` events and `lastDerived`. |
| FR-310 | Should | With `KAFKA_CONSUME_SOURCE=true` or `POST /api/stream-mode {source:"kafka"}` the backend SHALL consume the source topics and merge them into the live snapshot; `source` MUST be `kafka` or `sim`, otherwise HTTP 400. |
| FR-311 | Must | Publish counters SHALL increase only for batches handed to the producer without error; errors SHALL set `status=error` and increment `failed`. |
| FR-312 | Should | The Terraform pipeline SHALL provision 4 continuous CTAS statements (risk, quality, shift KPIs, governed masking) on a Flink compute pool, plus 6 Schema Registry subjects, topic ACLs and credentials. |
| FR-313 | Should | Governance SHALL include contract enforcement via Schema Registry compatibility, a masked derived topic (`factory-governed-telemetry`) and lineage/Data Portal visibility in Confluent Cloud; Flink Topic Actions (dedupe/mask/transform) SHALL be explained distinctly from business actions and agent tool calls in the UI. |
| FR-314 | Should | Tableflow SHALL be configurable (Terraform default on) to materialize `factory-iot-telemetry` as managed Apache Iceberg for lakehouse engines (e.g. watsonx.data, Trino, Presto, DuckDB). |
| FR-315 | Should | RTCE SHALL be enabled (Terraform default on) on `factory-asset-state` and exposed through a streamable-HTTP MCP endpoint. |
| FR-316 | Must | `GET /api/mcp/tools` SHALL list tools (`name`, `description`, `inputSchema`) from the configured remote RTCE MCP and return `{connected:false,error}` with HTTP 503 when unconfigured/unreachable. |
| FR-317 | Must | `POST /api/mcp/call` SHALL validate `name` (string, ≤ 150 chars, `^[-_a-zA-Z0-9.]+$`), default non-dict/empty `args` to `{}`, call the tool and return `{source:"CONFLUENT RTCE MCP", result}`; errors return HTTP 502. |
| FR-318 | Must | The MCP endpoint SHALL be HTTPS only; credentials (`RTCE_MCP_ENDPOINT`, `RTCE_MCP_BASIC_TOKEN`) SHALL stay server-side and `/api/health.mcpConfigured` SHALL reflect whether both are set. |
| FR-319 | Must | `POST /api/context {siteId, question}` SHALL return a deterministic rule-based answer (`title`, `risk`, `answer`, `evidence[]`, `suggestion`) labeled `source:"LOCAL DEMO RULES — NOT MCP/LLM"`; unknown `siteId` → HTTP 400 "Unknown factory". |
| FR-320 | Must | Rule routing SHALL be: question matching `maintenance|failure|risk|bearing|critical` → maintenance assessment; `quality|reject|yield` → quality analysis; `energy|power|consumption` → energy; otherwise live operations briefing. |
| FR-321 | Should | The AI context / MCP view SHALL provide "Discover remote MCP tools", a tool selector with argument input and "Invoke tool", separate from the "Ask Factory Pulse" local Q&A panel. |
| FR-322 | Should | The Flink SQL view SHALL display the recipe source text and a derived-topic monitor of the latest Flink output (empty/clearly "not connected" when no derived data). |
| FR-323 | Could | The system MAY document optional Confluent AI functions (`AI_DETECT_ANOMALIES`) and streaming agents (`AI_RUN_AGENT`) as design templates only. |
| FR-324 | Could | A watsonx Orchestrate agent MAY be integrated per the draft spec: `POST /api/agent/chat` (`siteId`, `message`, `sessionId`) streaming SSE `token`/`done` events, five read-only MCP tools (`get_site_status`, `get_all_sites_summary`, `get_maintenance_alerts`, `get_robot_detail`, `get_flink_derived`) at `/api/mcp/factory-tools` protected by bearer `FACTORY_MCP_TOKEN`. |
| FR-325 | Should | If Orchestrate is not configured (`WATSONX_ORCHESTRATE_URL` absent) the agent endpoint SHALL fall back to local rule answers and the UI SHALL show a "LOCAL DEMO RULES" source badge. |
| FR-326 | Won't | The agent WILL NOT be allowed to execute control actions (inject, pause, maintenance) without a separate operator confirmation step; Confluent-side live provisioning is not claimed verified. |

## 4. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-301 | Schema compliance | 100% of produced messages use Confluent wire format (`0x00` + 4-byte schema ID + JSON) and validate against the registered schema; 0 schemaless writes. |
| NFR-302 | Throughput | Producer SHALL sustain the simulated load (~72 telemetry msgs/min total plus state/events) with `failed == 0` under healthy connectivity. |
| NFR-303 | Latency | Source → derived Flink record observable in `/api/stream.lastDerived` ≤ 10 s after publication when Flink statements are running (to be validated). |
| NFR-304 | Security | Kafka, Schema Registry, MCP and Orchestrate credentials appear in 0 HTTP responses, headers or logs; MCP endpoint must be `https://`. |
| NFR-305 | Resilience | Reconnect attempts every 15 s; derived/source decode errors are recorded in `lastError` without terminating the consumer loop. |
| NFR-306 | Honesty | Local Q&A latency ≤ 50 ms and always labeled local; MCP results labeled `CONFLUENT RTCE MCP`; no response from local rules is attributed to LLM/RTCE. |
| NFR-307 | Compatibility | Schema evolution follows Schema Registry backward/forward compatibility; subjects use TopicNameStrategy. |
| NFR-308 | Agent latency (draft) | Orchestrate responses with tool calls within 1–5 s expected; tool call timeout 10 s; UI shows loading for the full duration. |
| NFR-309 | Agent rate limit (draft) | ≤ 30 requests/min per `sessionId` on `/api/agent/chat`. |
| NFR-310 | Cost control | Flink compute pool bounded by `flink_max_cfu` (default 5). |
| NFR-311 | Cloud portability | Terraform default region `us-east-2` on AWS; RTCE requires supported region/entitlement. |

## 5. Acceptance Criteria

**FR-301**
- *Given* `STREAM_MODE=kafka` with valid Kafka credentials, *When* a tick completes, *Then* telemetry (and every 3rd tick asset-state; on alert, maintenance events) are produced and `stream.sent` increases.

**FR-302**
- *Given* a fresh Schema Registry, *When* the backend connects, *Then* six subjects `factory-iot-telemetry-key/-value`, `factory-asset-state-key/-value`, `factory-maintenance-events-key/-value` exist.

**FR-303**
- *Given* a value with an extra undeclared property, *When* validated against the registered schema, *Then* it is rejected (`additionalProperties:false`); *And* key `{id:"DET-R01"}` is accepted.

**FR-304**
- *Given* the server runs in mock mode, *When* `GET /api/stream` is called, *Then* `mode:"mock"`, `status:"mock"`, `sent:0`, `topics` lists the three source topics.

**FR-305**
- *Given* `STREAM_MODE=kafka` and `KAFKA_API_KEY` unset, *When* the server starts, *Then* `status:"configuration_required"` and `lastError` begins with "Missing:" and contains `KAFKA_API_KEY`; no network connection is made.

**FR-306**
- *Given* status `error` in kafka mode, *When* 15 s elapse, *Then* a reconnect is attempted and a `cloud` SSE event with the new status is broadcast.

**FR-307**
- *Given* `KAFKA_AUTO_CREATE_TOPICS=true` and topics absent, *When* connecting, *Then* the topics are created with 3 partitions; *And* existing topics do not abort connection.

**FR-308**
- *Given* a telemetry record vibration 7.0, *When* the risk CTAS runs, *Then* a `BEARING_RISK`, `critical` row appears in `factory-risk-signals`. *Given* quality 70, *Then* `factory-quality-alerts` contains `QUARANTINE_BATCH`; quality 82 → `REQUEST_INSPECTION`.
- *Given* 60 s of telemetry for a site, *When* the KPI window closes, *Then* one `factory-shift-kpis` row has `sampleCount`, means and `energyKwhEstimate = ΣenergyKw/60`.

**FR-309**
- *Given* `KAFKA_CONSUME_DERIVED=true` and Flink running, *When* a derived record arrives, *Then* `/api/stream.lastDerived` holds `{topic,value,timestamp}` and clients receive an SSE `flink` event.

**FR-310**
- *Given* `POST /api/stream-mode {"source":"banana"}`, *When* sent, *Then* HTTP 400 "source must be 'kafka' or 'sim'".
- *Given* Kafka connected and no source consumer, *When* `{"source":"kafka"}` is sent, *Then* the consumer starts and response contains `sourceConnected:true`.

**FR-311**
- *Given* a producer exception, *When* publish runs, *Then* `failed` increases by the batch size, `status:"error"`, `lastError` populated and the simulation loop continues.

**FR-312**
- *Given* `terraform apply` in an eligible account, *When* complete, *Then* four Flink statements, six schema subjects, topic ACLs and API keys exist (to be verified live).

**FR-313**
- *Given* the governed CTAS is running, *When* a consumer reads `factory-governed-telemetry`, *Then* sensitive batch identifiers are masked; *And* the Actions view labels Flink Topic Actions distinct from "Schedule maintenance".

**FR-314**
- *Given* Tableflow enabled, *When* telemetry flows, *Then* an Iceberg table for `factory-iot-telemetry` is queryable by an Iceberg-compatible engine; *And* README/docs state watsonx.data catalog linkage is a manual customer step.

**FR-315**
- *Given* RTCE enabled on `factory-asset-state`, *When* tools are listed through MCP, *Then* at least one table discovery/query tool is returned (environment dependent).

**FR-316**
- *Given* MCP not configured, *When* `GET /api/mcp/tools` is called, *Then* HTTP 503 with `connected:false` and error "RTCE MCP is not configured…".
- *Given* MCP configured, *Then* HTTP 200 with `connected:true` and `tools[]` containing `name`, `description`, `inputSchema`.

**FR-317**
- *Given* `{"name":"bad name!"}`, *When* posted to `/api/mcp/call`, *Then* HTTP 400 "Invalid MCP tool name".
- *Given* a valid tool name and `args` omitted, *When* posted, *Then* the tool is called with `{}` and response has `source:"CONFLUENT RTCE MCP"`.
- *Given* a remote failure, *Then* HTTP 502 with `error`.

**FR-318**
- *Given* `RTCE_MCP_ENDPOINT=http://…`, *When* a tool call is made, *Then* it fails with "RTCE MCP endpoint must be HTTPS."
- *Given* only the endpoint set, *When* `/api/health` is read, *Then* `mcpConfigured:false`.

**FR-319**
- *Given* DET with a bearing fault, *When* `POST /api/context {"siteId":"DET","question":"Which robot needs maintenance?"}` is sent, *Then* the response includes `source:"LOCAL DEMO RULES — NOT MCP/LLM"`, `risk:"Elevated"`, an answer naming a warning asset with vibration and temperature, and 3 evidence strings.
- *Given* `siteId:"XXX"`, *Then* HTTP 400 `{"error":"Unknown factory"}`.

**FR-320**
- *Given* the questions "any quality drift?", "energy usage?", "hello", *When* asked, *Then* titles are "Quality and yield analysis", "Energy and utilization", "Live operations briefing" respectively.
- *Given* no robot in warning and a maintenance question, *Then* risk is "Low" with "No currently simulated threshold breach".

**FR-321**
- *Given* MCP configured, *When* the user presses "Discover remote MCP tools" then selects and invokes a tool, *Then* the JSON result renders; *Given* MCP unconfigured, *Then* the panel shows the 503 error without breaking the page.

**FR-322**
- *Given* the Flink SQL view, *When* opened without derived consumption, *Then* the recipe SQL is shown and the output monitor indicates no actual derived data; *When* a `flink` SSE event arrives, *Then* the monitor shows it.

**FR-323**
- *Given* `docs/confluent-feature-matrix.md`, *When* reviewed, *Then* AI_DETECT_ANOMALIES and AI_RUN_AGENT are listed as design templates dependent on availability, not as shipped features.

**FR-324**
- *Given* the agent configured, *When* `POST /api/agent/chat` is sent with valid fields, *Then* an SSE stream emits `token` events followed by `done {source:"WATSONX ORCHESTRATE", sessionId, toolsUsed[]}`.
- *Given* a tool request without `Authorization: Bearer <FACTORY_MCP_TOKEN>`, *Then* HTTP 401.
- *Given* tool arg `siteId:"XXX"`, *Then* `{error:"Unknown siteId", valid:["DET","AUS","SEA","PHX","CLT","CHI"]}`.
- *Given* Kafka not connected, *When* `get_flink_derived` is called, *Then* `{available:false, reason}` and no HTTP error.

**FR-325**
- *Given* `WATSONX_ORCHESTRATE_URL` unset, *When* a message is sent, *Then* a JSON response with `source:"LOCAL DEMO RULES — NOT WATSONX ORCHESTRATE"` is returned and shown as a badge.

**FR-326**
- *Given* the agent tool list, *When* inspected, *Then* none expose inject/pause/maintenance operations.
- *Given* README and feature matrix, *When* read, *Then* they state Terraform/cloud provisioning was not live-verified.

## 6. Out of Scope

- Authoring or operating the customer's real MES/SCADA/ERP/Kafka Connect source connectors.
- Automatic watsonx.data ↔ Iceberg catalog configuration.
- Maximo/ServiceNow work-order mapping and approval flows (only the generic HTTPS webhook).
- Real LLM reasoning in the local context panel (explicitly rule-based).
- Training or hosting ML models; production deployment of `AI_DETECT_ANOMALIES` / streaming agents.
- Guaranteeing Confluent entitlements/region availability for Flink, Tableflow, RTCE.
- Long-term retention policy and cost optimization of Kafka/Iceberg storage.

## 7. Open Questions

| # | Question | Owner |
|---|---|---|
| 1 | `flink/` file names (`02-risk-signal.sql`, `03-shift-kpis.sql`, `04-quality-alerts.sql`) differ from Terraform CTAS (`02-risk-ctas.sql`, `03-quality-ctas.sql`, `04-shift-kpis-ctas.sql`, `05-governed-topic-ctas.sql`); which are authoritative? | Streaming engineer / TBD |
| 2 | Producer relies on `produce()` + `poll(0)` without delivery callbacks, yet `sent` is described as "counted after acknowledgements" — align counter semantics. | Backend dev / TBD |
| 3 | Is the producer actually serializing with the registered schema ID (wire format) — current code registers schemas and produces JSON strings; verify and document. | Backend dev / TBD |
| 4 | Orchestrate deployment type, SSE streaming support and session memory (draft spec Q1, Q4, Q5). | Developer / TBD |
| 5 | Is the RTCE MCP endpoint available in the demo environment, and should Orchestrate register both MCP servers? | Demo team / TBD |
| 6 | Acceptable agent latency and whether operator-confirmed control actions should ever be exposed. | Product / UX / TBD |
| 7 | Quantitative end-to-end latency target (NFR-303) needs live measurement. | QA / TBD |
