# embedding — Schema Ingestion & Embedding Pipeline

**Run on demand** — after initial setup and whenever the source database schema changes.

## What it does

1. Connects to one or more source databases (PostgreSQL, Db2) **in parallel**.
2. Introspects every schema/table → builds a fully-enriched `SchemaDoc` per table (columns, PKs, FKs, indexes, sample rows, enum values, row counts).
3. Converts each `SchemaDoc` to a text blob via `to_text()`.
4. Embeds the text with **watsonx Granite** or **sentence-transformers** (auto-selected).
5. Upserts each document into the OpenSearch `schema_embeddings` k-NN index.

## Files

| File | Purpose |
|---|---|
| `ingest_opensearch.py` | Main ingestion script (OpenSearch target) |
| `ingest_pgvector.py` | Legacy ingestion script (pgvector/Postgres target) |
| `embedders.py` | Shared `WatsonxEmbedding` + `LocalSTEmbedding` providers |
| `connectors/base.py` | `SchemaDoc` dataclass + `to_text()` |
| `connectors/postgresql.py` | PostgreSQL introspection (reverse FKs, row counts, enums, indexes) |
| `connectors/db2.py` | Db2 introspection (SYSCAT views, COLCARD-based enum detection) |

## Usage

```bash
cd NL2SQL/embedding
pip install -r requirements.txt
cp .env.example .env   # fill in source DB + OpenSearch + embedding credentials

# PostgreSQL only, local sentence-transformers
EMBED_PROVIDER=st SOURCE_TYPES=postgresql python ingest_opensearch.py

# PostgreSQL + Db2, watsonx embeddings
SOURCE_TYPES=postgresql,db2 EMBED_PROVIDER=watsonx python ingest_opensearch.py
```

## When to re-run

| Scenario | Action |
|---|---|
| New table added to source DB | Re-run ingestion |
| Table schema changed | Re-run ingestion (upserts by `table_id`) |
| Embedding model changed | Delete OpenSearch index, re-create via `setup_opensearch`, re-run |
| Scheduled refresh | Set up a CronJob to run this on a schedule |
