# Streamhouse Gaps — Integration Plan

**Status:** Draft  
**Author:** FactoryPulse Engineering  
**Relates to:** `docs/ARCHITECTURE.md`, `specs/TECHNICAL_SPEC.md`, `docs/DECISIONS.md`

---

## Purpose

The FactoryPulse demo diagram shows four Confluent Cloud Streamhouse components (Kafka, Flink, Schema Registry, Tableflow) driving four consumer categories (Continuous RAG, Operations UI, Alerts/Actions, Analytics/AI). A gap analysis performed against the current codebase identified three components that are either absent or not active by default. This document specifies the work required to close each gap, gives a rationale for the approach, and defines acceptance criteria that a reviewer can verify without running a full Confluent Cloud environment.

---

## Gap summary

| Gap | Current state | Target state |
|---|---|---|
| **G1 — Flink operational pipeline** | `factory.state` and `factory.exceptions` are produced by a Python stub (`_build_demo_step`) | Flink SQL joins and detects over the four raw telemetry topics and produces `factory.state` and `factory.exceptions` continuously |
| **G2 — Tableflow materialization** | Mentioned in architecture diagram and `ARCHITECTURE.md`; no Terraform resource, no API, no UI panel | At least two topics configured for Tableflow materialization; Terraform provisions the connection; UI shows the analytical path |
| **G3 — Schema Registry active by default** | JSON schemas exist and serialization support is wired; default `SERIALIZATION_MODE=plain-json` bypasses Schema Registry | Schema Registry is the default when credentials are present; serialization mode is governed and visible in the UI |

---

## Scope boundaries

**In scope for this plan:**

- Flink SQL for operational telemetry correlation (G1).
- Terraform resources and documentation for Tableflow (G2).
- Schema Registry default-on behaviour when credentials are configured (G3).
- UI changes to surface the new capabilities in the Streamhouse and Settings views.
- Documentation updates.

**Out of scope:**

- Replacing the in-process vector index with an external vector store (`VECTOR_SEARCH_AGG`). Tracked separately in `TECHNICAL_SPEC.md` as a production extension.
- Outbound alerting integrations (PagerDuty, email). The Alerts/Actions consumer is display-only by design for the demo.
- Multi-machine or multi-line factory simulation.
- Authentication / authorization changes.

---

## ADR additions

### ADR-007 — Flink SQL as the operational correlation tier

**Decision:** Add a Flink SQL file that derives `factory.state` and `factory.exceptions` from raw telemetry topics. The Python demo step API (`/api/demo/step/{step}`) is retained as a quick override so the demo can be driven without requiring a running Flink compute pool.

**Reason:** The diagram explicitly shows Flink with a "join · detect · chunk · embed" role. Only the chunk and embed part is currently implemented. Adding the join/detect SQL closes the architectural gap and gives a realistic Confluent-native story without removing the demo shortcut.

**Constraints:**
- Flink SQL must use only topics already in the resource map.
- The Python demo path must still work unchanged when `RAG_PIPELINE_MODE=local` (i.e. no Flink pool required).
- The SQL must be safe to run repeatedly (use `CREATE TABLE IF NOT EXISTS`, `CREATE JOB IF NOT EXISTS` patterns).

---

### ADR-008 — Tableflow for factory operational analytics

**Decision:** Configure Tableflow on `factory.state` and `factory.exceptions` topics via Terraform. Add a new Terraform variable `enable_tableflow` (default `false`) so the resource is opt-in for demos that have a STANDARD cluster or a Tableflow-enabled environment.

**Reason:** ADR-005 established that Tableflow belongs to the historical/analytical path, not the RAG retrieval path. The gap is that the component is architecturally referenced but completely absent from code. Adding it as an optional Terraform resource with a clear Iceberg/Delta sink reference closes the diagram-to-code gap.

**Constraints:**
- Tableflow must not appear in the synchronous RAG latency path.
- The Terraform change must be idempotent and safe to apply on a cluster that does not have Tableflow enabled.
- The UI must make clear that Tableflow is the analytical / historical path, not the live retrieval path.

---

### ADR-009 — Schema Registry as the default when credentials are present

