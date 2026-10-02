# API specification

FastAPI publishes the authoritative OpenAPI document at `/openapi.json` and Swagger UI at `/docs`.

## `GET /api/tableflow/status`

Returns Tableflow materialization status. Safe to call without credentials — returns `enabled: false` when Tableflow is not configured.

```json
{
  "enabled": false,
  "materialized_topics": [],
  "note": "Tableflow materializes factory.state and factory.exceptions as Iceberg/Delta tables for historical analytics and AI workloads. It is not in the synchronous RAG latency path."
}
```

## `GET /api/health`

Returns application, Kafka, RAG pipeline, index count, and latest factory state timestamp.

## `GET /api/config`

Returns only non-secret configuration status. API key/secret values are never returned.

## `GET /api/dashboard`

Returns the current read model used by the UI:
- latest factory state,
- recent exceptions,
- knowledge document metadata/content,
- recent UI event feed,
- indexed chunk count,
- safe configuration summary.

## `GET /api/events/stream`

Server-Sent Events endpoint. Emits a `snapshot` event approximately every two seconds.

## `POST /api/knowledge`

Publishes a new enterprise knowledge event to `rag.knowledge.raw`.

Example:

```json
{
  "title": "CNC-03 inspection finding",
  "text": "Tool-holder imbalance was confirmed...",
  "source": "maintenance-work-order",
  "asset_id": "CNC-03",
  "metadata": {"work_order": "WO-11023"}
}
```

The pipeline continuously converts the knowledge event into chunk records and embeddings.

## `GET /api/knowledge`

Returns documents observed on the knowledge stream by this running instance.

## `POST /api/rag/ask`

Request:

```json
{
  "question": "What should we inspect when CNC-03 vibration and dimensional drift rise together?",
  "top_k": 4
}
```

Response shape:

```json
{
  "answer": "...",
  "evidence": [
    {
      "chunk_id": "...",
      "document_id": "...",
      "title": "...",
      "text": "...",
      "source": "...",
      "asset_id": "CNC-03",
      "score": 0.72,
      "updated_at": "..."
    }
  ],
  "retrieval_mode": "...",
  "generation_mode": "...",
  "latency_ms": 123
}
```

## `POST /api/demo/seed-knowledge`

Publishes all Markdown documents in `demo_knowledge/` to the knowledge stream.

## `POST /api/demo/step/{step}`

Supported steps:
- `baseline`
- `degrade`
- `critical`
- `resolved`

`resolved` also publishes a new work-order resolution into `rag.knowledge.raw`, creating the key Continuous RAG demo moment.
