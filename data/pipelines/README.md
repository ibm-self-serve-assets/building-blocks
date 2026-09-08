# Pipelines

Reusable ingestion, transformation, replication, retrieval, and natural-language data access patterns built around IBM data products.

| Building block | IBM product anchor | Use |
|---|---|---|
| [RAG](rag/) | IBM watsonx.data OpenRAG + IBM watsonx.ai | Retrieval-augmented generation and reference RAG services |
| [Unstructured Data Integration](udi/) | IBM watsonx.data integration — UDI | Parse, enrich, chunk, and prepare unstructured content |
| [Text2SQL](text2sql/) | IBM watsonx.data intelligence | Generate governed SQL from natural-language questions |
| [ETL / ELT](etl/) | IBM watsonx.data integration — DataStage | Batch data transformation and integration |
| [Data Sync](data-sync/) | IBM Aspera Sync | High-speed file and directory synchronization |

## Capability boundaries

- Batch transformation → **ETL / ELT**
- Unstructured document preparation → **UDI**
- File/directory transfer → **Data Sync**
- RAG retrieval/generation → **RAG**

## IBM references

- IBM watsonx.data integration: https://www.ibm.com/products/watsonx-data-integration
- IBM watsonx.data intelligence: https://www.ibm.com/products/watsonx-data-intelligence
- IBM watsonx.ai: https://www.ibm.com/products/watsonx-ai
- IBM Aspera: https://www.ibm.com/products/aspera