**Decision:** Change `SERIALIZATION_MODE` to default to `schema-registry-json` when `CONFLUENT_SCHEMA_REGISTRY_URL`, `CONFLUENT_SCHEMA_REGISTRY_API_KEY`, and `CONFLUENT_SCHEMA_REGISTRY_API_SECRET` are all set. Retain `plain-json` as an explicit opt-out for environments without Schema Registry credentials.

**Reason:** Schema Registry exists in every Confluent Cloud environment at no extra cost. Leaving it optional by default understates its role in the demo. Making it the default when credentials are present turns Schema Registry from a diagram label into a live governance participant.

**Constraints:**
- Existing demos running without Schema Registry credentials must not break.
- The logic must live in `Settings.serialization_mode` or a derived property — no scattered `if` checks across the codebase.
- The `SERIALIZATION_MODE` environment variable must still override the auto-detected default, allowing explicit `plain-json` when needed.

---

## Work breakdown

---

### G1 — Flink operational pipeline

#### G1-1 Create `infra/flink/factory_operations.sql`

Write a new Flink SQL file alongside `infra/flink/continuous_rag.sql`. The file must implement the following jobs:

**Job 1 — Telemetry aggregation window**

Aggregate `factory.machine.telemetry` over a 30-second tumbling window per `machine_id`. Compute:

- `avg_vibration_mm_s`
- `max_vibration_mm_s`
- `avg_temperature_c`
- `max_temperature_c`
- `avg_cycle_time_sec`
- `event_count`

Produce a row per window per machine into an intermediate table `factory.machine.metrics` (Flink-owned, compacted).

**Job 2 — Exception detection**

Read `factory.machine.metrics`. Apply threshold rules:

| Signal | Warning threshold | Critical threshold |
|---|---|---|
| `max_vibration_mm_s` | > 3.5 | > 5.0 |
| `max_temperature_c` | > 65 | > 70 |
| `avg_cycle_time_sec` | > 50 | > 60 |

When any threshold is exceeded, produce a record to `factory.exceptions`. Include `severity`, `machine_id`, `line_id`, `title`, `description`, and `recommended_action`. The schema must match the existing [`app/schemas/factory_exception.json`](../app/schemas/factory_exception.json).

**Job 3 — Factory state derivation**

Join `factory.machine.metrics` with recent `factory.quality.events` and `factory.production.events` over a 5-minute interval to produce a correlated `factory.state` record per machine. The output schema must match [`app/schemas/factory_state.json`](../app/schemas/factory_state.json).

Field mapping:

| `factory.state` field | Source |
|---|---|
| `vibration_mm_s` | `avg_vibration_mm_s` from metrics |
| `temperature_c` | `avg_temperature_c` from metrics |
| `cycle_time_sec` | `avg_cycle_time_sec` from metrics |
| `defect_rate_pct` | latest defect rate from `factory.quality.events` |
| `produced_units` | latest count from `factory.production.events` |
| `projected_units` | computed as `produced_units / elapsed_shift_fraction` |
| `machine_health` | derived: healthy / warning / critical from threshold matrix |
| `production_risk` | derived from `projected_units` vs target |
| `quality_risk` | derived from `defect_rate_pct` |
| `overall_risk` | `MAX(machine_health, production_risk, quality_risk)` |
| `root_signal` | plain-text summary generated in Flink SQL via `CASE` statements |
| `recommendation` | plain-text action from threshold matrix |

#### G1-2 Add `factory.machine.metrics` topic to Terraform

Add a `confluent_kafka_topic` resource for `factory.machine.metrics` in [`infra/confluent/terraform/main.tf`](../infra/confluent/terraform/main.tf):

```hcl
resource "confluent_kafka_topic" "machine_metrics" {
  topic_name       = "factory.machine.metrics"
  partitions_count = 3
  config = {
    "cleanup.policy" = "compact"
    "retention.ms"   = "3600000"
  }
  ...
}
```

Add `TOPIC_MACHINE_METRICS=factory.machine.metrics` to the generated `.env` output and to [`app/config.py`](../app/config.py).

