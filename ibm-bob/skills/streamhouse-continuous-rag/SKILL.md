---
name: streamhouse-continuous-rag
description: Build, review, explain, and extend the FactoryPulse Continuous RAG Streamhouse demo on Confluent Cloud. Use this skill for Kafka/Flink continuous knowledge ingestion, manufacturing exception-to-action flows, RAG freshness, Confluent configuration, API/UI changes, Bob-assisted development, and IBM Code Engine deployment in this repository.
---

# Streamhouse Continuous RAG

Use this skill when working on the FactoryPulse project or when the user asks for a Confluent Cloud Streamhouse implementation centered on **Continuous RAG**.

## Start here

Before changing code, read:

1. `README.md`
2. `docs/ARCHITECTURE.md`
3. `docs/TECHNICAL_SPEC.md`
4. The relevant file under `support/` in this skill.

Treat those files as the project contract. If code and documentation disagree, fix both in the same change.

## Architecture invariants

Preserve these design principles unless the user explicitly asks to change them:

- Python runtime is **3.12** and the backend is **FastAPI**.
- **Confluent Cloud Kafka is the event backbone**. Do not turn Continuous RAG into a scheduled/nightly document-loading job.
- New or changed knowledge enters `rag.knowledge.raw` as an event.
- Knowledge chunks/embeddings are materialized continuously to `rag.knowledge.embeddings`.
- Questions and knowledge must use the **same embedding model** in the managed Flink profile.
- Every RAG answer must return its retrieved evidence. Never hide the grounding path.
- The manufacturing story must connect machine condition, production impact, quality impact, and maintenance knowledge.
- Tableflow is the analytical/history path. Do not place Tableflow in the low-latency interactive RAG request path.
- Never hardcode Confluent, Schema Registry, IBM Cloud, or watsonx.ai secrets in source, examples, screenshots, or logs.
- Keep the UI enterprise-oriented, responsive, and operational rather than looking like a generic chatbot.

## Choose the correct RAG profile

### `local`
Use this for the fastest demo or development loop.

- Consume `rag.knowledge.raw` in Python.
- Chunk documents in Python.
- Generate deterministic demo embeddings.
- Publish chunks to `rag.knowledge.embeddings`.
- Replay the compacted embedding topic to rebuild the read index.

Always explain that the deterministic embedding is a **demo fallback**, not a production semantic embedding model.

### `flink`
Use this for the strongest Confluent-native demo.

- Use `ML_RECURSIVE_TEXT_SPLITTER` for continuous chunking.
- Use `AI_EMBEDDING` for both knowledge and question embeddings.
- Keep Kafka topics as durable event/materialization boundaries.
- For larger deployments, use `VECTOR_SEARCH_AGG` with a supported external vector database instead of an in-process index.

Use `infra/flink/continuous_rag.sql` as the starting point.

## Industry Blueprint & Implementation Examples

Continuous RAG applies to event-driven enterprise domains where operational state and operational knowledge must stay synchronized in real time.

### 1. Discrete & Process Manufacturing (Factory Operations)
- **Use Case:** Machine degradation, tooling wear, SOP updates, and work-order resolution feedback loops.
- **Event Flow:**
  1. Sensor telemetry emits high vibration / temperature alert on an asset (e.g., `CNC-03` spindle).
  2. Telemetry and MES events trigger an exception in `factory.exceptions`.
  3. Field technician resolves the incident and closes maintenance work order `WO-11023` (e.g., "replaced worn spindle bearing, applied torque spec 45Nm").
  4. CMMS/App publishes resolution note as a `KnowledgeDocument` event directly to `rag.knowledge.raw`.
  5. Streamhouse continuously chunks and embeds the document into `rag.knowledge.embeddings`.
  6. **Operator Query:** *"What is the standard procedure when CNC-03 shows vibration spikes over 4.5 mm/s?"* → Model immediately retrieves `WO-11023` resolution without batch re-indexing.

### 2. Supply Chain & Logistics
- **Use Case:** Supplier disruption notices, carrier route delays, port strikes, and customs advisory bulletins.
- **Event Flow:**
  1. ERP/Logistics gateway streams carrier delay notifications and customs policy changes to `rag.knowledge.raw`.
  2. Embeddings are materialized on the fly to `rag.knowledge.embeddings`.
  3. **Planner Query:** *"Which alternate distribution routes are approved for cold-chain shipments impacted by Port X congestion?"* → Model answers using live supplier and logistics advisories received seconds ago.

