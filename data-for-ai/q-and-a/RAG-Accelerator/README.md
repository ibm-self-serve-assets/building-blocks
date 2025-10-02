# RAG Service

The RAG Service provides a deployable API for orchestrating RAG pipelines. It simplifies ingestion and querying pipeline while offering extensible API parameter-levl customization options for document loaders, schemas, embedding models, and rerankers. The service is designed to save significant development and testing time — from hours to weeks compared to manual setup — by providing ready-to-use pipelines.

## Features

* **Ingestion Pipeline:** Chunking, merging, and ingestion into Milvus
* **Embedding:** Dense, hybrid, or dual embeddings with selectable models
* **Retriever & Querying:** Hybrid search, reranking (weighted, RRF, cross-encoder), configurable search parameters
* **Querying:** LLM integration with configurable models and prompt templates
* **Governance:** Integration with watsonx.governance for build-time and runtime governance

<img width="562" height="375" alt="rag drawio" src="https://github.com/user-attachments/assets/7846b5a7-5e22-45bd-94ea-d0176d7a07fc" />

## Deploying the Service

* **REST API:** You can set the value of `REST_API_KEY` with a unique value in the environment variables
* **watsonx.ai:** Required for Governance SDK, prompt lab, and model hosting
* **IBM COS:** Configure COS_ENDPOINT, COS_AUTH_ENDPOINT, and COS_SERVICE_INSTANCE_ID for storage services

## Customization

The API supports customizations at multiple levels:

* **Ingestion**
  * Document loaders: HTML, JSON, PDF, Markdown, custom loaders
  * Collection schema: Configurable via JSON templates
  * Embedding models: Hybrid, dense, dense+sparse (HuggingFace, watsonx.ai, IBM models)
  * Document processing: Docling/Markdown processing, picture annotation, table cleanup
  * Chunkers: Docling hybrid chunker, Markdown text splitter, recursive text splitter

* **Querying**
  * Search parameters: Number of docs retrieved and reranked
  * Rerankers: Weighted, RRF, cross-encoding
  * LLM models: Configurable by provider and prompt template

## Getting Started

### Prerequisites

The following prerequisites are required to spin up the RAG Service API:

1. **Python3.13** installed locally
2. Milvus DB Credentials
3. IBM watsonx.ai environt with project and necessay access control
4. IBM COS Credentials
5. git installed locally

### Installation

1. Clone the repository

    ```bash
    git clone https://github.com/ibm-self-serve-assets/building-blocks.git
    ```

2. Change directory into `RAG-Accelerator`

    ```bash
    cd /data-for-ai/q-and-a/RAG-Accelerator
    ```

3. Create a python virtual environment

    ```bash
    python3 -m venv virtual-env
    source virtual-env/bin/activate
    pip3 install -r requirements.txt
    ```

4. Copy env file to .env

    ```bash
    cp env .env
    ```