#### G1-3 Update `confluent-resource-map.md`

Add `factory.machine.metrics` row. Update the Flink column for `factory.state` and `factory.exceptions` to reference `factory_operations.sql`.

#### G1-4 Add a JSON schema for `factory.machine.metrics`

Create `app/schemas/machine_metrics.json` following the same structure as `factory_state.json`.

#### G1-5 Update the demo script and architecture docs

Update [`docs/DEMO_SCRIPT.md`](DEMO_SCRIPT.md) to explain that when `RAG_PIPELINE_MODE=flink`, the Flink operational pipeline drives state and exception events. Explain that the Python demo step buttons are a shortcut that bypasses Flink for quick demos.

Update [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) to show `factory_operations.sql` as the implementation of the "join · detect" Flink role.

---

### G2 — Tableflow materialization

#### G2-1 Add Tableflow Terraform resources

Add the following to [`infra/confluent/terraform/main.tf`](../infra/confluent/terraform/main.tf), gated by a new `enable_tableflow` variable (default `false`):

```hcl
variable "enable_tableflow" {
  description = "Enable Tableflow materialization for factory.state and factory.exceptions"
  type        = bool
  default     = false
}

resource "confluent_tableflow" "factory_state" {
  count        = var.enable_tableflow ? 1 : 0
  display_name = "factory-state-tableflow"

  kafka_cluster {
    id = confluent_kafka_cluster.main.id
  }

  environment {
    id = confluent_environment.main.id
  }

  topic_name = confluent_kafka_topic.factory_state.topic_name

  # Storage config — replace with actual storage integration
  # credentials { ... }
  depends_on = [confluent_kafka_topic.factory_state]
}

resource "confluent_tableflow" "factory_exceptions" {
  count        = var.enable_tableflow ? 1 : 0
  display_name = "factory-exceptions-tableflow"

  kafka_cluster {
    id = confluent_kafka_cluster.main.id
  }

  environment {
    id = confluent_environment.main.id
  }

  topic_name = confluent_kafka_topic.factory_exceptions.topic_name

  depends_on = [confluent_kafka_topic.factory_exceptions]
}
```

Add `enable_tableflow` to [`infra/confluent/terraform/variables.tf`](../infra/confluent/terraform/variables.tf) and `terraform.tfvars`.

#### G2-2 Add a `TABLEFLOW_ENABLED` config flag

Add to [`app/config.py`](../app/config.py):

```python
tableflow_enabled: bool = Field(default=False, alias="TABLEFLOW_ENABLED")
tableflow_topics: list[str] = Field(
    default_factory=lambda: ["factory.state", "factory.exceptions"],
    alias="TABLEFLOW_TOPICS",
)
```

Include `tableflow_enabled` in `Settings.safe_summary()` so the UI can display it.

#### G2-3 Add a `/api/tableflow/status` endpoint

Add to [`app/main.py`](../app/main.py):

```
GET /api/tableflow/status
```

Response:

```json
{
  "enabled": true,
  "materialized_topics": ["factory.state", "factory.exceptions"],
  "note": "Tableflow materializes these topics as Iceberg/Delta tables for historical analytics. It is not in the synchronous RAG path."
}
```

This gives the UI something live to display rather than static text.

#### G2-4 Update the Settings UI panel

In [`app/static/index.html`](../app/static/index.html), add a Tableflow card to the Settings grid:

```html
<article class="setting-card">
  <span class="eyebrow">Tableflow</span>
  <strong id="settingTableflow">—</strong>
  <p>Iceberg / Delta materialization for factory.state and factory.exceptions</p>
</article>
```

Populate `settingTableflow` in [`app/static/app.js`](../app/static/app.js) from `/api/tableflow/status`.

#### G2-5 Update the Streamhouse architecture view

In the Streamhouse panel in [`app/static/index.html`](../app/static/index.html), add a descriptive note under the Tableflow architecture node explaining that it exposes historical data to Iceberg/Delta tables for analytical consumption (separate from the live RAG path).

#### G2-6 Add `docs/TABLEFLOW_SETUP.md`

Create a new documentation file explaining:

