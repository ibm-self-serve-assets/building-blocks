# Serverless Vector

**IBM products**: IBM watsonx.data — Astra DB service, IBM watsonx.ai, IBM Cloud Object Storage

Reference assets for serverless vector ingestion/search and NoSQL document access using the Astra DB service available through IBM watsonx.data.

> Service availability depends on watsonx.data deployment type, cloud provider, and region. Check the current IBM availability matrix before designing around this service.

## Architecture

```text
IBM Cloud Object Storage
          |
          v
     document loader
          |
          v
    IBM watsonx.ai
       embeddings
          |
          v
IBM watsonx.data
   Astra DB service
          |
          +--> vector similarity search
          +--> NoSQL document CRUD
```

## Included assets

| Path | Purpose |
|---|---|
| [`assets/astradb-vector-ingestion/`](assets/astradb-vector-ingestion/) | COS -> watsonx.ai embeddings -> Astra DB vector collection |
| [`assets/astradb-nosql-crud/`](assets/astradb-nosql-crud/) | FastAPI document CRUD service using the Astra Data API |
| [`bob-modes/`](bob-modes/) | IBM Bob modes for vector and NoSQL patterns |
| [`bob-skills/`](bob-skills/) | IBM Bob skills for vector setup and document modeling |

## Quick start: vector ingestion

```bash
cd assets/astradb-vector-ingestion
cp .env.example .env
# Configure IBM Cloud/watsonx.ai plus Astra DB endpoint/token values.
pip install -r requirements.txt
python main.py
# Swagger UI: http://localhost:8080/docs
```

## Quick start: NoSQL CRUD

```bash
cd assets/astradb-nosql-crud
cp .env.example .env
# Configure ASTRA_DB_API_ENDPOINT and ASTRA_DB_APPLICATION_TOKEN.
pip install -r requirements.txt
python main.py
# Swagger UI: http://localhost:8080/docs
```

See the asset READMEs for payload examples and Docker commands.

## Embedding model

Current example:

```text
EMBEDDING_MODEL_ID=ibm/granite-embedding-278m-multilingual
```

The example model produces 768-dimensional embeddings in current watsonx.ai documentation. Keep the collection/index dimension aligned with the actual model you deploy.

- Supported embedding models: https://www.ibm.com/docs/en/watsonx/saas?topic=models-supported-embedding
- Model lifecycle: https://www.ibm.com/docs/en/watsonx/saas?topic=model-foundation-lifecycle

## Service selection

For a vector-store option provisioned directly in watsonx.data, also evaluate **Milvus**. Keep Astra DB when its serverless vector + NoSQL characteristics fit the application and it is available in the target deployment.

## Production checklist

- Validate Astra DB availability in the target cloud/region.
- Protect the Astra application token and service credentials.
- Create collection dimensions from the selected embedding model.
- Define metadata/filtering strategy before bulk ingestion.
- Test retrieval quality and latency with representative data.
- Re-index if you change to a model with incompatible dimensions.

## IBM references

- Add Astra DB service in watsonx.data: https://www.ibm.com/docs/en/watsonxdata/saas?topic=watsonxdata-adding-astra-db-service
- watsonx.data availability matrix: https://cloud.ibm.com/docs/watsonxdata?topic=watsonxdata-feature_parity_wxd
- Add Milvus service: https://cloud.ibm.com/docs/watsonxdata?topic=watsonxdata-adding-milvus-service
- IBM watsonx.ai: https://www.ibm.com/products/watsonx-ai
