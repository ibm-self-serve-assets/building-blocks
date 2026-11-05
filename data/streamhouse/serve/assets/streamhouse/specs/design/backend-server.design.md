# Factory Pulse Streamhouse — Backend Server Design

| Item | Value |
|---|---|
| Scope | `server/app.py`, `server/kafka.py`, `server/plants.py`, `server/simulation.py`, `server/schemas.py`, `server/context.py`, `server/mcp.py`, `deploy/requirements.txt`, `.env.example` |
| Runtime | Python 3.11 (Docker `python:3.11-slim`), Flask >= 3.0 < 4.0, single process, multi-threaded |
| Status | Reverse-engineered from source (as-built). Observed defects and ambiguities are flagged as **[NOTE]** and collected in section 10 |
| Source of truth | The code. Where this document and code differ, the code wins |

---

## 1. Problem Statement

Factory Pulse is a demo "Streamhouse" digital-twin for a fictional six-plant US manufacturing network. A browser dashboard needs:

1. A **live, believable stream of industrial telemetry** (temperature, vibration, RPM, energy, quality, health, OEE, throughput) for 6 plants × 6 robotic assets, with injectable faults (bearing wear, thermal excursion, quality drift, demand surge) and operator actions (pause, resume, maintenance, acknowledge).
2. A **real Confluent Cloud data path** as an *optional* mode: publish the simulated events to Kafka topics governed by Schema Registry, let Confluent Flink SQL derive risk signals / shift KPIs, and consume those derived topics (and optionally the source topics themselves) back into the UI.
3. An **optional Confluent RTCE MCP** (Real-Time Context Engine, Model Context Protocol) passthrough with server-side credentials, plus a deterministic local "context" answerer used when MCP is not configured.
4. A **single deployable process** that also serves the compiled frontend (`frontend/dist`).

The backend is a Python/Flask rewrite of an earlier Node/Express server (legacy references to `server/src/*.js` still exist in `tests/`; see section 9).

The system must run with **zero cloud credentials** (`STREAM_MODE=mock`) and degrade gracefully when any cloud dependency is absent or fails.

---

## 2. Goals & Non-Goals

### Goals
- G1. Deterministic-shaped, stochastic-noise simulation of 6 plants, ticking at a configurable interval (default 1.7 s).
- G2. Push-based UI updates via Server-Sent Events (SSE) with a single multiplexed stream.
- G3. Optional schema-governed publishing to three Kafka topics on Confluent Cloud (SASL_SSL/PLAIN) with Schema Registry subject registration (`<topic>-key`, `<topic>-value`, JSON Schema).
- G4. Optional consumption of Flink-derived topics (`factory-risk-signals`, `factory-shift-kpis`) and of source topics ("Kafka source mode") to drive the UI from a real round-trip.
- G5. Runtime toggle between "sim" and "kafka" source modes (`POST /api/stream-mode`) with automatic fallback to direct sim→SSE when Kafka is not connected.
- G6. Server-side-only secrets (Kafka, Schema Registry, MCP, webhook).
- G7. Optional HTTPS webhook dispatch when a maintenance action is triggered.
- G8. Serve the SPA bundle from the same origin.

### Non-Goals
- No persistence: all state (sites, alerts, actions, counters) is in process memory and resets on restart.
- No authentication/authorization on the HTTP API (CORS is wide open). See section 10.
- No multi-worker / horizontal scaling (simulation state and SSE client set are process-local).
- No LLM: `/api/context` is rule-based and explicitly labelled "LOCAL DEMO RULES — NOT MCP/LLM".
- Producer does not use the Confluent Schema Registry wire format (see 4.2 / section 10) and does not validate payloads against the registered JSON Schemas.
- No real device/PLC integration; all robot data is synthetic.
- The backend does **not** compute risk scores itself; risk scoring is performed in Flink SQL (`flink/02-risk-signal.sql`) and merely forwarded.

---

## 3. Architecture Overview

```mermaid
flowchart LR
    subgraph Browser
        UI[React SPA<br/>frontend/dist]
    end

    subgraph Server["Flask process: server/app.py (port PORT)"]
        direction TB
        API["HTTP routes<br/>/api/*"]
        SSE["SSE hub<br/>_clients: set of queue.Queue"]
        PUB["Publisher thread<br/>_publisher_loop every SIM_INTERVAL_MS"]
        RETRY["Reconnect thread<br/>every 15 s"]
        SIM["FactorySimulation<br/>simulation.py"]
        PL["PLANTS / SCENARIOS<br/>plants.py"]
        CTX["demo_answer<br/>context.py"]
        MCPM["with_mcp<br/>mcp.py"]
        KT["ConfluentTransport<br/>kafka.py"]
        SCH["VALUE_SCHEMAS / KEY_SCHEMA<br/>schemas.py"]
        CD["derived consumer thread"]
        CS["source consumer thread"]
    end

    subgraph Confluent["Confluent Cloud"]
        K[(Kafka cluster)]
        SR[Schema Registry]
        F[Flink SQL statements]
        RTCE[RTCE MCP endpoint]
    end

    WH[External HTTPS webhook]

    UI -- "GET /api/bootstrap, POST /api/*" --> API
    UI <-- "GET /api/events (SSE)" --> SSE
    API --> SIM
    API --> CTX
    API --> MCPM
    API -- "maintenance only" --> WH
    PUB -- "step()" --> SIM
    SIM --> PL
    SIM -- "emit(snapshot/alert/scenario/action)" --> SSE
    PUB -- "publish(batch)" --> KT
    KT --> SCH
    KT -- "produce JSON" --> K
    KT -- "register subjects" --> SR
    K -- "iot-telemetry, asset-state, maintenance-events" --> F
    F -- "factory-risk-signals, factory-shift-kpis" --> K
    K --> CD --> KT
    K --> CS --> KT
    KT -- "on_derived: SSE flink" --> SSE
    KT -- "on_source: merge into sim + SSE snapshot/alert" --> SIM
    RETRY --> KT
    MCPM -- "streamable HTTP + Basic auth" --> RTCE
```

### Process / threading model
| Thread | Created in | Lifetime | Purpose |
|---|---|---|---|
| Main / Flask worker threads (`threaded=True`) | `app.run` | process | HTTP handlers; one thread blocked per open SSE connection |
| `_publisher_loop` | `_startup()` | daemon | sim tick → Kafka publish → SSE `cloud` event |
| `retry` | `_startup()` | daemon | every 15 s reconnect if `mode=="kafka"` and status in (`error`,`disconnected`) |
| derived `poll_loop` | `ConfluentTransport._connect_derived` | daemon, runs while `self.consumer is not None` | Flink output topics |
| source `poll_loop` | `ConfluentTransport._connect_source` | daemon, runs while `self.source_consumer is not None` | source topics |

There are **no locks**. The simulation dict, `_clients`, alerts, and transport counters are mutated across threads relying on the GIL. See section 10.

### Module dependency graph
`app.py` → `context`, `kafka`, `mcp`, `plants`, `simulation`; `kafka.py` → `schemas` (lazy import inside `_value_schemas()` / `_key_schema()`); `simulation.py` → `plants`. `schemas.py`, `plants.py`, `context.py` have no intra-project dependencies.

**Import path assumption:** the code uses flat imports (`from context import ...`). It must be started as `python server/app.py` (so `server/` is `sys.path[0]`) — the Dockerfile does exactly this (`CMD ["python", "server/app.py"]`).

---

## 4. Component Design

### 4.1 `server/app.py` — HTTP API, SSE hub, orchestration

**Responsibility:** create the Flask app; wire simulation ↔ transport ↔ SSE; hold runtime source-mode flag; run publisher and reconnect threads; serve static frontend.