- what Tableflow does in the FactoryPulse context,
- which topics are materialized and why,
- how to enable it via Terraform (`enable_tableflow = true`),
- that it is an analytical path and must not be confused with the low-latency RAG retrieval path,
- expected Iceberg/Delta output and how a downstream analytics tool would consume it.

#### G2-7 Update `ARCHITECTURE.md`

Expand the "Streamhouse analytical path" section with specifics on which topics feed Tableflow and where the materialized tables would land.

---

### G3 — Schema Registry active by default

#### G3-1 Change the default serialization logic in `Settings`

Modify [`app/config.py`](../app/config.py) to derive the effective serialization mode:

```python
@property
def effective_serialization_mode(self) -> str:
    """
    Returns 'schema-registry-json' if Schema Registry credentials are present
    and SERIALIZATION_MODE was not explicitly set to 'plain-json'.
    Falls back to 'plain-json' if credentials are absent.
    """
    if self.serialization_mode == "plain-json" and self.schema_registry_ready:
        return "schema-registry-json"
    return self.serialization_mode
```

Replace all internal uses of `settings.serialization_mode` in `KafkaGateway` with `settings.effective_serialization_mode`.

**Note:** `serialization_mode` retains its raw value from the environment variable so that an explicit `SERIALIZATION_MODE=plain-json` still overrides the auto-detection.

#### G3-2 Update `KafkaGateway` to use `effective_serialization_mode`

In [`app/services/kafka.py`](../app/services/kafka.py), replace every reference to `self.settings.serialization_mode` with `self.settings.effective_serialization_mode`. The `_configure_schema_registry_if_requested`, `_encode`, and `_decode` methods are the three affected sites.

#### G3-3 Surface `effective_serialization_mode` in the Settings UI

Update `Settings.safe_summary()` to include:

```python
"effective_serialization_mode": self.effective_serialization_mode,
```

Update the RAG pipeline settings card in the UI to show both the configured mode and the effective mode so operators can see whether Schema Registry was auto-activated.

#### G3-4 Update `SERIALIZATION_MODE` documentation

Update [`README.md`](../README.md) and [`specs/TECHNICAL_SPEC.md`](TECHNICAL_SPEC.md) to document the new auto-detection behaviour:

- If `SERIALIZATION_MODE` is not set and Schema Registry credentials are present → `schema-registry-json` is used automatically.
- Set `SERIALIZATION_MODE=plain-json` explicitly to override.
- Set `SERIALIZATION_MODE=schema-registry-json` to enforce Schema Registry even during startup validation.

#### G3-5 Update Terraform `.env` output

In [`infra/confluent/terraform/main.tf`](../infra/confluent/terraform/main.tf), update the generated `.env` template to emit `SERIALIZATION_MODE=schema-registry-json` for STANDARD clusters (where the Flink profile is used and Schema Registry governs all topics). Retain `plain-json` for BASIC clusters where SR is present but not in the active Flink data path.

---

## Acceptance criteria

### G1

- [ ] `infra/flink/factory_operations.sql` exists and is syntactically valid Flink SQL.
- [ ] The file contains three clearly labelled jobs: telemetry aggregation, exception detection, factory state derivation.
- [ ] The threshold matrix in the SQL matches the values used by the Python demo step stubs in [`app/main.py`](../app/main.py) for consistency.
- [ ] `factory.machine.metrics` topic is defined in Terraform and in `app/config.py`.
- [ ] `app/schemas/machine_metrics.json` exists.
- [ ] `docs/DEMO_SCRIPT.md` explains when the Flink pipeline replaces the Python step buttons.
- [ ] `docs/ARCHITECTURE.md` references `factory_operations.sql`.
- [ ] `python -m compileall app` passes.
- [ ] `pytest -q` passes.

### G2

- [ ] `enable_tableflow` variable exists in `variables.tf` and `terraform.tfvars` (default `false`).
- [ ] `confluent_tableflow` resources are defined in `main.tf` and guarded by `count = var.enable_tableflow ? 1 : 0`.
- [ ] `GET /api/tableflow/status` returns a valid JSON response with `enabled`, `materialized_topics`, and `note`.
- [ ] The Settings UI panel shows a Tableflow card populated from the API.
- [ ] `docs/TABLEFLOW_SETUP.md` exists and covers: purpose, topics, enable steps, analytical path distinction.
- [ ] `docs/ARCHITECTURE.md` is updated.
- [ ] `python -m compileall app` passes.
- [ ] `pytest -q` passes.

