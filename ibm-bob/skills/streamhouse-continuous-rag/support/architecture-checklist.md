# Continuous RAG architecture checklist

## Ingestion and freshness
- Knowledge changes are emitted as events, not discovered by a nightly scan.
- `document_id` is stable for a logical knowledge item.
- `updated_at`, `source`, and `asset_id` are populated where available.
- The ingestion path is observable in the Live Events view.

## Chunking and embeddings
- Chunk size and overlap are centrally configured.
- Chunk IDs are deterministic for the same document/version/chunk content.
- Knowledge and query embeddings use the same model and dimensionality.
- The local hash embedding is identified as a demo-only fallback.

## Retrieval
- Top-K is bounded.
- Each result carries title, source, asset, timestamp, text, and score.
- The answer exposes evidence to the UI/API.
- No evidence results in an explicit insufficient-knowledge response.

## Generation
- Prompt instructs the model to use only supplied evidence.
- Evidence identifiers are available for inline grounding.
- Secrets and raw credentials never enter the model prompt.

## Streamhouse separation of concerns
- Kafka/Flink are on the low-latency operational path.
- Tableflow is used for historical/analytical access, audit, and model development.
- External vector search is optional for scale; the in-process read index is a demo convenience.

## Operations
- Consumers have explicit group IDs and offset behavior.
- Materialized embedding topics are compacted where appropriate.
- Failed or malformed records are logged without printing secrets.
- Code Engine replicas can rebuild retrieval state from Kafka.