#### Module-level state
| Name | Type | Initial | Notes |
|---|---|---|---|
| `app` | `Flask` | `static_folder = <server>/../frontend/dist`, `static_url_path="/"` | `JSONIFY_PRETTYPRINT_REGULAR=False`, `JSON_SORT_KEYS=False` set (**[NOTE]** the latter is ignored by Flask >= 2.3/3.0; the provider's `app.json.sort_keys` defaults to `True`, so JSON object keys are emitted alphabetically) |
| `CORS(app)` | flask-cors | all origins, all routes | |
| `sim` | `FactorySimulation` | new | |
| `cloud` | `ConfluentTransport` | new | reads `os.environ` |
| `_clients` | `set[queue.Queue]` | empty | one unbounded queue per SSE connection |
| `_last_derived` | `dict \| None` | `None` | last `{topic,value,timestamp}` from a Flink topic |
| `_source_mode` | `bool` | `os.environ.get("KAFKA_CONSUME_SOURCE") == "true"` | runtime-togglable |
| `_shutdown` | `threading.Event` | unset | stops publisher + retry threads |

`load_dotenv()` is called **before** importing project modules so they see `.env`.

#### Helper functions
| Signature | Behavior |
|---|---|
| `now_iso() -> str` | `datetime.now(timezone.utc).isoformat()` |
| `broadcast(event: str, data: Any) -> None` | Formats `f"event: {event}\ndata: {json.dumps(data)}\n\n"`; `put_nowait` to every queue in `list(_clients)`; queues raising are discarded (queues are unbounded so in practice never raise) |
| `_on_derived(value: dict) -> None` | sets `_last_derived = value`; `broadcast("flink", value)`. Value shape: `{"topic": str, "value": dict\|None, "timestamp": iso}` |
| `_on_source(msg: dict) -> None` | See merge algorithm below |
| `_cloud_info() -> dict` | `cloud.info()` + `lastDerived` + `sourceMode` (`"kafka"` if `_source_mode` else `"sim"`) |
| `_publisher_loop(stop: Event, interval: float) -> None` | See 7.5 |
| `_startup() -> None` | See 7.1 |
| `_shutdown_server() -> None` | `_shutdown.set(); cloud.disconnect()` (only invoked from the `__main__` `finally`) |
| `create_app() -> Flask` | returns `app` (note: `_startup()` already ran at import time) |

Wiring performed at import: `sim.subscribe(lambda event, data: broadcast(event, data))` — every simulation `emit` (`snapshot`, `alert`, `scenario`, `action`) is forwarded verbatim as an SSE event; `cloud.on_derived = _on_derived`; `cloud.on_source = _on_source`; then `_startup()` runs (starts threads) on import.

#### `_on_source(msg)` merge algorithm
Input `msg = {"topic": str, "value": dict, "timestamp": iso}`. No-op if `_source_mode` is false. Entire body wrapped in `try/except Exception → print("Source merge error:", exc)`.

- **Topic `factory-iot-telemetry` or `factory-asset-state`** (literal strings, *not* the env-configurable topic names — **[NOTE]**: if `KAFKA_TELEMETRY_TOPIC`/`KAFKA_STATE_TOPIC` are overridden the merge silently ignores them):
  1. Require `siteId` and `assetId`; else return.
  2. Look up `sim.sites[siteId]`; return if unknown.
  3. Find the robot with `id == assetId`; for each key present in `value`, overwrite: `temperature→temperature`, `vibration→vibration`, `rpm→rpm`, `energyKw→energyKw`, `qualityScore→quality`, `health→health`, `status→status`.
  4. If `"scenario" in value`: `site_state["scenario"] = value["scenario"]` (**not** validated against known scenarios; also does not alter `intensity`).
  5. `broadcast("snapshot", sim.snapshot())`.
- **Topic `factory-maintenance-events`**: build alert
  `{id: value.eventId or "KFK-<ms epoch>", timestamp: value.timestamp or now, siteId: value.siteId or "", siteName: value.siteId or "", assetId: value.assetId or "", type: value.eventType or "UNKNOWN", severity: value.severity or "warning", message: value.message or "Event from Kafka", acknowledged: value.acknowledged or False}`. If no existing `sim.alerts` item has the same `id`: `sim.alerts.insert(0, alert)`; truncate to 45; `broadcast("alert", alert)`; `broadcast("snapshot", sim.snapshot())`. Because the simulation's own alerts use the same id as `eventId`, round-tripped self-generated alerts are de-duplicated; only externally produced events add new alerts. (`siteName` is set to siteId, not the plant name — externally injected alerts show the id.)
- Any other topic: ignored.

#### HTTP API
All JSON. Error shape `{"error": str}` unless noted.

| Method & Path | Request body | Success response | Errors |
|---|---|---|---|
| `GET /api/health` | – | `{ok:true, server:"Factory Pulse", time, stream: cloud.info(), mcpConfigured: bool(RTCE_MCP_ENDPOINT and RTCE_MCP_BASIC_TOKEN), googleMapsConfigured: bool(VITE_GOOGLE_MAPS_API_KEY)}` | none; used by Docker HEALTHCHECK |
| `GET /api/bootstrap` | – | `{snapshot, scenarios: SCENARIOS, plants: PLANTS, cloud: _cloud_info(), mcpConfigured, lastDerived}` | – |
| `GET /api/events` | – | SSE (`text/event-stream`), headers `Cache-Control: no-cache, no-transform`, `Connection: keep-alive`. First frame is `event: snapshot` with the current snapshot, then queue messages; if none for 18 s emits comment `: heartbeat\n\n` | – |
| `POST /api/simulate` | `{siteId: str, scenario: str, intensity?: number=75}` | `{ok:true, result:{siteId, scenario, intensity}}` | 400 `{error}` for unknown site / invalid scenario / non-numeric intensity |
| `POST /api/control` | `{siteId, action, robotId?}` | `{ok:true, result: <action record>}`; if `ACTION_WEBHOOK_URL` set and `action=="maintenance"`, result gains `webhookDispatched:true` | 400 `{error, note:"The local simulation may already have changed; external workflow failed."}` on any exception (including webhook failure — local state change is **not** rolled back) |
| `POST /api/context` | `{siteId, question?}` | `{source:"LOCAL DEMO RULES — NOT MCP/LLM", title, risk, answer, evidence[], suggestion}` | 400 `{error:"Unknown factory"}` |
| `GET /api/mcp/tools` | – | `{connected:true, tools:[{name, description, inputSchema}]}` | 503 `{connected:false, error}` (also when MCP not configured) |
| `POST /api/mcp/call` | `{name: str, args?: object}` | `{source:"CONFLUENT RTCE MCP", result}` | 400 `{error:"Invalid MCP tool name"}` if `name` not str, > 150 chars, or not matching `^[-_a-zA-Z0-9.]+$`; 502 `{error}` otherwise. `args` coerced to `{}` unless a non-empty dict |
| `POST /api/stream-mode` | `{source: "kafka"\|"sim"}` | `{ok:true, sourceMode, sourceConnected: bool(cloud.source_consumer)}` | 400 if `source` invalid |
| `GET /api/stream` | – | `{...cloud.info(), lastDerived, sourceMode}` | – |
| `GET /` and `GET /<path>` (`serve_static`) | – | static file from `frontend/dist`, else `index.html` (SPA fallback) | `path` starting `api/` → 404 `{error:"Not found"}`; no build → 404 `{error:"Frontend not built. Run \`npm run build\` first."}` |

`POST /api/control` webhook algorithm: if `ACTION_WEBHOOK_URL` set **and** action == `maintenance`: must start with `https://` else `ValueError("Action webhook URL must be HTTPS")`; POST `json.dumps(result)` (the action record) with `Content-Type: application/json` and optional `Authorization: Bearer <ACTION_WEBHOOK_TOKEN>`; timeout 8 s via `urllib.request`; status >= 400 → `ValueError`. (urllib raises `HTTPError` for 4xx/5xx before that check anyway.)

`POST /api/stream-mode` algorithm: set `_source_mode`; if switching to kafka **and** `cloud.status == "connected"` **and** `cloud.source_consumer is None`, call `cloud._connect_source()` (errors printed, not raised); broadcast `cloud` SSE event with `_cloud_info()`. Switching back to `sim` does **not** stop the source consumer; `_on_source` simply ignores messages.

**SSE event catalogue** (all emitted from this module's `broadcast`):

| Event | Data | Producer |
|---|---|---|
| `snapshot` | full snapshot (5.5) | sim tick (unless suppressed), `_on_source`, publisher fallback, initial frame |
| `alert` | alert object (5.4) | `sim.step` for generated alerts; `_on_source` for new external alerts |
| `scenario` | `{siteId, scenario, intensity}` | `sim.inject` |
| `action` | action record (5.6) | `sim.act` |
| `flink` | `{topic, value, timestamp}` | `_on_derived` |
| `cloud` | `_cloud_info()` every tick; `cloud.info()` (without lastDerived/sourceMode) after a successful reconnect attempt; `_cloud_info()` after stream-mode change | publisher/retry/stream-mode |

**Error handling:** every route wraps in try/except returning JSON errors (see table); publisher loop catches everything and prints `Publish error:`; static fallback returns 404 JSON.

**Startup/entry:** `python server/app.py` → `app.run(host="0.0.0.0", port=int(PORT or 4000), threaded=True)`; `finally: _shutdown_server()`.

---

### 4.2 `server/kafka.py` — `ConfluentTransport`

**Responsibility:** optional Confluent Cloud connectivity: producer, Schema Registry subject registration, topic creation, derived-topic consumer, source-topic consumer, connection status/metrics. In mock mode it is a no-op that reports `status="mock"`.

#### Class `ConfluentTransport(env: Mapping[str,str] | None = None)`
Attributes:

| Attribute | Type | Initial | Meaning |
|---|---|---|---|
| `env` | mapping | `os.environ` | injectable for tests |
| `mode` | `"kafka"\|"mock"` | `"kafka"` iff `env["STREAM_MODE"]=="kafka"` | fixed at construction |
| `status` | str | `"disconnected"` | one of `disconnected`, `mock`, `configuration_required`, `connecting`, `connected`, `error` |
| `sent`, `failed` | int | 0 | message counters (enqueue-based) |
| `last_error` | `str\|None` | None | |
| `last_ack` | `str\|None` | None | ISO time of last successful enqueue (not broker ack) |
| `producer` | `confluent_kafka.Producer\|None` | None | |
| `registry` | `SchemaRegistryClient\|None` | None | |
| `ids` | `dict[str, {"key": int, "value": int}]` | `{}` | registered schema ids per topic. **Note:** `register_schema` returns an `int` id |
| `consumer` | `Consumer\|None` | None | derived consumer |
| `source_consumer` | `Consumer\|None` | None | |
| `on_derived`, `on_source` | callables or None | None | set by app |

Methods:

| Signature | Behavior |
|---|---|
| `info() -> dict` | `{mode, status, sent, failed, lastError, lastAck, topics: list(VALUE_SCHEMAS.keys()), derivedConnected: consumer is not None, sourceConnected: source_consumer is not None}` |
| `connect() -> None` | Algorithm below |
| `_connect_derived() -> None` | Creates consumer, subscribes, starts poll thread |
| `_connect_source() -> None` | Creates consumer, subscribes, starts poll thread |
| `publish(batch: list[dict]) -> None` | Algorithm below |
| `disconnect() -> None` | Closes consumers (swallow errors), `producer.flush(5)`, nulls `consumer/source_consumer/producer`; if status was `connected` → `disconnected` |

Helpers: `now() -> str` (UTC ISO), `_value_schemas()`, `_key_schema()` (lazy imports from `schemas`). `import json` is at the **bottom** of the module (works because uses are at call time).

#### `connect()` algorithm
1. `mode != "kafka"` → `status="mock"`; return.
2. Mandatory env: `KAFKA_BOOTSTRAP_SERVERS, KAFKA_API_KEY, KAFKA_API_SECRET, SCHEMA_REGISTRY_URL, SCHEMA_REGISTRY_API_KEY, SCHEMA_REGISTRY_API_SECRET`. Any missing/empty → `status="configuration_required"`, `last_error="Missing: A, B"`; return.
3. Import `confluent_kafka.Producer`, `confluent_kafka.schema_registry.{SchemaRegistryClient, Schema}`; failure → `status="configuration_required"`, `last_error="confluent_kafka not installed: <exc>"`; return.
4. `status="connecting"`; in a try block:
   - Client conf `{bootstrap.servers, security.protocol: "SASL_SSL", sasl.mechanism: "PLAIN", sasl.username: KAFKA_API_KEY, sasl.password: KAFKA_API_SECRET}`; `producer = Producer(conf)`.
   - `registry = SchemaRegistryClient({"url": SCHEMA_REGISTRY_URL, "basic.auth.user.info": "<SR_KEY>:<SR_SECRET>"})`.
   - If `KAFKA_AUTO_CREATE_TOPICS == "true"`: `AdminClient(conf).create_topics([NewTopic(t, num_partitions=3, replication_factor=3) for t in VALUE_SCHEMAS])`; each future's result awaited; per-topic exceptions (e.g. already exists) swallowed.
   - For each topic in `VALUE_SCHEMAS`: `registry.register_schema(f"{topic}-key", Schema(json.dumps(KEY_SCHEMA), "JSON"))` and `registry.register_schema(f"{topic}-value", Schema(json.dumps(schema), "JSON"))`; store ids in `self.ids[topic] = {"key": id, "value": id}`.
   - `status="connected"`, `last_error=None`.
   - If `KAFKA_CONSUME_DERIVED == "true"` → `_connect_derived()`; if `KAFKA_CONSUME_SOURCE == "true"` → `_connect_source()`.
   - On any exception: `status="error"`, `last_error=str(exc)`, `disconnect()` (note `disconnect()` only downgrades `connected`, so status stays `error`).

#### `_connect_derived()`
- Consumer conf: producer conf + `group.id = f"factory-pulse-output-{int(time.time()*1000)}"` (unique per connect → every instance reads independently, no committed-offset continuity), `auto.offset.reset="latest"`. (Kafka default `enable.auto.commit=true` applies.)
- Topics: `[KAFKA_RISK_TOPIC or "factory-risk-signals", KAFKA_KPI_TOPIC or "factory-shift-kpis"]`.
- Poll loop (`while self.consumer is not None`): `poll(1.0)`; `None` or `msg.error()` → continue; else `value = json.loads(msg.value().decode("utf-8")) if msg.value() else None`; call `on_derived({"topic": msg.topic(), "value": value, "timestamp": now()})`; decode/handler exceptions → `last_error = f"Decode {topic}: {exc}"`.
- `JSONDeserializer` is imported but unused → payloads must be plain JSON (no Schema Registry magic byte).

#### `_connect_source()`
- Same conf, `group.id = f"factory-pulse-source-{int(time.time()*1000)}"`, `auto.offset.reset="latest"`.
- Topics: `[KAFKA_TELEMETRY_TOPIC or "factory-iot-telemetry", KAFKA_STATE_TOPIC or "factory-asset-state", KAFKA_EVENTS_TOPIC or "factory-maintenance-events"]`.
- Poll loop identical but only invokes `on_source({"topic","value","timestamp"})` when the decoded value is truthy; error text prefix `Source decode <topic>: ...`.
- Requires `self.env["KAFKA_BOOTSTRAP_SERVERS"]` etc. to exist (raises `KeyError` if called when not configured; callers guard with `status == "connected"`).

#### `publish(batch)`
1. Return immediately unless `status == "connected"`, `producer` exists and `batch` non-empty.
2. Group items whose topic is in `self.ids` (unknown topics skipped); for each: `key = json.dumps(item["key"])` (e.g. `'{"id": "DET-R01"}'`), `value = json.dumps(item["value"])`; `producer.produce(topic, key=key, value=value)` (strings; no partitioner override, no headers, no delivery callback, no explicit timestamp — a `timestamp` string is built but unused).
3. `producer.poll(0)`; `sent += len(batch)` (counts the whole batch even if some items were skipped); `last_ack = now()`; `last_error = None`.
4. Exception (e.g. `BufferError` queue full): `failed += len(batch)`, `status="error"`, `last_error=str(exc)`. The 15 s reconnect loop later calls `connect()`.

**Wire format (important):** keys and values are **plain UTF-8 JSON strings**. The Schema Registry client is used only to register subjects; ids are stored but never embedded. There is no Confluent magic byte/schema-id prefix and no client-side validation.

**Error handling summary:** configuration problems → `configuration_required` (not retried); runtime failures → `error` (retried every 15 s); decode failures recorded in `last_error`, never raised.

---

### 4.3 `server/plants.py` — static reference data
Pure data module: `PLANTS`, `ROBOT_TYPES`, `SCENARIOS` (values in section 5.1–5.3). No functions. Note the comment: sites are fictional but placed at real US city coordinates.

---

### 4.4 `server/simulation.py` — `FactorySimulation`

**Responsibility:** in-memory physics-ish model of all plants; scenario injection; operator actions; per-tick telemetry/state/event batch generation; snapshot composition; listener (pub-sub) notification.

#### Module helpers
| Signature | Definition |
|---|---|
| `clamp(n, a, b)` | `max(a, min(b, n))` |
| `r(x, d=1)` | `round(float(x), d)` (Python banker's rounding on halves) |
| `now()` | UTC ISO-8601 string with microseconds and `+00:00` |

#### Class `FactorySimulation(random: Callable[[], float] | None = None)`
`random` defaults to `random.random` (uniform [0,1)). Tests inject `lambda: 0.5` (zero noise).

State: `tick:int=0`, `paused:bool=False` (global; never set to True by any code path, `step()` returns `[]` if it were), `sites: dict[siteId, site]` (5.2), `events: list[dict]`, `alerts: list[dict]`, `actions: list[dict]`, `listeners: set[Callable[[str, Any], None]]`, `last_batch: list[dict]`, `suppress_broadcast: bool=False`.

| Method | Signature | Behavior |
|---|---|---|
| `subscribe` | `(fn) -> unsubscribe_callable` | add listener |
| `emit` | `(event: str, payload) -> None` | call each listener (copy of set); exceptions from listeners **propagate** |
| `inject` | `(site_id, scenario, intensity=75) -> dict` | validate site (`ValueError("Unknown factory")`) and scenario ∈ {baseline,bearing,thermal,quality,surge} (`ValueError("Invalid scenario")`); `intensity = clamp(float(intensity) if intensity is not None else 75, 1, 100)`; set `scenario`, `intensity`, `paused=False`; if baseline also `stopped=False`; `emit("scenario", {...})`; return `{siteId, scenario, intensity}` |
| `act` | `(site_id, action, robot_id=None) -> dict` | validate site and action ∈ {pause,resume,maintenance,acknowledge} (`ValueError("Invalid action")`). `pause`: `paused=True`. `resume`: `paused=False, stopped=False, scenario="baseline"`. `maintenance`: `scenario="baseline", paused=False, stopped=False`, every robot `health=99`. `acknowledge`: all alerts of that site `acknowledged=True`. Record `{id:"ACT-<ms epoch>", timestamp, siteId, action, robotId, mode:"simulation"}`; prepend to `actions`, cap 50; `emit("action", record)`. `intensity` is left unchanged by resume/maintenance |
| `step` | `() -> list[dict]` | Advance one tick (algorithm 4.4.1); returns the Kafka-style batch |
| `snapshot` | `() -> dict` | Compose read model (4.4.2) |

#### 4.4.1 `step()` algorithm (per tick, per plant `p`, site state `s`)
```
tick += 1
severity = 0 if scenario == "baseline" else intensity/100          # 0.01 .. 1.0
mod      = {baseline:0, bearing:1, thermal:2, quality:3, surge:4}[scenario]
sin      = sin(tick/4 + s.seed)                                    # seed = plant index 0..5
line_down = s.paused or s.stopped

temp_base      = 35 + max(0, severity*51 if mod==2 else severity*8) + sin*1.6
vibration_base = 1.1 + (severity*7.3 if mod==1 else severity*0.9) + |sin|*0.32
quality_base   = 99.3 - (severity*24 if mod==3 else severity*1.8) + sin*0.35

target_oee = clamp( oee_base
                    - (severity*17 if mod==1 else 0)
                    - (severity*23 if mod==2 else 0)
                    - (severity*21 if mod==3 else 0)
                    + (severity*2  if mod==4 else 0), 45, 99 )
if s.stopped: target_oee = 0                       # fault trip collapses OEE; operator pause does NOT change target
s.oee = r(s.oee*0.67 + target_oee*0.33)            # first-order lag, 1 decimal

base_rate  = p.rate * p.lines
throughput = 0 if line_down else round(base_rate * ((1+severity*0.25) if mod==4 else 1) * s.oee/100)   # integer
s.output  += throughput
s.history.append({t: tick, output: throughput, oee: s.oee, temp: r(temp_base), vibration: r(vibration_base,2), quality: r(quality_base)})
history capped at 55 (pop(0))
```
Per robot index `j` in 0..5 (`noise = (random() - 0.5) * 0.6`, i.e. uniform in [-0.3, 0.3)):
```
temp      = r(temp_base + noise*3 + j*0.55)                    # 1 dp
vibration = r(vibration_base + noise*0.5 + j*0.06, 2)           # 2 dp
rpm       = 0 if line_down else round(1800 + (severity*420 if mod==4 else 0) - severity*95 + sin(tick/2 + j)*25)
health    = clamp(round(99 - (severity*43 if mod==1 else 0) - (severity*30 if mod==2 else 0)
                           - (severity*19 if mod==3 else 0) + noise*2 - j*0.5), 15, 100)   # integer
energyKw  = r(1.5 if line_down else 12 + (severity*4.5 if mod==4 else 0) + (severity*3 if mod==2 else 0) + j*0.6, 1)
quality   = r(clamp(quality_base + noise, 55, 100), 1)
flag      = (not line_down) and (temp > 72 or vibration > 5.2 or quality < 86)
status:   if line_down: if s.paused: "stopped"   (if only s.stopped: status left unchanged)
          else:         "warning" if flag else "running"
robot.update(temperature=temp, vibration, rpm, health, energyKw, quality)
trip:     if flag and not s.stopped and mod in (1,2) and severity >= 0.6: s.stopped = True
          (only bearing/thermal can trip; remaining robots in the same tick still use the pre-computed line_down=False)
```
Consequences: a tripped line freezes robot status (typically `warning`), sets rpm to 0 and energy to 1.5 kW on subsequent ticks, forces OEE→0 and throughput→0, and suppresses alerts, until `baseline` inject / `resume` / `maintenance`. A `pause` sets robots to `stopped`; OEE target unchanged (holds), throughput 0.

Batch generation (same loop):
- **Telemetry** (topic `factory-iot-telemetry`): for each robot where `j == (tick+seed) % 6` **or** `j == (tick+seed+3) % 6` → exactly 2 messages per plant per tick (12 per tick total). Key `{"id": robot.id}`; value fields per schema (5.6) with `eventId = f"{siteId}-{tick}-{j}"`, `lineId = f"LINE-{j % 3 + 1}"`, `batchId = f"BATCH-{int(tick/12) + 1001}"`, `scenario`, `status` = robot status after update.
- **Asset state** (topic `factory-asset-state`): when `tick % 3 == 0`, for `robots[:3]` of each plant (18 messages on those ticks). Key `{"id": robot.id}`.
- **Maintenance event / alert** (topic `factory-maintenance-events`): when `not line_down and scenario != "baseline" and tick % 5 == 0 and severity >= 0.35` (i.e., intensity >= 35):
  - `id = f"AL-{siteId}-{tick}"`, `assetId = robots[0].id`, `type = {bearing:BEARING_RISK, thermal:OVERHEAT, quality:QUALITY_DRIFT, surge:CAPACITY_PRESSURE}[scenario]`, `severity = "critical" if intensity >= 70 else "warning"`, `acknowledged=False`.
  - message: bearing → "Abnormal spindle vibration detected"; thermal → "Temperature exceeds safe operating envelope"; quality → "First-pass yield is trending below target"; surge → "Line utilization above planned capacity".
  - Prepended to `self.alerts` (cap 45); queued into `generated`; Kafka value `{eventId=id, timestamp, siteId, assetId, eventType=type, severity, message, acknowledged:false}`, key `{"id": id}`.

After all plants: `last_batch = batch`; `events = [telemetry values from batch] + events`, cap 90; `snapshot()` computed; `emit("snapshot")` unless `suppress_broadcast`; then `emit("alert", a)` for each generated alert (never suppressed); return `batch`.

Note the **"risk score"** concept is not computed in Python. Anomaly detection in the sim is the `flag` thresholds above plus the alert rules; risk scoring (`riskScore`) is a Flink SQL derivation (section 6.2).

Rough steady-state expectations (random=0.5, noise 0): baseline temps ≈ 35 ± 1.6 (+0.55·j); vibration ≈ 1.1–1.42 (+0.06·j); quality ≈ 99.3 ± 0.35; health 99 − 0.5·j; rpm 1800 ± 25; energy 12 + 0.6·j; OEE converges to `oee_base` (EMA factor 0.33/tick).

#### 4.4.2 `snapshot()` algorithm
For each plant: `site = {**PLANT_FIELDS, scenario, intensity, paused, stopped, oee, throughput (= last history output or 0), output (cumulative), alerts (count of unacknowledged alerts for this site in self.alerts), status, robots: [copy of robot dicts], history: copy}`. The `robots` key **overrides** the integer `robots` field of the plant definition with the list of 6 robot dicts. `status`: `"idle"` if `paused`; else `"warning"` if `stopped` or any robot `status=="warning"`; else `"healthy"`.

Top level:
```
{ tick, timestamp, paused, sites: [6], alerts: alerts[:25], actions: actions[:20], recentEvents: events[:32],
  summary: { plants: 6, assets: sum(len(robots)) = 36, throughput: sum(site.throughput),
             oee: r( sum(site.oee * plant.lines) / sum(plant.lines) ),           # line-weighted, total lines = 36
             activeAlerts: count(unacknowledged alerts in self.alerts),
             eventsPerSecond: r( len(last_batch) / (max(250, SIM_INTERVAL_MS or 1700)/1000) ) } }
```
`eventsPerSecond` counts the full last batch (all topics, not just telemetry — contrary to the in-code comment) and reads `SIM_INTERVAL_MS` from env on each call (`float(...)`, invalid values raise `ValueError`).

**Error handling:** `ValueError` for unknown site / scenario / action (surfaced as HTTP 400); `step()` itself has no internal guards.

---

### 4.5 `server/schemas.py` — Schema Registry definitions
Exports `VALUE_SCHEMAS: dict[topic, jsonschema]` and `KEY_SCHEMA`. Helper `object(properties, required=None)` (shadows builtin) builds draft-07 object schemas with `additionalProperties: false` and **all properties required** by default. Shared primitives `_str, _num, _integer, _bool`. Full definitions in 5.6. Terraform copies in `infra/terraform/schemas/*.json` must be byte-semantically equal (asserted by a test that is currently stale).

---

### 4.6 `server/context.py` — local rules answerer
`demo_answer(question: Any, site: dict) -> dict` where `site` is a snapshot site. `q = str(question or "").lower()`, `bad = [robots with status=="warning"]`, `focus = site["name"]`. First matching regex wins (searched anywhere in `q`, no word boundaries):

| Order | Regex | title | risk | answer | evidence | suggestion |
|---|---|---|---|---|---|---|
| 1 | `maintenance\|failure\|risk\|bearing\|critical` | "Maintenance risk assessment" | `"Elevated"` if `bad` else `"Low"` | if bad: `"{focus} has {len(bad)} assets above normal thresholds. {bad[0].id} currently reads {vibration:.2f} mm/s vibration and {temperature:.1f}°C. A condition-based inspection is recommended before the next shift."`; else `"No currently simulated threshold breach at {focus}. Continue condition monitoring; no urgent work order is indicated."` | `["Scenario: <scenario>", "Active assets: <running count>/<n robots>", "Plant OEE: <oee>%"]` | "Inspect affected equipment and schedule maintenance if confirmed." |
| 2 | `quality\|reject\|yield` | "Quality and yield analysis" | `"Elevated"` if any robot `quality < 86` else `"Low"` | `"The current simulated average quality score for {focus} is {avg:.1f}%. "` + (scenario=="quality" → "A deliberate inspection drift is active; check vision calibration and the current batch." else "No significant quality drift is active.") | `["Shift throughput: <throughput> units/min", "Scenario: <scenario>"]` | "Review inspection calibration and quarantine suspect lots if necessary." |
| 3 | `energy\|power\|consumption` | "Energy and utilization" | `"Informational"` | `"Estimated current modeled asset load for {focus}: {sum energyKw:.1f} kW. Utilization increases during surge conditions."` | `["Plant OEE: <oee>%", "Active production lines: <lines>"]` | "Compare production intensity with energy usage in your analytics lakehouse." |
| 4 (default) | – | "Live operations briefing" | `"Attention"` if bad else `"Normal"` | `"{focus} is reporting {oee}% OEE and {throughput} units/min throughput. " + ("{n} robot(s) need attention." or "All modeled robots are operating within normal sensor thresholds.") + " This is a demo-derived summary, not a query to Confluent RTCE."` | `["Active scenario: <scenario>", "Last telemetry: <HH:MM:SS server-local time>"]` | "Select a fault scenario and compare live operational context." |

Error handling: none internal; caller returns 400 on exceptions. No I/O.

---

### 4.7 `server/mcp.py` — RTCE MCP client wrapper
`with_mcp(operation: Callable[[ClientSession], Awaitable[T]]) -> T`:
1. Read `RTCE_MCP_ENDPOINT`, `RTCE_MCP_BASIC_TOKEN`; missing → `RuntimeError("RTCE MCP is not configured. See docs/cloud-setup.md")`.
2. Endpoint must start with `https://` else `RuntimeError("RTCE MCP endpoint must be HTTPS.")`.
3. Import `mcp.client.streamable_http.streamablehttp_client` and `mcp.ClientSession`; failure → `RuntimeError("MCP SDK not installed: <exc>")`.
4. `anyio.run(run)` where `run()` opens `streamablehttp_client(endpoint, headers={"Authorization": f"Basic {token}"})` → `(read, write, _)`, `ClientSession(read, write)`, `await session.initialize()`, `return await operation(session)`.

A fresh MCP session is created per HTTP request (no pooling). The token is a pre-encoded base64 `key:secret` string (deploy script builds it as `base64("<mcp_global_key>:<mcp_global_secret>")`). Credentials never leave the server. **[NOTE]** Module naming collision, see section 10 (R1).

---

### 4.8 `deploy/requirements.txt`
```
Flask>=3.0,<4.0
flask-cors>=4.0,<5.0
python-dotenv>=1.0,<2.0
confluent-kafka[schemaregistry,json]>=2.4,<3.0
mcp>=1.8,<2.0
anyio>=3.7
```
`confluent-kafka[schemaregistry,json]` is imported lazily and only when `STREAM_MODE=kafka`; `mcp`+`anyio` lazily on first MCP call. Dockerfile: base `python:3.11-slim`, `ENV PORT=8080 STREAM_MODE=mock PYTHONUNBUFFERED=1`, `EXPOSE 8080`, healthcheck hits `/api/health` every 30 s (timeout 5 s), `CMD ["python","server/app.py"]`, frontend built in a prior `node:22-alpine` stage and copied to `/app/frontend/dist`.

---

## 5. Data Models

### 5.1 `PLANTS` (6 entries; `server/plants.py`)
| id | name | city | state | lat | lng | type | lines | robots (declared) | region | asset | oee_base | rate (units/line/min) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DET | Detroit Assembly | Detroit | Michigan | 42.3314 | -83.0458 | Automotive assembly | 8 | 12 | MIDWEST | EV body shop | 93.0 | 8 |
| AUS | Austin Gigafactory | Austin | Texas | 30.2672 | -97.7431 | Battery / robotics | 6 | 14 | SOUTH | Battery module line | 89.0 | 5 |
| SEA | Seattle Precision | Seattle | Washington | 47.6062 | -122.3321 | Precision components | 5 | 10 | WEST | CNC fabrication | 86.0 | 12 |
| PHX | Phoenix Semicon | Phoenix | Arizona | 33.4484 | -112.0740 | Electronics | 7 | 16 | WEST | Electronics assembly | 94.0 | 40 |
| CLT | Charlotte Manufacturing | Charlotte | North Carolina | 35.2271 | -80.8431 | Industrial machinery | 6 | 11 | EAST | Machine tool assembly | 90.0 | 4 |
| CHI | Chicago Distribution | Chicago | Illinois | 41.8781 | -87.6298 | Packaging / fulfillment | 4 | 9 | MIDWEST | Smart packaging | 96.0 | 60 |

Derived: total lines = 8+6+5+7+6+4 = **36** (equals number of simulated robots by coincidence: 6×6). The declared `robots` integer (72 total) is **not** the simulated count (always 6 per plant = 36). Baseline throughput per plant (units/min at nominal OEE) = `rate × lines × oee/100`: DET 59.5≈ round(64×0.93)=60, AUS round(30×0.89)=27, SEA round(60×0.86)=52, PHX round(280×0.94)=263, CLT round(24×0.90)=22, CHI round(240×0.96)=230. Comment-documented rationale: Automotive 92–94 %, battery 88–90 %, CNC 85–87 %, electronics 93–95 %, machinery 89–91 %, packaging 95–97 %.

Plant seed (phase offset for the sine wave and telemetry selection) = index in the list: DET 0, AUS 1, SEA 2, PHX 3, CLT 4, CHI 5.

### 5.2 Constants
| Name | Value |
|---|---|
| `ROBOT_TYPES` (index j → robot name) | `["Welding robot","Pick & place","Quality scanner","Assembly cobot","AGV transporter","Packaging arm"]` |
| Robot id format | `f"{plantId}-R{str(j+1).zfill(2)}"` → `DET-R01 … DET-R06` |
| Robots per plant | 6 (`range(6)`) |

#### `SCENARIOS`
| id | name | description |
|---|---|---|
| baseline | Healthy operations | All assets normal; deterministic live industrial telemetry. |
| bearing | Bearing wear | Vibration increases before a predictive maintenance alarm. |
| thermal | Thermal excursion | Heat and energy consumption spike on the production line. |
| quality | Quality drift | Inspection rejects rise and yield drops across a batch. |
| surge | Demand surge | Higher conveyor speed boosts output and load. |

Scenario `mod` index: baseline 0, bearing 1, thermal 2, quality 3, surge 4.

#### Robot initial values
`status:"running"`, `health: 99 - j`, `rpm:1800`, `vibration:1.2`, `temperature:36`, `energyKw:12`, `quality:99.1`.

#### Site initial state
`scenario:"baseline"`, `intensity:0`, `paused:false`, `stopped:false`, `seed:<plant index>`, `output:0`, `oee: r(oee_base)`, `history:[]`.

### 5.3 Simulation thresholds & tuning constants
| Constant | Value | Used for |
|---|---|---|
| Temp warning threshold | `temp > 72` | robot `flag` (→ status `warning`) |
| Vibration warning threshold | `vibration > 5.2` | `flag` |
| Quality warning threshold | `quality < 86` | `flag` |
| Trip condition | `flag and mod in (1,2) and severity >= 0.6` (intensity ≥ 60) | sets `stopped=True` |
| Alert condition | `tick % 5 == 0`, `severity >= 0.35`, not baseline, not line_down | generate alert + maintenance event |
| Alert critical cutoff | `intensity >= 70` | `severity:"critical"` else `"warning"` |
| OEE target clamp | `[45, 99]` (0 if stopped) | |
| OEE smoothing | `new = old*0.67 + target*0.33` | |
| OEE penalties (× severity) | bearing 17, thermal 23, quality 21; surge +2 | target OEE |
| Temp contribution | thermal 51·sev, others 8·sev; sine ±1.6; per-robot +0.55·j; noise ±0.9 | |
| Vibration contribution | bearing 7.3·sev, others 0.9·sev; \|sine\|·0.32; per-robot +0.06·j; noise ±0.15 | |
| Quality contribution | quality-scenario 24·sev, others 1.8·sev; sine ±0.35; noise ±0.3; clamp [55,100] | |
| Health | 99 − (bearing 43 / thermal 30 / quality 19)·sev + noise·2 − 0.5·j, clamp [15,100] | |
| RPM | 1800 + (surge 420·sev) − 95·sev + 25·sin(tick/2 + j); 0 if line_down | |
| Energy kW | 12 + (surge 4.5·sev) + (thermal 3·sev) + 0.6·j; 1.5 if line_down | |
| Throughput | `round(rate·lines·(1+0.25·sev if surge)·oee/100)`; 0 if line_down | |
| History cap | 55 points/site | |
| Alerts cap | 45 stored; 25 in snapshot | |
| Actions cap | 50 stored; 20 in snapshot | |
| Events cap | 90 stored; 32 in snapshot | |
| Intensity clamp | [1, 100], default 75 | |
| Batch id rollover | every 12 ticks, starting 1001 | |
| Publisher interval | `max(0.5 s, SIM_INTERVAL_MS/1000)`, default 1.7 s | |
| SSE heartbeat | 18 s | |
| Reconnect period | 15 s | |
| Kafka poll timeout | 1.0 s | |
| Webhook timeout | 8 s | |
| Producer flush on disconnect | 5 s | |
| Topic creation | partitions 3, replication factor 3 | |

### 5.4 Alert (stored in `sim.alerts`, SSE `alert`, snapshot `alerts[]`)
| Field | Type | Constraint |
|---|---|---|
| id | string | `AL-<siteId>-<tick>` (sim) / `eventId` or `KFK-<ms>` (Kafka) |
| timestamp | string | ISO-8601 UTC |
| siteId | string | plant id |
| siteName | string | plant name (sim) / siteId (Kafka-sourced) |
| assetId | string | `<siteId>-R01` for sim alerts |
| type | string | BEARING_RISK \| OVERHEAT \| QUALITY_DRIFT \| CAPACITY_PRESSURE (sim); any string from Kafka (default `UNKNOWN`) |
| severity | string | `critical` \| `warning` (Kafka may supply any string) |
| message | string | |
| acknowledged | boolean | false initially; set by `acknowledge` action |

### 5.5 Snapshot sub-structures
**Robot:** `{id:str, name:str, status:"running"|"warning"|"stopped", health:int[15..100], rpm:int, vibration:float(2dp), temperature:float(1dp), energyKw:float(1dp), quality:float(1dp, 55..100)}`.
**History point:** `{t:int tick, output:int, oee:float, temp:float, vibration:float(2dp), quality:float}`.
**Site (snapshot):** all `PLANTS` fields (incl. `oee_base`, `rate`, `lat`, `lng`, …) plus `scenario:str, intensity:number, paused:bool, stopped:bool, oee:float, throughput:int, output:int (cumulative units since start), alerts:int (unacknowledged), status:"healthy"|"warning"|"idle", robots:Robot[6], history:HistoryPoint[≤55]`.
**Snapshot:** `{tick:int, timestamp:str, paused:bool, sites:Site[6], alerts:Alert[≤25], actions:Action[≤20], recentEvents:Telemetry[≤32], summary:{plants:int, assets:int, throughput:int, oee:float, activeAlerts:int, eventsPerSecond:float}}`.

### 5.6 Kafka message schemas (`server/schemas.py`)
All value schemas and the key schema: JSON Schema draft-07, `type: object`, `additionalProperties: false`, every listed property in `required`.

**Key schema** (all three topics; subject `<topic>-key`): `{id: string}` — `id` is the robot id (telemetry, asset-state) or alert id (maintenance events).

**`factory-iot-telemetry`** (subject `factory-iot-telemetry-value`; produced 12 msgs/tick):
| Field | Type | Example / source |
|---|---|---|
| eventId | string | `DET-42-3` = `<site>-<tick>-<j>` |
| timestamp | string | ISO-8601 UTC |
| siteId | string | `DET` |
| siteName | string | `Detroit Assembly` |
| assetId | string | `DET-R04` |
| assetType | string | robot name |
| lineId | string | `LINE-1..3` = `j % 3 + 1` |
| scenario | string | current site scenario |
| temperature | number | °C 1 dp |
| vibration | number | mm/s 2 dp |
| rpm | integer | |
| energyKw | number | |
| qualityScore | number | % |
| health | integer | 15..100 |
| status | string | running / warning / stopped |
| batchId | string | `BATCH-1001+` |

**`factory-asset-state`** (produced every 3rd tick, 3 robots/plant): `assetId:string, siteId:string, timestamp:string, status:string, health:integer, temperature:number, vibration:number, qualityScore:number, scenario:string`.

**`factory-maintenance-events`** (produced with each generated alert): `eventId:string, timestamp:string, siteId:string, assetId:string, eventType:string, severity:string, message:string, acknowledged:boolean`.

**Flink-derived topics (consumed, schemas not defined in backend; from `flink/*.sql`):**
| Topic | Fields |
|---|---|
| `factory-risk-signals` | `siteId, assetId, eventTime, riskType (BEARING_RISK/THERMAL_RISK/QUALITY_RISK), riskScore DOUBLE, severity (critical/warning), message` |
| `factory-shift-kpis` | `siteId, windowStart (STRING), sampleCount, meanTemperature, meanVibration, meanQuality, energyKwhEstimate` (1-minute tumbling windows) |
| `factory-quality-alerts` (not consumed by the backend) | `siteId, assetId, batchId, qualityScore, eventTime, action (QUARANTINE_BATCH \| REQUEST_INSPECTION)` |

Flink risk formulas (for reference, performed in Confluent, not in Python): `riskType` = BEARING_RISK if `vibration > 5.2`, else THERMAL_RISK if `temperature > 72`, else QUALITY_RISK; `riskScore` = `vibration*11` / `temperature` / `(100 - qualityScore)*4` respectively; `severity` = `critical` if `vibration > 6.5 OR temperature > 85 OR qualityScore < 80`, else `warning`; filter `vibration > 5.2 OR temperature > 72 OR qualityScore < 86`. Quality alerts: `qualityScore < 86`; action QUARANTINE_BATCH if `< 78`. `energyKwhEstimate = SUM(energyKw)/60.0`.

### 5.7 Action record
`{id:"ACT-<ms epoch>", timestamp:ISO, siteId:str, action:"pause"|"resume"|"maintenance"|"acknowledge", robotId:str|null, mode:"simulation", webhookDispatched?:true}`.

### 5.8 Transport info (`GET /api/stream`, SSE `cloud`, health `stream`)
`{mode:"kafka"|"mock", status:"disconnected"|"mock"|"configuration_required"|"connecting"|"connected"|"error", sent:int, failed:int, lastError:str|null, lastAck:str|null, topics:[3 topic names], derivedConnected:bool, sourceConnected:bool}` plus (app-level) `lastDerived:{topic,value,timestamp}|null, sourceMode:"kafka"|"sim"`.

---

## 6. Integration Points

| # | System | Direction | Protocol / Auth | Details & notes |
|---|---|---|---|---|
| 1 | Confluent Cloud Kafka — produce | Backend → Kafka | Kafka native, `SASL_SSL`, `PLAIN` (API key/secret) via `confluent_kafka.Producer` | Topics `factory-iot-telemetry`, `factory-asset-state`, `factory-maintenance-events`. Key `json.dumps({"id": ...})`, value `json.dumps(obj)`; plain JSON (no SR framing). No explicit partitioner (keyed hash), no delivery callbacks. Only when `STREAM_MODE=kafka` and status `connected` |
| 2 | Kafka — derived consume | Kafka → Backend | Same auth; `Consumer`, group `factory-pulse-output-<ms>`, `latest` | Topics `KAFKA_RISK_TOPIC`(`factory-risk-signals`), `KAFKA_KPI_TOPIC`(`factory-shift-kpis`); enabled by `KAFKA_CONSUME_DERIVED=true`; forwarded to UI as SSE `flink` |
| 3 | Kafka — source consume | Kafka → Backend | Same; group `factory-pulse-source-<ms>`, `latest` | Topics `KAFKA_TELEMETRY_TOPIC`, `KAFKA_STATE_TOPIC`, `KAFKA_EVENTS_TOPIC` (defaults = the three produced topics); enabled by `KAFKA_CONSUME_SOURCE=true` at connect or on-demand via `/api/stream-mode`; merged into sim state |
| 4 | Schema Registry | Backend → SR | HTTPS REST, basic auth `SR_KEY:SR_SECRET` via `SchemaRegistryClient` | Registers 6 subjects `<topic>-key` / `<topic>-value` as `JSON` schemas on each `connect()` (idempotent for identical schemas). Ids cached, unused afterwards |
| 5 | Kafka Admin | Backend → Kafka | Same SASL_SSL | Optional topic creation (3 partitions, RF 3) when `KAFKA_AUTO_CREATE_TOPICS=true` |
| 6 | Confluent Flink SQL | Indirect (via Kafka) | n/a | Statements in `flink/01..04*.sql` read telemetry and write `factory-risk-signals`, `factory-shift-kpis`, `factory-quality-alerts`. Backend neither calls Flink APIs nor needs the compute pool id |
| 7 | Confluent RTCE MCP | Backend → MCP | MCP Streamable HTTP over HTTPS, `Authorization: Basic <RTCE_MCP_BASIC_TOKEN>` via `mcp` SDK + `anyio` | `GET /api/mcp/tools` → `list_tools`; `POST /api/mcp/call` → `call_tool(name, arguments=args)`. New session per request. Tool name whitelist `^[-_a-zA-Z0-9.]+$`, ≤150 chars |
| 8 | Frontend (React SPA) | Bidirectional | HTTP/JSON + SSE, same origin (or any origin: CORS `*`) | See 4.1 for routes and SSE event catalogue. Static assets from `frontend/dist` |
| 9 | Action webhook | Backend → external | HTTPS POST JSON, optional `Bearer` token, 8 s timeout | Only for `maintenance` action; body = action record |
| 10 | Google Maps | None in backend | – | Backend merely reports `googleMapsConfigured` from `VITE_GOOGLE_MAPS_API_KEY`; key is baked into the frontend at build time (Docker ARG/ENV) |
| 11 | Deploy tooling | Config in | `scripts/deploy.py`, Terraform in `infra/terraform` produce the `.env` (`STREAM_MODE=kafka`, `KAFKA_CONSUME_DERIVED=true` when a Flink pool exists, `RTCE_MCP_BASIC_TOKEN=base64(key:secret)`, bootstrap with `SASL_SSL://` prefix stripped) | Outside this document's scope |

---

## 7. Critical Flows (Sequence Diagrams)

### 7.1 Startup
```mermaid
sequenceDiagram
    autonumber
    participant Proc as python server/app.py
    participant Env as dotenv/os.environ
    participant App as app.py
    participant Sim as FactorySimulation
    participant KT as ConfluentTransport
    participant K as Kafka/SR

    Proc->>Env: load_dotenv()
    Proc->>App: import context, kafka, mcp, plants, simulation
    App->>Sim: FactorySimulation() (6 sites x 6 robots, tick 0)
    App->>KT: ConfluentTransport() (mode from STREAM_MODE)
    App->>App: _source_mode = (KAFKA_CONSUME_SOURCE == "true")
    App->>Sim: subscribe(broadcast)
    App->>KT: on_derived=_on_derived, on_source=_on_source
    App->>App: _startup()
    App->>KT: connect()
    alt STREAM_MODE != kafka
        KT-->>App: status = mock
    else missing env or lib
        KT-->>App: status = configuration_required, lastError set
    else configured
        KT->>K: Producer, SchemaRegistryClient, optional create_topics
        KT->>K: register_schema x6
        KT->>KT: status = connected
        opt KAFKA_CONSUME_DERIVED = true
            KT->>K: subscribe risk and KPI topics (thread)
        end
        opt KAFKA_CONSUME_SOURCE = true
            KT->>K: subscribe 3 source topics (thread)
        end
    end
    opt KAFKA_CONSUME_SOURCE=true and connected and no source consumer
        App->>KT: _connect_source()
    end
    App->>App: start publisher thread (interval = max(0.5, SIM_INTERVAL_MS/1000))
    App->>App: start retry thread (15 s)
    Proc->>App: app.run(0.0.0.0, PORT or 4000, threaded=True)
```

### 7.2 Telemetry produce / consume (Kafka source mode round trip)
```mermaid
sequenceDiagram
    autonumber
    participant Pub as Publisher thread
    participant Sim as FactorySimulation
    participant KT as ConfluentTransport
    participant K as Kafka
    participant F as Flink SQL
    participant CS as Source poll thread
    participant CD as Derived poll thread
    participant App as app.py
    participant SSE as SSE clients

    Pub->>Sim: suppress_broadcast = (source_mode and kafka connected)
    Pub->>Sim: step()
    Sim-->>Pub: batch (telemetry, asset-state, events)
    Pub->>KT: publish(batch)
    KT->>K: produce(topic, key json, value json) + poll(0)
    K->>F: factory-iot-telemetry
    F->>K: factory-risk-signals / factory-shift-kpis / factory-quality-alerts
    K-->>CD: risk and KPI records
    CD->>App: on_derived({topic,value,timestamp})
    App->>SSE: event: flink
    K-->>CS: telemetry/state/events (latest offsets)
    CS->>App: on_source({topic,value,timestamp})
    alt source_mode true
        App->>Sim: merge robot fields, scenario / insert alert (dedupe by id)
        App->>SSE: event: snapshot (and alert if new)
    else sim mode
        App-->>CS: ignored
    end
    Pub->>SSE: event: cloud (cloud info)
```

### 7.3 SSE streaming
```mermaid
sequenceDiagram
    autonumber
    participant B as Browser
    participant A as GET /api/events
    participant Q as queue.Queue (per client)
    participant H as broadcast()

    B->>A: GET /api/events
    A->>Q: create queue; _clients.add(q)
    A-->>B: event: snapshot (current)
    loop until disconnect
        H->>Q: put_nowait("event: X\ndata: json\n\n")
        Q-->>B: yield message
        Note over A,Q: if no message for 18 s: yield ": heartbeat"
    end
    B--xA: connection closed (GeneratorExit)
    A->>A: finally: _clients.discard(q)
```
Initial page load additionally calls `GET /api/bootstrap` for scenarios/plants/cloud/lastDerived.

### 7.4 Auth flows
There is **no end-user authentication**. Outbound credential flows:
```mermaid
sequenceDiagram
    autonumber
    participant B as Browser
    participant S as Flask server
    participant MCP as RTCE MCP (HTTPS)
    participant K as Kafka (SASL_SSL PLAIN)
    participant SR as Schema Registry (basic auth)
    participant W as Webhook (HTTPS, Bearer)

    B->>S: POST /api/mcp/call {name,args} (no credentials)
    S->>S: validate name regex and length; require env endpoint+token, https
    S->>MCP: Streamable HTTP, Authorization: Basic RTCE_MCP_BASIC_TOKEN
    MCP-->>S: tool result
    S-->>B: {source:"CONFLUENT RTCE MCP", result}

    S->>K: SASL PLAIN KAFKA_API_KEY/SECRET (startup, reconnect)
    S->>SR: Basic SR_API_KEY:SR_API_SECRET

    B->>S: POST /api/control {action: maintenance}
    S->>W: POST JSON + Bearer ACTION_WEBHOOK_TOKEN (if set)
```
Secrets never appear in any response; `info()` returns only status/last error text (which may include exception messages).

### 7.5 Simulation tick (publisher loop)
```mermaid
sequenceDiagram
    autonumber
    participant L as _publisher_loop
    participant Sim as FactorySimulation
    participant KT as ConfluentTransport
    participant H as broadcast

    loop every interval (stop.wait(interval))
        L->>L: wanted = _source_mode ; live = (cloud.status == "connected")
        L->>Sim: suppress_broadcast = wanted and live
        L->>Sim: step()
        Sim->>Sim: update 6 sites, build batch, snapshot
        alt not suppressed
            Sim->>H: emit snapshot
        end
        Sim->>H: emit alert (each new alert)
        Sim-->>L: batch
        L->>KT: publish(batch) (no-op unless connected)
        opt wanted and not live
            L->>H: broadcast snapshot (explicit fallback)
        end
        L->>H: broadcast cloud _cloud_info()
    end
    Note over L: any exception is printed ("Publish error:") and the loop continues
```
Delay semantics: waits first (`stop.wait(interval)`), so the first tick occurs one interval after startup; the initial SSE frame before that shows `tick:0` with empty history.

### 7.6 Operator action
```mermaid
sequenceDiagram
    participant B as Browser
    participant A as POST /api/control
    participant Sim as FactorySimulation
    participant W as Webhook
    participant SSE as SSE clients
    B->>A: {siteId, action, robotId?}
    A->>Sim: act()
    Sim->>SSE: event: action
    opt action == maintenance and ACTION_WEBHOOK_URL set
        A->>W: POST (https only, 8 s)
    end
    A-->>B: {ok:true, result} or 400 {error, note}
```
The next tick's `snapshot` reflects the changes (no immediate snapshot is pushed by `act`/`inject`; only `action`/`scenario` events).

---

## 8. Error Handling & Edge Cases

### 8.1 Fallback / degraded modes
| Situation | Behavior |
|---|---|
| `STREAM_MODE` unset or `mock` | `status="mock"`, `publish` is a no-op, `derivedConnected/sourceConnected=false`. All UI data comes from the direct sim→SSE path. Default and fully functional |
| `STREAM_MODE=kafka` but required env missing | `status="configuration_required"`, `lastError="Missing: ..."`. Not retried automatically (the retry loop only retries `error`/`disconnected`). Sim continues in direct mode |
| `confluent_kafka` not installed | `status="configuration_required"`, `lastError="confluent_kafka not installed: ..."` |
| Kafka/SR connect failure (bad credentials, network) | `status="error"`, `lastError` set; retried every 15 s via `connect()` (re-creates producer, re-registers schemas, re-subscribes consumers if flags set) |
| Publish failure at runtime | `failed += len(batch)`, `status="error"`; reconnect loop recovers; meanwhile `step()` still runs and (if `_source_mode`) the publisher emits a direct snapshot |
| Source mode wanted but Kafka not connected | `suppress_broadcast=False` and the publisher also broadcasts a snapshot → UI keeps updating (badge shows `sourceMode:"kafka"` with status != connected). **[NOTE]** in this case `sim.step()` already emitted a snapshot, so the UI receives **two** snapshots per tick |
| Source mode on, Kafka connected, but no messages arrive | UI receives no `snapshot` events at all (suppressed) until messages come back; only `cloud` events every tick (and heartbeats) |
| Source consumer messages when `_source_mode=false` | ignored; the consumer keeps running |
| Derived consumer disabled (`KAFKA_CONSUME_DERIVED!="true"`) | no `flink` events; `lastDerived` stays `null` |
| Switching to `kafka` while not connected | `_source_mode=True`; no consumer started; fallback path applies |
| MCP not configured / SDK missing / non-HTTPS | `/api/mcp/tools` → 503 `{connected:false,error}`; `/api/mcp/call` → 502; `/api/health.mcpConfigured=false`. `/api/context` always works locally |
| Frontend not built | non-API paths → 404 JSON |
| Webhook failure | HTTP 400 with `note`; the local sim change already happened and an `action` SSE event was already emitted |
| Webhook URL not https | `ValueError` → 400 (after local action applied) |

### 8.2 Edge cases in the simulation
- `inject` with `intensity` missing/`null` → 75; non-numeric → `ValueError` → 400; `<1` → 1; `>100` → 100. `scenario=baseline` zeros severity regardless of stored intensity.
- Changing scenario while `stopped=True` and scenario ≠ baseline keeps the line stopped (only `baseline` inject, `resume`, `maintenance` clear it). `inject` always clears `paused`.
- A tripped line keeps its `warning` robot statuses frozen even if sensors would no longer breach.
- Alerts accumulate without dedup within the sim except by id; one critical alert per site every 5 ticks while active; capped at 45.
- `acknowledge` only changes alerts of the given site that are already stored; new alerts continue.
- `robotId` in control actions is accepted but unused by the simulation.
- Python `round()` uses banker's rounding for integer `rpm/health/throughput`.
- Initial SSE frame before first tick: `tick=0`, all `history` empty, `throughput=0`, `eventsPerSecond=0`.
- Large number of SSE clients: each holds a thread and an **unbounded** queue; slow clients accumulate memory.
- `_on_source` accepts unvalidated scenario strings and statuses from the topic; unknown scenario would make the next `step()` raise `KeyError` in `mod` lookup (caught by the publisher loop's try/except, but the tick would then fail repeatedly until fixed). **[NOTE]**
- `broadcast` serializes JSON per call per event, without `default=`; non-serializable values raise (not expected).

### 8.3 Concurrency hazards
No locking around `sim` mutation vs. `snapshot()` (request thread, publisher thread, Kafka thread). `list`/`dict` iteration while another thread appends may raise "changed size during iteration" in rare cases; publisher loop swallows exceptions, request handlers return 400.

---

## 9. Testing Strategy

**Current state:** `tests/simulation.test.js` imports `../server/src/simulation.js` and `schemas.js` (the removed Node implementation) and `tests/test_deploy.py::test_terraform_schema_files_match_actual_node_producer` also shells out to Node against `server/src/schemas.js`. These are **stale** relative to the Python backend. `tests/test_deploy.py` otherwise tests `scripts/deploy.py` render logic and Terraform schema file presence (6 schema files; subject names `factory-(iot-telemetry|asset-state|maintenance-events)-(key|value).json`).

**Recommended (pytest, no network):**
1. **Unit — simulation** (inject `random=lambda: 0.5`):
   - 6 sites, 36 robots, `activeAlerts==0`, all baseline at construction.
   - `step()` returns ≥ 12 messages; first tick contains exactly 12 telemetry messages; `tick % 3 == 0` adds 18 asset-state messages; telemetry values validate against `VALUE_SCHEMAS` with `jsonschema` (draft-07, `additionalProperties:false`).
   - Bearing @90 for 10 ticks: DET `status=="warning"`, `stopped==True`, `oee<90`, critical alert present (alerts need `tick%5==0` and not line_down — verify on tick 5), `last_batch` non-empty.
   - Thermal @95 then `acknowledge` → `activeAlerts==0`; `maintenance` → scenario baseline, `stopped False`, health 99.
   - Trip/reset matrix: pause → status `idle`, robots `stopped`, throughput 0; resume clears.
   - Invalid site/scenario/action → `ValueError`.
   - OEE EMA convergence to `oee_base`; weighted summary OEE equals manual formula; clamping bounds (OEE 45..99, health ≥ 15, quality ≥ 55).
   - Determinism: seeded `random` → identical batches.
2. **Unit — context.py:** each regex branch, empty/None question, with/without warning robots.
3. **Unit — kafka.py** with injected `env` and fake `confluent_kafka` modules via `sys.modules` monkeypatch: mock mode status; missing-env message; successful connect registers 6 subjects; `publish` groups and encodes `json.dumps` keys; exception path sets `error` and increments `failed`; consumer poll loop dispatch (feed fake messages, invalid JSON → `last_error`); `disconnect` idempotent.
4. **Unit — mcp.py:** unconfigured, non-HTTPS, SDK missing; happy path with a fake `streamablehttp_client` and `ClientSession`.
5. **API tests (Flask `test_client`)** with `STREAM_MODE=mock` and the background threads neutralised (set env so interval is huge, or patch `_startup`): health, bootstrap shape, simulate/control validations (400s), webhook (patch `urllib.request.urlopen`), context 400/200, mcp tool-name validation, stream-mode validation and toggle, static fallback. SSE: read first frame from `/api/events` streamed response and assert `event: snapshot`.
6. **Contract tests:** Terraform `infra/terraform/schemas/*.json` equal `VALUE_SCHEMAS`/`KEY_SCHEMA` (replace the Node-based test with a Python import); Flink SQL column names exist in telemetry schema.
7. **Integration (optional, manual/CI-secret gated):** real Confluent environment from Terraform with `KAFKA_CONSUME_DERIVED=true`; verify `flink` events and source round trip.
8. **Smoke:** Docker image build + `/api/health` HEALTHCHECK.

**Testability issue:** importing `app.py` starts threads and calls `cloud.connect()` at import; tests must set env before import or patch `threading.Thread`.

---

## 10. Open Questions & Risks

| # | Type | Item |
|---|---|---|
| R1 | Risk (high) | **Module name shadowing:** `server/mcp.py` is imported as top-level `mcp` (because `server/` is `sys.path[0]`). Inside `with_mcp`, `from mcp.client.streamable_http import ...` then resolves against the local module (not a package) and fails with "MCP SDK not installed", so the real MCP feature cannot work as written when launched via `python server/app.py`. Likewise `server/kafka.py` shadows the name `kafka` (harmless for `confluent_kafka`). Fix would be renaming the modules or packaging `server` — not done here. Reimplementers should avoid these names |
| R2 | Risk | **No Schema Registry wire format:** `publish` sends raw JSON strings; registered schema ids are not embedded, no validation. Flink tables inferred from Schema Registry with a `json-registry` format may expect the magic byte. Consumers decode with plain `json.loads`, so derived topics with registry framing would fail decode (`last_error="Decode ..."`). Needs confirmation against the actual Flink/Terraform configuration |
| R3 | Risk | Unauthenticated, CORS `*` API that can inject faults, trigger webhooks, call arbitrary MCP tools (`/api/mcp/call` allows any tool name matching the regex). Acceptable for a demo; not for production |
| R4 | Risk | No locking / unbounded SSE queues / thread-per-SSE client; Flask dev server (`app.run`) is the production server in Docker. Running under gunicorn with multiple workers would duplicate simulations and Kafka consumers because `_startup()` executes on import |
| R5 | Risk | Reconnect races: `connect()` after an error creates new consumers while old poll threads (loop condition `self.consumer is not None`) may keep polling the *new* consumer object → duplicate polling threads / duplicate events; `poll()` on a closed consumer can raise and kill a thread silently |
| R6 | Bug | In source-mode-with-Kafka-unavailable, two snapshots per tick are broadcast (see 8.1) |
| R7 | Bug | `_on_source` hard-codes topic names, ignoring `KAFKA_TELEMETRY_TOPIC`/`KAFKA_STATE_TOPIC`/`KAFKA_EVENTS_TOPIC` overrides; accepts arbitrary scenario strings (can break `step()` with `KeyError`) |
| R8 | Bug | `JSON_SORT_KEYS=False` is a no-op in Flask 3 (keys sorted alphabetically). Frontend must not rely on key order |
| R9 | Bug | `/api/mcp/call` returns `jsonify({"result": <MCP CallToolResult pydantic object>})`; Flask's default JSON provider cannot serialize pydantic models → likely 502 even if the MCP call succeeds. `/api/mcp/tools` explicitly converts, so it is fine |
| R10 | Bug | Stale comment/doc mismatches: `eventsPerSecond` counts all topics, not telemetry only; PLANTS `robots` integers (72 total) disagree with the 36 simulated robots; `.env.example` omits `KAFKA_CONSUME_SOURCE`, `KAFKA_TELEMETRY_TOPIC`, `KAFKA_STATE_TOPIC`, `KAFKA_EVENTS_TOPIC` |
| R11 | Risk | `sent`/`last_ack` reflect local enqueue, not broker delivery; no delivery report callback; `BufferError` marks the whole transport `error` and drops the batch |
| R12 | Open | Static route precedence: Flask registers its own `static` rule at `/<path:filename>` (because `static_url_path="/"`) in addition to the custom catch-all `/<path:path>`. Which wins for SPA deep links (index.html fallback vs plain 404) depends on Werkzeug rule ordering — not verified |
| R13 | Open | `simulation.paused` (global) is never set; is a global pause intended? |
| R14 | Open | Should externally-produced maintenance events be allowed to alter `siteName` etc.? Currently `siteName=siteId` |
| R15 | Open | Consumer group ids include a timestamp (fresh group every connect, `latest` offset) — intentional for demo, but offsets/lag are never persisted, and groups accumulate on the broker (they expire) |
| R16 | Open | `KAFKA_AUTO_CREATE_TOPICS` creates only the 3 source topics; derived topics (`factory-risk-signals`, `factory-shift-kpis`, `factory-quality-alerts`) are expected to be created by Flink/Terraform |
| R17 | Open | Tests directory still targets removed Node code; decide whether to port or delete |

---

## Appendix A — Configuration (environment variables)

Loaded from the process environment; `python-dotenv` `load_dotenv()` first loads a `.env` (found by walking up from `server/app.py`, never overrides already-set variables). Booleans are string-compared to exactly `"true"`.

| Variable | Default (code) | Default (`.env.example`) | Purpose | Used in |
|---|---|---|---|---|
| `PORT` | `4000` | `4000` (Docker image sets `8080`) | HTTP listen port | `app.py` `__main__` |
| `SIM_INTERVAL_MS` | `1700` (publisher interval floor 500 ms; `eventsPerSecond` floor 250 ms) | `1700` | Simulation tick period in ms | `app.py` `_startup`; `simulation.py` `snapshot()` |
| `STREAM_MODE` | unset → `mock` | `mock` | `kafka` enables Confluent transport; anything else = mock | `kafka.py` `__init__` |
| `KAFKA_BOOTSTRAP_SERVERS` | – (required in kafka mode) | `pkc-xxxxx.us-east-1.aws.confluent.cloud:9092` | Broker list (host:port, no scheme) | `kafka.py` connect/consumers |
| `KAFKA_API_KEY` | – (required) | empty | SASL PLAIN username | `kafka.py` |
| `KAFKA_API_SECRET` | – (required) | empty | SASL PLAIN password | `kafka.py` |
| `SCHEMA_REGISTRY_URL` | – (required) | `https://psrc-xxxxx.us-east-1.aws.confluent.cloud` | Schema Registry endpoint | `kafka.py` |
| `SCHEMA_REGISTRY_API_KEY` | – (required) | empty | SR basic-auth user | `kafka.py` |
| `SCHEMA_REGISTRY_API_SECRET` | – (required) | empty | SR basic-auth password | `kafka.py` |
| `KAFKA_AUTO_CREATE_TOPICS` | unset (false) | `false` | Create 3 source topics (3 partitions, RF 3) at connect | `kafka.py` |
| `KAFKA_CONSUME_DERIVED` | unset (false) | `false` | Start consumer for Flink output topics | `kafka.py` |
| `KAFKA_CONSUME_SOURCE` | unset (false) | *not listed* | Start source consumer and initial `_source_mode=True` ("kafka" source mode) | `kafka.py`, `app.py` (`_source_mode`, `_startup`) |
| `KAFKA_RISK_TOPIC` | `factory-risk-signals` | `factory-risk-signals` | Derived topic: risk signals | `kafka.py` `_connect_derived` |
| `KAFKA_KPI_TOPIC` | `factory-shift-kpis` | `factory-shift-kpis` | Derived topic: shift KPIs | `kafka.py` `_connect_derived` |
| `KAFKA_TELEMETRY_TOPIC` | `factory-iot-telemetry` | *not listed* | Source consumer telemetry topic (producer topic names are fixed) | `kafka.py` `_connect_source` |
| `KAFKA_STATE_TOPIC` | `factory-asset-state` | *not listed* | Source consumer asset-state topic | `kafka.py` `_connect_source` |
| `KAFKA_EVENTS_TOPIC` | `factory-maintenance-events` | *not listed* | Source consumer maintenance-events topic | `kafka.py` `_connect_source` |
| `ACTION_WEBHOOK_URL` | unset | empty | HTTPS URL to POST on `maintenance` action | `app.py` `/api/control` |
| `ACTION_WEBHOOK_TOKEN` | unset | empty | Bearer token for webhook | `app.py` `/api/control` |
| `RTCE_MCP_ENDPOINT` | unset | empty | Confluent RTCE MCP HTTPS endpoint | `mcp.py`; `app.py` health/bootstrap flags |
| `RTCE_MCP_BASIC_TOKEN` | unset | empty | Pre-encoded Basic auth token (`base64(key:secret)`) | `mcp.py`; `app.py` flags |
| `VITE_GOOGLE_MAPS_API_KEY` | unset | empty | Browser Maps key; backend only reports whether set (`googleMapsConfigured`); consumed by frontend build | `app.py` health; frontend/Docker build arg |
| `VITE_GOOGLE_MAPS_MAP_ID` | unset | empty | Maps map id (frontend only) | frontend/Docker build arg |
| `PYTHONUNBUFFERED` | – | – | Set to `1` in Dockerfile for log flushing | `deploy/Dockerfile` |

Secrets rule (from `.env.example`): credentials remain server-side; never prefix secrets with `VITE_`.

## Appendix B — Reimplementation checklist
1. Create `plants.py` data exactly as 5.1–5.2.
2. Implement `schemas.py` with the `object()` helper and the 3 value schemas + key schema (5.6).
3. Implement `FactorySimulation` per 4.4 using the exact coefficients; verify with a zero-noise test (random=0.5).
4. Implement `ConfluentTransport` per 4.2, preserving status strings, group id patterns, and plain-JSON wire format.
5. Implement `demo_answer` per 4.6 and `with_mcp` per 4.7 (rename modules to avoid R1).
6. Implement `app.py` routes, SSE hub (18 s heartbeat; first frame `snapshot`), publisher/retry threads, `_on_source` merge, and static serving.
7. Package with `deploy/requirements.txt` and the Dockerfile (port 8080, health check on `/api/health`).
