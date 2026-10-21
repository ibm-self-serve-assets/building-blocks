-- pgvector_schema.sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS schema_embeddings (
    table_id TEXT PRIMARY KEY,           -- schema.table
    schema_name TEXT NOT NULL,
    table_name TEXT NOT NULL,
    columns_json JSONB,
    pk_json JSONB,
    fk_json JSONB,
    sample_rows_json JSONB,
    text_agg TEXT,
    embedding vector(384)                -- adjust dims to your embedding model
);

-- Index for faster nearest neighbor (requires pgvector index support)
-- Example: ivfflat index (requires setting number of lists tuned to dataset size)
-- CREATE INDEX ON schema_embeddings USING ivfflat (embedding) WITH (lists = 100);

-- GIN index for text search on table_name and text_agg
CREATE INDEX IF NOT EXISTS idx_schema_text ON schema_embeddings USING gin ((to_tsvector('english', coalesce(table_name, '') || ' ' || coalesce(text_agg, ''))));
