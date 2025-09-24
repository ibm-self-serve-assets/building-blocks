# RAG Ingestion Integration Service for GenAI Pipelines

The RAG Service API provides a modular framework for building GenAI pipelines that combine retrieval-augmented generation (RAG) with Milvus as the vector database. It simplifies ingestion and querying pipeline while offering extensible customization options for document loaders, schemas, embedding models, and rerankers. The framework is designed to save significant development and testing time — from hours to weeks compared to manual setup — by providing ready-to-use pipelines, governance hooks, and evaluation tools.

## Features
* **Ingestion Pipeline:** Chunking, merging, and ingestion into Milvus
* **Embedding:** Dense, hybrid, or dual embeddings with selectable models

## Deploying the Framework
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

## Getting Started
### Prerequisites
The following prerequisites are required to spin up the RAG Service API:
1. Python3 installed locally
2. Milvus DB Credentials
3. IBM watsonx.ai Credentials
4. IBM COS Credentials

### Installation
1. Clone the repository
    ```
    git clone git@github.com:ibm-self-serve-assets/building-blocks.git
    ```

2. Change directory into `RAG Service Ingestion Pipeline`
    ```
    cd building-blocks/data-for-ai/vector-search/RAG Service Ingestion Pipeline
    ```

3. Create a python virtual environment
    ```
    python3 -m venv virtual-env
    source virtual-env/bin/activate
    pip3 install -r requirements.txt
    ```

4. Copy env file to .env
    ```
    cp env .env
    ```

5. Configure parameters in .env
    1. **Milvus credentials**: 
        * `WXD_MILVUS_HOST` (Milvus host URL)
        * `WXD_MILVUS_PORT` (Milvus port)
        * `WXD_MILVUS_USER` (Username)
        * `WXD_MILVUS_PASSWORD` (IBM Cloud API Key associated with Milvus account)
    2. **IBM COS credentials**: 
        * `IBM_CLOUD_API_KEY` ([IBM Cloud API Key](<https://cloud.ibm.com/iam/apikeys>))
        * `COS_ENDPOINT` (Service endpoint URL for your COS instance)
        * `COS_AUTH_ENDPOINT` (IAM auth endpoint)
        * `COS_SERVICE_INSTANCE_ID` (Bucket ID found in COS service credentials)
    3. `REST_API_KEY`: All API request endpoints require a header `REST_API_KEY`: <your-secret>. Must be any arbitrary string (not empty), set in .env

6. When finished, deactivate the virtual environment by running this command: 
    ```
    deactivate
    ```

### Starting the Application Locally
Ensure `.env` file is fully configured with all required credentials. You can start the application by running the following in terminal if you are using Python:
```bash
python3 main.py
```

The RAG Service API is built using Uvicorn CLI. You can also run the following within the `/app` directory:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 4050 --reload
```

### Swagger UI
The RAG Service API is built with FastAPI, which includes interactive docs with Swagger UI support. 
To view endpoints, http://0.0.0.0:4050/docs (replace with your configured host/port)
#### Ingestion
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
url = "http://0.0.0.0:4050/ingest-files"

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

### **Coming Soon**
* .png and .jpg VLM Support
* Additional docling processing functions (image annotation, table exports)
* **Error Logging:** Structured logs with timestamp, line of code, and error response models

## Team
### Created and Architected By
Anand Das, Anindya Neogi, Joseph Kim
