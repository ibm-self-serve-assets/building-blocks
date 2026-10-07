# Technical specification

## Runtime

- Python 3.12
- FastAPI
- Uvicorn
- confluent-kafka Python client
- optional httpx calls to watsonx.ai
- static HTML/CSS/JavaScript UI

## Non-functional targets for the demo

- no secret values returned to browser,
- startup can rebuild RAG read index from Kafka,
- new knowledge becomes searchable without an explicit batch reindex command,
- every RAG response contains retrieved evidence,
- application container is stateless and non-root,
- deployment works with Code Engine local-source Dockerfile build.

## Demo-mode retrieval

`HashEmbeddingModel` is a deterministic feature-hashing vectorizer. It provides zero-extra-service retrieval for the demo, but it is not a semantic embedding model. Use Flink `AI_EMBEDDING` or another production embedding service for realistic semantic quality.

## Serialization and Schema Registry

`SERIALIZATION_MODE` controls how Kafka messages are encoded:

- `plain-json` — raw JSON bytes, no Schema Registry involvement. Default when SR credentials are absent.
- `schema-registry-json` — messages are wrapped with the Confluent wire format and the schema is registered/validated against Schema Registry.

**Auto-detection:** when `CONFLUENT_SCHEMA_REGISTRY_URL`, `CONFLUENT_SCHEMA_REGISTRY_API_KEY`, and `CONFLUENT_SCHEMA_REGISTRY_API_SECRET` are all set and `SERIALIZATION_MODE` is not explicitly `plain-json`, the app automatically uses `schema-registry-json`. The `effective_serialization_mode` field in `GET /api/config` shows which mode is actually active.

To opt out of auto-detection and keep plain JSON even when SR credentials are present:

```bash
SERIALIZATION_MODE=plain-json
```

The in-memory read index tracks the newest `updated_at` per `document_id`; chunks from older document versions remain durable in Kafka but are excluded from retrieval. A production implementation should formalize document versioning/deletion semantics and tombstones.

## Managed embedding profile

`RAG_PIPELINE_MODE=flink` changes query embedding behavior:
1. backend publishes the question to `rag.query.requests`,
2. Flink generates the query embedding with the same model used for knowledge chunks,
3. result arrives on `rag.query.embeddings`,
4. backend correlates by `request_id`,
5. retrieval searches the Kafka-replayed vector read index.

## Generation

`LLM_PROVIDER=none`:
- no remote model,
- returns an extractive evidence-led response.

`LLM_PROVIDER=watsonx`:
- gets an IBM Cloud IAM token using the API key,
- calls watsonx.ai text generation,
- sends only the question plus retrieved evidence,
- prompts the model to cite `[E1]`, `[E2]`, etc.

## Production extensions

Recommended next changes for a real implementation:
- external vector store + `VECTOR_SEARCH_AGG`,
- CDC from Maximo/MES/ERP rather than demo API writes,
- data contracts per operational topic,
- authorization-aware knowledge filtering,
- RAG evaluation and trace/audit topic,
- operational Flink derivation of `factory.state` rather than simulator values,
- alerting/work-order connector for exception-to-action.