### G3

- [ ] `Settings.effective_serialization_mode` property exists and returns `schema-registry-json` when SR credentials are present and `SERIALIZATION_MODE` is not explicitly `plain-json`.
- [ ] All three affected sites in `kafka.py` use `effective_serialization_mode`.
- [ ] `safe_summary()` includes `effective_serialization_mode`.
- [ ] Existing tests pass without SR credentials configured (i.e. fallback to `plain-json` still works).
- [ ] `README.md` and `TECHNICAL_SPEC.md` document the auto-detection logic.
- [ ] Terraform `.env` output for STANDARD clusters sets `SERIALIZATION_MODE=schema-registry-json`.
- [ ] `python -m compileall app` passes.
- [ ] `pytest -q` passes.

---

## Execution order

The three gaps are independently implementable but the following sequencing minimises rework:

```
G3 (Schema Registry default-on)
  → G1 (Flink operational pipeline)        ← benefits from SR being active
  → G2 (Tableflow materialization)         ← Tableflow works cleanest on SR-governed topics
```

G3 is purely additive in Python and Terraform. Doing it first means the Flink SQL in G1 and the Tableflow resources in G2 can assume `schema-registry-json` serialization as the baseline.

---

## Files changed per gap

### G1

| File | Change |
|---|---|
| `infra/flink/factory_operations.sql` | **New** — Flink SQL for operational correlation |
| `app/schemas/machine_metrics.json` | **New** — JSON schema for intermediate metrics topic |
| `infra/confluent/terraform/main.tf` | Add `factory.machine.metrics` topic resource |
| `infra/confluent/terraform/variables.tf` | No change |
| `app/config.py` | Add `topic_machine_metrics` field |
| `.bob/skills/streamhouse-continuous-rag/support/confluent-resource-map.md` | Add `factory.machine.metrics` row |
| `docs/ARCHITECTURE.md` | Reference `factory_operations.sql` |
| `docs/DEMO_SCRIPT.md` | Explain Flink vs Python step path |

### G2

| File | Change |
|---|---|
| `infra/confluent/terraform/main.tf` | Add `confluent_tableflow` resources and `enable_tableflow` variable |
| `infra/confluent/terraform/variables.tf` | Add `enable_tableflow` variable |
| `infra/confluent/terraform/terraform.tfvars` | Add `enable_tableflow = false` |
| `app/config.py` | Add `tableflow_enabled` and `tableflow_topics` fields |
| `app/main.py` | Add `GET /api/tableflow/status` endpoint |
| `app/static/index.html` | Add Tableflow Settings card; update Streamhouse view note |
| `app/static/app.js` | Populate Tableflow card from API |
| `docs/TABLEFLOW_SETUP.md` | **New** |
| `docs/ARCHITECTURE.md` | Expand analytical path section |

### G3

| File | Change |
|---|---|
| `app/config.py` | Add `effective_serialization_mode` property |
| `app/services/kafka.py` | Replace `serialization_mode` with `effective_serialization_mode` (3 sites) |
| `infra/confluent/terraform/main.tf` | Update `.env` output for STANDARD clusters |
| `README.md` | Document auto-detection |
| `specs/TECHNICAL_SPEC.md` | Document auto-detection |

---

## Definition of done

All three gaps are considered closed when:

1. Every acceptance criterion checkbox above is ticked.
2. `python -m compileall app scripts tests` produces zero errors.
3. `pytest -q` produces zero failures.
4. `bash -n infra/code-engine/deploy.sh` produces zero syntax errors.
5. The Streamhouse architecture view in the UI accurately reflects what is actually implemented (no components shown that have no code backing them).
6. A reviewer reading `docs/ARCHITECTURE.md` and the Streamhouse UI panel sees a consistent picture of all four Confluent Cloud components.
