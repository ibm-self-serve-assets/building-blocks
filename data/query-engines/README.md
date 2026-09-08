# Query Engines

Query-engine building blocks provide developer patterns for **federated/lakehouse SQL** and **vector/NoSQL access** anchored in IBM watsonx.data.

## Building blocks

| Building block | IBM product anchor | Developer use |
|---|---|---|
| [Zero-Copy Lakehouse](zero-copy-lakehouse/) | IBM watsonx.data | Query supported external data and open lakehouse tables without unnecessary duplication |
| [Serverless Vector](serverless-vector/) | IBM watsonx.data — Astra DB service | Vector ingestion/search and NoSQL CRUD patterns |

## Choose the pattern

```text
SQL across supported external data / Iceberg -> Zero-Copy Lakehouse
Vector similarity + serverless NoSQL          -> Serverless Vector
```

For vector workloads, IBM watsonx.data also supports Milvus in applicable deployments. Select the service based on workload and the current regional/deployment availability matrix.

## IBM references

- IBM watsonx.data: https://www.ibm.com/products/watsonx-data
- watsonx.data availability: https://cloud.ibm.com/docs/watsonxdata?topic=watsonxdata-feature_parity_wxd
- Add Milvus service: https://cloud.ibm.com/docs/watsonxdata?topic=watsonxdata-adding-milvus-service
- Add Astra DB service: https://www.ibm.com/docs/en/watsonxdata/saas?topic=watsonxdata-adding-astra-db-service
