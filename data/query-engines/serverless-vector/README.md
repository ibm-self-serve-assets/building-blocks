# Serverless Vector

**IBM products**: IBM watsonx.data — Astra DB service, IBM watsonx.ai, IBM Cloud Object Storage

Reference assets for serverless vector search and NoSQL document access using the Astra DB service available through IBM watsonx.data.

> Availability depends on watsonx.data deployment type, cloud provider, and region. Verify the current IBM availability matrix before deployment.

## Included assets

| Path | Purpose |
|---|---|
| [`assets/astradb-vector-ingestion/`](assets/astradb-vector-ingestion/) | COS → watsonx.ai embeddings → Astra DB vector collection |
| [`assets/astradb-nosql-crud/`](assets/astradb-nosql-crud/) | Reference document CRUD service |
| [`bob-modes/`](bob-modes/) | IBM Bob modes for vector and NoSQL patterns |
| [`bob-skills/`](bob-skills/) | IBM Bob skills for vector setup and document modeling |

## Model default

```text
EMBEDDING_MODEL_ID=ibm/granite-embedding-278m-multilingual
```

The current IBM model has 768 dimensions. Keep collection/index dimensions aligned with the configured model and verify the current support matrix before deployment.

- Supported embedding models: https://www.ibm.com/docs/en/watsonx/saas?topic=models-supported-embedding
- Model lifecycle: https://www.ibm.com/docs/en/watsonx/saas?topic=model-foundation-lifecycle

## IBM portfolio guidance

For a native watsonx.data vector-store option, also evaluate **Milvus in IBM watsonx.data**. Keep Astra DB when its serverless/vector/NoSQL characteristics fit the workload and are available in the target environment.

## IBM references

- Add Astra DB service in watsonx.data: https://www.ibm.com/docs/en/watsonxdata/saas?topic=watsonxdata-adding-astra-db-service
- watsonx.data/Astra DB cloud availability: https://cloud.ibm.com/docs/watsonxdata?topic=watsonxdata-feature_parity_wxd
- Set up Milvus in watsonx.data: https://www.ibm.com/docs/en/watsonx/saas?topic=settings-setting-up-milvus-vector-store
- IBM watsonx.ai: https://www.ibm.com/products/watsonx-ai
