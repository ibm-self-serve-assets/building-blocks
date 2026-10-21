"""
opensearch_index_mapping.py

Reference index mapping for the schema_embeddings k-NN index.
Use this to create or update the index manually via the OpenSearch REST API
or the OpenSearch Dashboards Dev Tools console.

Apply with:
  PUT /schema_embeddings
  <body of MAPPING below>

Notes
-----
• VECTOR_DIM: Change to match your embedding model output dimension.
  - BAAI/bge-base-en-v1.5                      → 768  (default local model)
  - ibm-granite/granite-embedding-125m-english → 768  (default watsonx model)
  - ibm-granite/granite-embedding-278m-english → 1024
  - ibm-granite/granite-embedding-30m-english  → 384
  - BAAI/bge-large-en-v1.5                     → 1024
  - BAAI/bge-m3                                → 1024
  - all-MiniLM-L6-v2                           → 384
  - all-mpnet-base-v2                          → 768
  - text-embedding-ada-002 (OpenAI)            → 1536

  Override at runtime with: VECTOR_DIM env var (used by ingest_opensearch.py
  when the model is not in the static _MODEL_DIMS table).

• hnsw / nmslib is the recommended engine for Amazon OpenSearch Service
  and self-hosted OpenSearch ≥ 1.0. Use "faiss" as engine for GPU nodes.

• ef_construction=512 and m=16 give good recall/performance balance.
  Increase m to 32 for higher recall at the cost of memory.

• space_type is cosinesimil — requires normalize_embeddings=True at embed time.
  Both watsonx and sentence-transformers providers normalise automatically.
  Scores are in [0, 1]; tune MIN_SCORE env var (default 0.40) to filter noise.

Enrichment fields
-----------------
The following fields are populated by ingest_opensearch.py and returned by
the /retrieve-schema endpoint.  They are stored as disabled objects (not
full-text indexed) to avoid mapping explosions:

  indexes_json        — list of non-PK indexes: name, columns, is_unique
  referenced_by_json  — reverse FK refs: list of "schema.table.col" strings
  row_count_approx    — approximate row count (long); from pg_stat / SYSCAT stats
  column_count        — number of columns (integer)
  column_names        — space-separated column names; text field for BM25 boost
  unique_columns      — column names with UNIQUE constraint (keyword list)
  enum_values_json    — per-column distinct value map (disabled object)
"""

VECTOR_DIM = 768

MAPPING = {
    "settings": {
        "index": {
            "knn": True,
            "knn.algo_param.ef_search": 512,
            "number_of_shards": 1,
            "number_of_replicas": 1,
        }
    },
    "mappings": {
        "properties": {
            # ---- identity ----
            "table_id":    {"type": "keyword"},
            "source_type": {"type": "keyword"},
            "db_alias":    {"type": "keyword"},
            "schema_name": {"type": "keyword"},
            "table_name": {
                "type": "keyword",
                "fields": {"text": {"type": "text", "analyzer": "english"}},
            },
            # ---- schema metadata ----
            "table_comment":    {"type": "text", "analyzer": "english"},
            "columns_json":     {"type": "object", "enabled": False},
            "pk_json":          {"type": "keyword"},
            "fk_json":          {"type": "object", "enabled": False},
            "sample_rows_json": {"type": "object", "enabled": False},
            # ---- enrichment fields ----
            "indexes_json":       {"type": "object", "enabled": False},
            "referenced_by_json": {"type": "object", "enabled": False},
            "row_count_approx":   {"type": "long"},
            "column_count":       {"type": "integer"},
            # searchable flat lists for BM25 boost
            "column_names": {
                "type":     "text",
                "analyzer": "english",
                "fields":   {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "unique_columns":   {"type": "keyword"},
            "enum_values_json": {"type": "object", "enabled": False},
            # ---- embedding text (BM25 search target) ----
            "text_agg": {
                "type":     "text",
                "analyzer": "english",
                "fields":   {"keyword": {"type": "keyword", "ignore_above": 512}},
            },
            # ---- vector ----
            "embedding": {
                "type":      "knn_vector",
                "dimension": VECTOR_DIM,
                "method": {
                    "name":       "hnsw",
                    "engine":     "nmslib",
                    "space_type": "cosinesimil",
                    "parameters": {"ef_construction": 512, "m": 16},
                },
            },
        }
    },
}
