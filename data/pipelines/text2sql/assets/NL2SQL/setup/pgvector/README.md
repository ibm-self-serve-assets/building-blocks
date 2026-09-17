# setup_pgvector — First-Time PostgreSQL Bootstrap

**Run once** the very first time you deploy. Re-run only if you add a new source schema or recreate the database.

## What it does

- Enables the `pgvector` extension on the target PostgreSQL database.
- Creates the partitioned `schema_embeddings` parent table with the correct `VECTOR(n)` column.
- Creates one child partition per schema (e.g. `schema_embeddings_p_public`).
- Creates an `ivfflat` vector index on each partition for fast ANN search.
- Idempotent — safe to re-run; existing tables and indexes are not touched.

## Files

| File | Purpose |
|---|---|
| `bootstrap_embeddings_schema.py` | Creates the full table/index structure in Postgres |
| `sql/pgvector_schema.sql` | Reference DDL for the base (non-partitioned) table |
| `sql/embedding_schema.sql` | Alternative flat DDL with ivfflat index |

## Usage

```bash
cd NL2SQL/setup/pgvector
pip install -r requirements.txt
cp .env.example .env   # fill in credentials
python bootstrap_embeddings_schema.py
```

## When to re-run

| Scenario | Action |
|---|---|
| Adding a new source schema | Re-run — creates the missing partition and index |
| Changing embedding model (different `VECTOR_DIM`) | Drop the table, update `VECTOR_DIM` in `.env`, re-run |
