# Pipelines — Building Blocks

The **Pipelines** use case prepares, transforms, moves and indexes structured and unstructured data for analytics, RAG, search and AI applications.

---

## When to Use

| If you need to… | Building Block |
|---|---|
| Ground AI agents in enterprise documents | [`rag/`](rag/) |
| Ingest and prepare complex PDFs, tables or presentations | [`udi/`](udi/) |
| Let business users query governed data in plain English | [`text2sql/`](text2sql/) |
| Build repeatable batch ETL/ELT across enterprise systems | [`etl/`](etl/) |
| Synchronize large file repositories across WAN or cloud sites | [`data-sync/`](data-sync/) |

---

## Available Building Blocks

| Building Block | Path | Products | Best Fit |
|---|---|---|---|
| **RAG** | [`rag/`](rag/) | IBM watsonx.data OpenRAG + OpenSearch | Enterprise retrieval and agent grounding |
| **UDI (Unstructured Data Integration)** | [`udi/`](udi/) | IBM watsonx.data integration + Docling for IBM watsonx | Document ingestion, parsing, transformation, chunking and enrichment |
| **Text2SQL** | [`text2sql/`](text2sql/) | IBM watsonx.data intelligence | Natural-language access to governed relational data |
| **ETL / ELT** | [`etl/`](etl/) | IBM DataStage + IBM watsonx.data integration | Batch transformation and data movement |
| **Data Sync** | [`data-sync/`](data-sync/) | IBM Aspera Sync | High-speed synchronization of files and large repositories over WAN |

---

## Getting Started

### Prerequisites

All Pipelines building blocks require:
- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **Python 3.10+** (for FastAPI and script assets)
- Access to the IBM service listed in each building block's README header

### Common Setup Pattern

```bash
# 1. Navigate to the asset
cd <building-block>/assets/<asset-name>

# 2. Configure credentials
cp .env.example .env
# Edit .env: IBM_API_KEY, WATSONX_PROJECT_ID, and service-specific vars

# 3. Install and run
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080   # or: python main.py
# Swagger docs → http://localhost:8080/docs
```

### IBM Bob — Your Fellow Developer

Each building block ships a **Bob Mode** (specialist persona) and **Bob Skills** (reusable knowledge packs).

**Install a Bob Mode**:
```powershell
# Windows
Copy-Item bob-modes/base-modes/<mode>.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/<mode>.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

**Install a Bob Skill**:
```bash
unzip bob-skills/<skill>.zip
```
Open IBM Bob → Skills panel → enable the skill.

---

## IBM Products Used

| Product | Role |
|---|---|
| **[IBM watsonx.data OpenRAG](https://www.ibm.com/products/watsonx-data/ai-enterprise-search)** | Managed enterprise RAG service with OpenSearch backend |
| **[IBM watsonx.data integration — UDI](https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=data-integrating-unstructured-documents)** | Visual drag-and-drop unstructured document pipeline |
| **[Docling for IBM watsonx](https://www.ibm.com/products/docling)** | Advanced document conversion for complex PDFs, tables and layouts |
| **[IBM watsonx.data intelligence](https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=tools-data-intelligence)** | Metadata context for Text2SQL; natural-language query generation |
| **[IBM DataStage](https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=datastage-designing-flows)** | Visual ETL/ELT flow designer with enterprise connectors |
| **[IBM Aspera Sync](https://www.ibm.com/products/aspera/sync)** | High-speed WAN file and repository synchronization |
