-- Enable pgvector extension (if not already)
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the schema if you’re using a custom one
CREATE SCHEMA IF NOT EXISTS public;

-- Create the embeddings table
CREATE TABLE public.schema_embeddings (
    table_id TEXT PRIMARY KEY,                -- "schema.table" identifier
    schema_name TEXT NOT NULL,                 -- schema of the table
    table_name TEXT NOT NULL,                  -- table name
    columns_json JSONB NOT NULL,               -- column metadata (name, type, description, is_pii)
    pk_json JSONB NOT NULL,                    -- primary key columns
    fk_json JSONB NOT NULL,                    -- foreign key info
    sample_rows_json JSONB NOT NULL,           -- masked sample rows
    text_agg TEXT NOT NULL,                    -- combined text for embedding
    embedding VECTOR(384) NOT NULL             -- vector from embedding model
);

-- Create an index for vector similarity search
CREATE INDEX IF NOT EXISTS schema_embeddings_embedding_idx
ON public.schema_embeddings
USING ivfflat (embedding vector_l2_ops)
WITH (lists = 100);
