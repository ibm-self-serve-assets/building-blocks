# setup_opensearch — One-Time OpenSearch Index Creation

**Run once** before the first ingestion run. Re-run only if you delete and recreate the index.

## What it does

Defines the k-NN index mapping for `schema_embeddings` in OpenSearch:

- Sets `knn: true` with `hnsw / nmslib` engine and `cosinesimil` space type.
- Declares the `embedding` field as `knn_vector` with the correct dimension.
- Maps all enrichment fields (`indexes_json`, `referenced_by_json`, `row_count_approx`, etc.).
- Maps `column_names` and `text_agg` as `text` fields for BM25 hybrid search.

## Files

| File | Purpose |
|---|---|
| `opensearch_index_mapping.py` | Exports the `MAPPING` dict and `VECTOR_DIM` constant |

## Usage

### Option A — apply via Python + REST

```bash
cd NL2SQL/setup/opensearch
pip install -r requirements.txt
cp .env.example .env   # fill in credentials

python - <<'EOF'
import json, os
from opensearch_index_mapping import MAPPING
from opensearchpy import OpenSearch
from dotenv import load_dotenv
load_dotenv()

http_auth = (os.getenv("OS_USER"), os.getenv("OS_PASSWORD")) if os.getenv("OS_USER") else None
client = OpenSearch(
    hosts=[{"host": os.getenv("OS_HOST","localhost"), "port": int(os.getenv("OS_PORT",9200))}],
    http_auth=http_auth,
    use_ssl=os.getenv("OS_USE_SSL","false").lower()=="true",
    verify_certs=os.getenv("OS_VERIFY_CERTS","false").lower()=="true",
)
idx = os.getenv("OS_INDEX","schema_embeddings")
if not client.indices.exists(idx):
    client.indices.create(idx, body=MAPPING)
    print(f"Index '{idx}' created.")
else:
    print(f"Index '{idx}' already exists — skipped.")
EOF
```

### Option B — apply via OpenSearch Dashboards Dev Tools

```
PUT /schema_embeddings
{ ... paste MAPPING body from opensearch_index_mapping.py ... }
```

## When to re-run

| Scenario | Action |
|---|---|
| Changing embedding model (different `VECTOR_DIM`) | Delete the index, update `VECTOR_DIM`, re-apply, then re-run ingestion |
| Adding new enrichment fields | Update `MAPPING`, delete the index, re-apply |
