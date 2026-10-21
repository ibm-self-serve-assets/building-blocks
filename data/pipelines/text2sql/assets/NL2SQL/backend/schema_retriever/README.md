# schema_retriever — Schema Retrieval API (called by LLM)

**Always-on FastAPI service.** The LLM calls `POST /retrieve-schema` with a natural-language question and receives the most relevant table schemas to use when writing SQL.

## What it does

- Embeds the incoming user question with the same provider used during ingestion.
- Runs a k-NN (or hybrid k-NN + BM25) search against the OpenSearch `schema_embeddings` index.
- Returns ranked table schemas: columns, PKs, FKs, sample rows, enum values, dialect-aware SQL sketches.
- Filters by `min_score` to discard low-confidence matches.

## Files

| File | Purpose |
|---|---|
| `schema_retriever_opensearch.py` | FastAPI app — OpenSearch backend (production) |
| `schema_retriever_pgvector.py` | FastAPI app — pgvector/Postgres backend (alternative) |

## Usage

```bash
cd NL2SQL/backend/schema_retriever
pip install -r requirements.txt
cp .env.example .env   # fill in OpenSearch + embedding credentials

uvicorn schema_retriever_opensearch:app --host 0.0.0.0 --port 8080
```

## API

### `POST /retrieve-schema`

```json
{
  "user_query": "find all customer orders",
  "top_k": 5,
  "schema_filter": ["public"],
  "db_alias_filter": ["mydb"]
}
```

Returns a ranked list of matching table schemas with `confidence` scores.

### `POST /retrieve-schema/hybrid`

```json
{
  "user_query": "find all customer orders",
  "top_k": 5,
  "schema_filter": ["public"],
  "db_alias_filter": ["mydb"],
  "keyword_weight": 0.3,
  "knn_weight": 0.7
}
```

Performs hybrid retrieval combining k-NN vector similarity and BM25 full-text matching.

### `GET /health`

Returns `{"ok": true}` when the service is running and OpenSearch is reachable.

## Deployment (IBM Cloud Code Engine)

See `docker-build/schema-retriever/` for the Dockerfile, `ce-app.yaml`, and `build.sh`.
