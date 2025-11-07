# RAG Service
The RAG Service acts as an orchestration layer for Retrieval-Augmented Generation workflows, combining ingestion, vectorization, and querying into a single managed service. Designed for enterprise AI platforms, it simplifies integration of vector databases, LLMs, and data governance modules while delivering low-latency, high-throughput query execution. This architecture accelerates GenAI solution development by offering reusable, pre-tested components for ingestion, retrieval, and compliance enforcement.

## 📘 Table of Contents
- [Overview](#overview)  
- [Architecture](#architecture)  
- [Features](#features)  
- [Technology Stack](#technology-stack)  
- [Prerequisites](#prerequisites)  
- [Project Structure](#project-structure)  
- [Developer Guide](#developer-guide)  
- [Configuration](#configuration)  
- [Usage](#usage)  
- [Examples](#examples)  
- [Coming Soon](#coming-soon)  
- [Contributing](#contributing)  
- [License](#license)  

---


## Overview
The **RAG Service** provides a deployable API for orchestrating **Retrieval-Augmented Generation (RAG)** pipelines. It simplifies both **ingestion** and **query orchestration** processes by abstracting complex data handling and embedding operations behind a modular API layer. The service is designed to accelerate enterprise GenAI integration by reducing development cycles—from weeks to hours—through pre-built, configurable pipelines and governance integrations.

---

## Architecture
The architecture is centered around three primary components — **Ingestion**, **Embedding**, and **Query Retrieval**, all managed through a unified FastAPI interface. The system integrates with **Milvus** as a vector database for similarity search, **IBM COS** for scalable data storage, and **watsonx.ai** for governance and model orchestration.

<img width="562" height="375" alt="rag drawio" src="https://github.com/user-attachments/assets/7846b5a7-5e22-45bd-94ea-d0176d7a07fc" />

---

## Features

* **Ingestion Pipeline:** Handles document segmentation, chunking, merging, and ingestion into Milvus with fault-tolerant retries.  
* **Embedding Layer:** Supports multiple strategies (dense, hybrid, or dual embeddings) using pluggable models from Hugging Face, watsonx.ai, or IBM Foundation Models.  
* **Retriever & Querying Engine:** Implements hybrid search with reranking mechanisms (Weighted, RRF, Cross-Encoder) and configurable parameters for precision retrieval.  
* **LLM Query Integration:** Seamlessly connects with LLMs via watsonx.ai APIs for dynamic query interpretation and contextual response generation.  
* **Governance Hooks:** Native integration with **watsonx.governance** to ensure compliance across build-time and runtime inference.  

---

## Technology Stack

- **Language:** Python 3.13  
- **Framework:** FastAPI, Uvicorn  
- **Vector Database:** Milvus  
- **Storage:** IBM Cloud Object Storage (COS)  
- **LLM Orchestration:** watsonx.ai  
- **Governance SDK:** watsonx.governance  
- **Containerization (Optional):** Docker / Podman  

---

## Prerequisites

Before deploying or running the service, ensure the following components are available and configured:

1. **Python 3.13+**
2. **Milvus** vector DB credentials and instance access  
3. **IBM watsonx.ai** project with governance SDK access  
4. **IBM COS** credentials for object storage  
5. **Git** installed locally  
6. **Optional:** Docker/Podman for containerized deployment  

---

## Project Structure

```
RAG-Accelerator/
│
├── app/
│   ├── main.py                # FastAPI entrypoint
│   ├── routes/                # API route definitions
│   ├── services/              # Core ingestion and query modules
│   ├── utils/                 # Helper scripts, COS connectors, and loggers
│
├── requirements.txt           # Dependency definitions
├── env                        # Sample environment file
├── README.md                  # Documentation
└── .env                       # Local environment configuration
```

---

## Developer Guide

### Installation

```bash
git clone https://github.com/ibm-self-serve-assets/building-blocks.git
cd /data-for-ai/q-and-a/RAG-Accelerator
python3 -m venv virtual-env
source virtual-env/bin/activate
pip install -r requirements.txt
cp env .env
```

### Running Locally

Ensure `.env` is configured properly, then launch the service:

```bash
python3 main.py
```
Or using Uvicorn directly:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 4050 --reload
```

Access API docs at: [http://127.0.0.1:4050/docs](http://127.0.0.1:4050/docs)

---

## Configuration

### Required Environment Variables

**Milvus Configuration**
```
WXD_MILVUS_HOST=<milvus-host>
WXD_MILVUS_PORT=<milvus-port>
WXD_MILVUS_USER=<username>
WXD_MILVUS_PASSWORD=<ibm-cloud-api-key>
```

**watsonx.ai Configuration**
```
WATSONX_MODEL_ID=<model-id>
WATSONX_PROJECT_ID=<project-id>
WATSONX_APIKEY=<api-key>
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

**IBM COS Configuration**
```
IBM_CLOUD_API_KEY=<api-key>
COS_ENDPOINT=<endpoint-url>
COS_AUTH_ENDPOINT=<iam-auth-endpoint>
COS_SERVICE_INSTANCE_ID=<instance-id>
```

**REST API Security Key**
```
REST_API_KEY=<your-secret>
```

---

## Usage

### Ingestion Endpoint

**POST /ingest-files**

Request Body:
```json
{
    "bucket_name": "<cos-bucket>",
    "collection_name": "<milvus-collection>",
    "chunk_type": "DOCLING_DOCS"
}
```

Headers:
```
REST_API_KEY: <your-secret>
Content-Type: application/json
```

This endpoint pulls documents from COS, processes and embeds them, and pushes vectors into Milvus.

---

### Query Endpoint

**POST /query**

Request Body:
```json
{
    "collection_name": "<milvus-collection>",
    "query": "<query text>"
}
```

Headers:
```
REST_API_KEY: <your-secret>
Content-Type: application/json
```

This retrieves contextually relevant information from Milvus using hybrid search and optionally generates an LLM response through watsonx.ai.

---

## Examples

**Python Example - Query Endpoint**
```python
import json, requests
url = "http://127.0.0.1:4050/query"
payload = json.dumps({
    "collection_name": "sample_collection",
    "query": "What are IBM foundation models?"
})
headers = {
    "REST_API_KEY": "my-secret",
    "Content-Type": "application/json"
}
response = requests.post(url, headers=headers, data=payload)
print(response.text)
```

---

## Coming Soon

- Vision-Language Model (VLM) support (.png/.jpg)  
- Extended Docling capabilities for image annotation & table extraction  
- **Prompt Guardrails:** Runtime prompt safety with policy enforcement  
- **Governance SDK Enhancements:** Model evaluation, golden dataset benchmarking, runtime metrics  
- **Memory Layers:** Multi-turn contextual caching and long-term memory support  
- **Advanced Logging:** Structured error telemetry and observability integration  

---

## Contributing

We welcome contributions! Developers can submit pull requests or open issues in the repository. Ensure that all contributions align with IBM open-source contribution guidelines and include sufficient test coverage.

---

## 👥 Team

**Created and Architected by**  
Anand Das • Anindya Neogi • Joseph Kim • Shivam Solanki

---
## License

Licensed under the **Apache 2.0 License**. See the [LICENSE](LICENSE) file for details.

