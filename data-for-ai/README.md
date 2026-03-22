# Building Block of Data for AI

Welcome to the **Building Block of Data for AI**. 

This framework provides ready-to-use accelerators that make it easier to operationalize data for AI/GenAI use cases. Each accelerator addresses a critical capability required to manage, process, and secure data for AI-driven applications. These accelerators are designed to integrate seamlessly with existing enterprise systems, reducing time-to-value for AI projects. By standardizing data access, governance, and enrichment, the framework ensures scalability, trust, and efficiency across diverse AI workloads.


## Data Ingestion
- Comprehensive data ingestion solutions for **unstructured and structured** data.
- **IBM UDI** for unstructured data processing.
- **Database connectors** for structured data with CDC support.

---

## Zero-Copy Lakehouse
- Enables seamless querying across databases, warehouses, and cloud object stores without data duplication.
- Reduces **costs and latency** by eliminating data movement.

---

## Vector Search
- Provides a **vector-based retrieval service** for GenAI pipelines.
- Powers **semantic similarity search** for retrieval-augmented generation (RAG).
- Optimized for **scalable AI workloads**.

---

## Question & Answer
- Delivers **natural language interfaces** to interact with data.
- **watsonx.data intelligence Text2SQL** converts natural language questions into executable SQL.

---

## Data Security & Encryption
- Protects sensitive data through **masking, encryption, and access controls**.
- Enhances **data governance** and regulatory compliance.

---

## Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ibm-self-serve-assets/building-blocks.git
   cd building-blocks/data-for-ai
   ```

2. **Explore the building blocks**:
   - [`data-ingestion/`](./data-ingestion/) - Ingest unstructured, structured, and semi-structured data
   - [`zero-copy-lakehouse/`](./zero-copy-lakehouse/) - Query across data sources without duplication
   - [`vector-search/`](./vector-search/) - Semantic search for GenAI pipelines
   - [`question-and-answer/`](./question-and-answer/) - RAG and Text-to-SQL capabilities
   - [`data-security-and-encryption/`](./data-security-and-encryption/) - Data protection and governance

3. **Navigate to specific building block** and follow the README in each directory


## Contributing

We welcome contributions! Please fork this repo, create a feature branch, and open a pull request with your changes.

---

## License

This project is licensed under the Apache 2.0 License.
