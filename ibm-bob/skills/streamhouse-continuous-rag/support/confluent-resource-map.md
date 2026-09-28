# Confluent resource map

| Resource | Role | Producer | Consumer / processor |
|---|---|---|---|
| `factory.machine.telemetry` | Machine/PLC signals | simulator / real gateway | factory processing / demo feed |
| `factory.production.events` | MES production changes | simulator / MES integration | factory processing |
| `factory.quality.events` | Inspection and defect events | simulator / QMS integration | factory processing |
| `factory.maintenance.events` | Maintenance operational events | CMMS / simulator | operations and analytics |
| `factory.state` | Current correlated factory state | processing/demo | FastAPI UI consumer, Tableflow candidate |
| `factory.exceptions` | Exception-to-action stream | processing/demo | FastAPI UI consumer, alert integrations, Tableflow candidate |
| `rag.knowledge.raw` | Canonical changing enterprise knowledge | API, work order/SOP integrations | local indexer or Flink chunking |
| `rag.knowledge.embeddings` | Materialized embedded chunks | local indexer or Flink | FastAPI read-index consumer / external vector sink pattern |
| `rag.query.requests` | Interactive questions needing managed embedding | FastAPI | Flink AI embedding |
| `rag.query.embeddings` | Correlated query embeddings | Flink | FastAPI query broker |

## Recommended keys

- Factory state/exception: machine or asset ID where ordering by asset matters.
- Raw knowledge: stable `document_id`.
- Embedded chunks: stable `chunk_id`.
- Query request/result: `request_id`.

## Cleanup policies

- Use compaction for materialized/current-state topics where key replacement is intended, especially `rag.knowledge.embeddings` and `rag.query.embeddings`.
- Use retention/delete for raw event streams unless the business contract calls for an upsert view.