### 3. Energy & Utilities (Grid & Turbines)
- **Use Case:** Substation relay trips, turbine fault codes, shift handover logs, and environmental compliance notices.
- **Event Flow:**
  1. SCADA systems capture turbine vibration and thermal anomalies.
  2. Shift supervisor logs a shift-handover note detailing transient grid load adjustments.
  3. Handover log is streamed as an event to `rag.knowledge.raw`.
  4. **Control Room Query:** *"Has Turbine-4 shown similar transient thermal trips during peak grid load this month?"* → RAG synthesizes real-time SCADA state with newly logged handover notes.

### 4. Healthcare & Clinical Equipment Operations
- **Use Case:** Medical device error codes, biomedical engineering calibrations, urgent FDA/regulatory recall bulletins.
- **Event Flow:**
  1. Hospital asset management system streams biomedical maintenance and calibration records.
  2. Regulatory recall advisory is streamed to `rag.knowledge.raw`.
  3. **Biomedical Engineer Query:** *"Are there active recall alerts or special calibration steps for Infusion Pump Model X?"* → Immediate, verifiable recall retrieval with exact document provenance.

---

## When adding a new knowledge source

1. Identify the business event that indicates knowledge changed (e.g., closed work order, revised standard operating procedure, supplier bulletin, shift handover log).
2. Map it to `KnowledgeDocument` or add a versioned schema:
   ```json
   {
     "document_id": "doc-mfg-cnc03-wo11023",
     "title": "WO-11023 Spindle Bearing Resolution",
     "source": "CMMS_MAXIMO",
     "asset_id": "CNC-03",
     "content": "Technician replaced spindle bearing B-442. Vibration reduced from 4.8 mm/s to 0.9 mm/s. Recommended inspection interval: 200 operating hours.",
     "updated_at": "2025-03-30T10:15:00Z",
     "metadata": {"plant": "Austin-01", "line": "Line-A", "technician": "TECH-409"}
   }
   ```
3. Publish the event to `rag.knowledge.raw` with a stable `document_id`.
4. Include `source`, `asset_id`, `updated_at`, and useful metadata.
5. Verify the continuous pipeline creates new embeddings in `rag.knowledge.embeddings`.
6. Ask a query that proves the newly streamed information is retrievable.
7. Update `docs/DEMO_SCRIPT.md` if the source changes the demo story.

Do not add a manual “rebuild index” step unless the user explicitly asks for a disaster-recovery utility.

## When changing Kafka topics or schemas

Use `support/confluent-resource-map.md` as the resource map.

For each changed topic:

- Update `app/config.py`.
- Update `scripts/create_topics.py`.
- Update/add a JSON Schema under `app/schemas/` if Schema Registry serialization is supported for it.
- Update Flink SQL if the topic participates in managed processing.
- Update `README.md` and `docs/ARCHITECTURE.md`.
- Prefer stable keys for streams that represent current state or upsert materializations.

## When changing RAG behavior

Use `support/architecture-checklist.md`.

Check that:

- chunking is deterministic enough to produce stable identities,
- query and chunk embedding dimensions/models match,
- retrieval returns source metadata,
- empty/insufficient evidence is handled safely,
- generated answers are instructed to stay within retrieved evidence,
- new knowledge can be observed without restarting or rebuilding a static corpus.

## When changing the UI

Keep the current interaction pattern:

- Operations Overview = live manufacturing state.
- Continuous RAG = question, answer, freshness, evidence.
- Knowledge = show/publish knowledge events.
- Streamhouse = explain the data path and Confluent components.
- Live Events = expose event movement for the demo.
- Settings = show configuration readiness, never secret values.

Use semantic HTML, accessible labels, responsive CSS, and no secret/config value rendering.

## When changing deployment

The deployment target is IBM Cloud Code Engine.

- Keep the service stateless at the container filesystem level.
- Listen on `0.0.0.0:$PORT` (default `8080`).
- Keep secrets in Code Engine secrets and inject them as environment variables.
- Keep the container non-root.
- Do not bake `.env` into the image.
- Update `infra/code-engine/deploy.sh` and `docs/DEPLOY_CODE_ENGINE.md` together.

## Validation before finishing

Run at minimum:

```bash
python -m compileall app scripts tests
pytest -q
bash -n infra/code-engine/deploy.sh
```

If Confluent credentials are available, also run:

```bash
python scripts/create_topics.py --profile local
```

Then exercise the demo in this order:

1. Seed knowledge.
2. Baseline.
3. Degrade.
4. Critical.
5. Ask the CNC-03 vibration question.
6. Resolve + Learn.
7. Ask what changed after WO-11023.

The final step is the proof of Continuous RAG freshness.

## How to explain this project

Use this framing:

> Kafka is the shared event backbone, Flink continuously turns changing data into usable context and embeddings, Continuous RAG keeps AI knowledge current as the factory changes, and Tableflow exposes selected streams to the analytical lakehouse world.

Avoid describing Streamhouse as only a message broker or only a database.

See `support/demo-prompts.md` for demo questions and talking points.