5. Configure parameters in .env
    1. **Milvus credentials**:
        * `WXD_MILVUS_HOST` (Milvus host URL)
        * `WXD_MILVUS_PORT` (Milvus port)
        * `WXD_MILVUS_USER` (Username)
        * `WXD_MILVUS_PASSWORD` (IBM Cloud API Key associated with Milvus account)
    2. **watsonx.ai credentials**:
        * `WATSONX_MODEL_ID` (Choose the foundation model ID found in your project on [watsonx.ai](https://dataplatform.cloud.ibm.com/))
        * `WATSONX_PROJECT_ID` (From your watsonx.ai project dashboard)
        * `WATSONX_APIKEY` ([IBM Cloud API Key](<https://cloud.ibm.com/iam/apikeys>))
        * `WATSONX_URL` (Typically "<https://us-south.ml.cloud.ibm.com>")
    3. **IBM COS credentials**:
        * `IBM_CLOUD_API_KEY` ([IBM Cloud API Key](<https://cloud.ibm.com/iam/apikeys>))
        * `COS_ENDPOINT` (Service endpoint URL for your COS instance)
        * `COS_AUTH_ENDPOINT` (IAM auth endpoint)
        * `COS_SERVICE_INSTANCE_ID` (Bucket ID found in COS service credentials)
    4. `REST_API_KEY`: All API request endpoints require a header `REST_API_KEY`: <your-secret>. Must be any arbitrary string (not empty), set in .env

6. When finished, deactivate the virtual environment by running this command:

    ```bash
    deactivate
    ```

### Starting the Application Locally

Ensure `.env` file is fully configured with all required credentials. You can start the application by running the following in terminal if you are using Python:

```bash
python3 main.py
```

The RAG Service API is built using Uvicorn CLI. You can also run the following within the `/app` directory:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 4050 --reload
```

### Swagger UI

The RAG Service API is built with FastAPI, which includes interactive docs with Swagger UI support.
To view endpoints, <http://127.0.0.1:4050/docs> (replace with your configured host/port)

## Ingestion

Use the ingestion endpoint to pull documents from your COS bucket, process them (split/chunk), embed, and upsert into Milvus.
**Endpoint**

```
POST /ingest-files
```

**Required JSON Body**

```
{
    "bucket_name": "<cos-bucket>",
    "collection_name": "<milvus-collection>",
    "chunk_type": "DOCLING_DOCS"
}
```

* `bucket_name`: Name of the S3/COS bucket containing documents
* `collection_name`: Target Milvus collection to create or upsert into
* `chunk_type`: Which chunker to use. Supported values include DOCLING_DOCS, MARKDOWN, and RECURSIVE.

**Headers**

```
REST_API_KEY: <your-secret>
Content-Type: application/json
```

**Test via Swagger UI**
The API includes interactive documentation powered by FastAPI + Swagger.

1. Navigate to `/docs` → expand **POST /ingest-files**.
2. Click `Try it out` → fill in **bucket_name**, **collection_name**, and **chunk_type**.
3. Click `Execute`. Verify the 200 response and review any ingestion statistics returned.

**Sample Test Python endpoint:**

```
import json, requests
url = "http://127.0.0.1:4050/ingest-files"

payload = json.dumps({
    "bucket_name": "<cos-bucket>"
    "collection_name": "<milvus-collection>"
    "chunk_type": "DOCLING_DOCS"
})
headers = {
    "REST_API_KEY": <your-secret>,
    "Content-Type": "application/json"
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
```

Verify results through the Swagger UI or by checking the API response.

## Query

Use the query endpoint to pull query Milvus database by natural language (RAG)

**Endpoint**

```
POST /query
```
**Required JSON Body**

```
{
    "collection_name": "<milvus-collection>",
    "query": "<query text>"
}
```

* `collection_name`: Target Milvus collection to fetch data
* 'query' : Natual language query to fetch data

**Headers**

```
REST_API_KEY: <your-secret>
Content-Type: application/json
```

**Test via Swagger UI**
The API includes interactive documentation powered by FastAPI + Swagger.

1. Navigate to `/docs` → expand **POST /ingest-files**.
2. Click `Try it out` → fill in **collection name**, **query**
3. Click `Execute`. Verify the 200 response and review any ingestion statistics returned.

**Sample Test Python endpoint:**

```
import json, requests
url = "http://127.0.0.1:4050/query"

payload = json.dumps({
    "collection_name": "<milvus-collection>"
    "query": "<query text>"
})
headers = {
    "REST_API_KEY": <your-secret>,
    "Content-Type": "application/json"
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
```

Verify results through the Swagger UI or by checking the API response.

### **Coming Soon**

* .png and .jpg VLM Support
* Additional docling processing functions (image annotation, table exports)
* **Prompt Controls & Guardrails:** Guardrails for runtime governance and prompt safety
* **Governance SDK:** Evaluation of golden datasets, runtime metrics, LLM-as-a-judge
* **Memory Layers:** Multi-turn Q&A, cache integration, context management (MemVerge, Zep)
* **Error Logging:** Structured logs with timestamp, line of code, and error response models

## Team

### Created and Architected By

Anand Das, Anindya Neogi, Joseph Kim, Shivam Solanki
**Endpoint**
