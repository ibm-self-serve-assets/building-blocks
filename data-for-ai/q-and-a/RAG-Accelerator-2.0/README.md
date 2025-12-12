# RAG Service

The RAG Service provides a deployable API for orchestrating RAG pipelines. It simplifies ingestion and querying pipeline while offering extensible API parameter-level customization options for document loaders, schemas, embedding models, and rerankers. The service is designed to save significant development and testing time — from hours to weeks compared to manual setup — by providing ready-to-use pipelines.

---

## Features

- Supports files: `.pdf`, `.docx`, `.pptx`, `.html`, `.md`, `.txt`; ZIP files are extracted automatically.
- Splits documents into chunks, preserves metadata, and generates embeddings using watsonx.ai.  
- Supports Elasticsearch (with deployed embedding model), Milvus (dense/hybrid), and DataStax/Cassandra.  
- Inserts documents in batches with progress tracking, handling large datasets efficiently.  
- Generates unique IDs for each chunk and supports dense or hybrid embeddings for vector databases.
- Connects to the chosen vector database (Elasticsearch, Milvus, or DataStax) . 
- **Elasticsearch**: Uses Elastic Learned Sparse Encoder (ELSER) or dense models with LangChain to retrieve relevant documents . 
- **Milvus / DataStax**: Uses embedding models with LangChain for document retrieval.
- Supports hybrid search strategies for Milvus and Elasticsearch, combining dense and sparse search methods.

---

## Getting Started

### Prerequisites

The following prerequisites are required to spin up the RAG Service API:

1. **Python3.11** installed locally
2. IBM watsonx.ai environment with project and necessary access control
3. IBM COS Credentials
4. git installed locally
5. Create and configure the **platform connection asset** for your vector database: Make sure to follow the same name while creating connection as stated below.
  - `elasticsearch_connect`  
  - `milvus_connect`  
  - `datastax_connect` 
6. Upload files or ZIP archives containing supported documents to the COS bucket before ingestion.
7. An Elasticsearch template is provided at `RAG-Accelerator-2.0/app/src/utils/elastic_search/elastic_search_ELSER_BM25_hybrid_template.json`. Please ensure that the local path to this file is correctly set in your `.env` file.

### Installation

1. Clone the repository

    ```bash
    git clone https://github.com/ibm-self-serve-assets/building-blocks.git
    ```

2. Change directory into `RAG-Accelerator-2.0`

    ```bash
    cd /data-for-ai/q-and-a/RAG-Accelerator-2.0
    ```

3. Create a python virtual environment

    ```bash
    python3 -m venv virtual-env
    source virtual-env/bin/activate
    pip3 install -r requirements.txt
    ```
    
4. Configure the required parameters in a `.env` file. Use the provided `.env.template` in the same folder as a reference—fill in your credentials and save it as `.env`. This file is loaded by `config.py` in the `utils` folder following a specific format. If you add new parameters to `.env`, update `config.py` accordingly to ensure proper customization of the code.

5. When finished, deactivate the virtual environment by running this command:

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

Use the ingestion endpoint to pull documents from your COS bucket, process them (split/chunk), embed, and insert into milvus/elastic search vector databases.

**Endpoint**

```
POST /ingest-files
```

**Required JSON Body**

```
{
  "bucket_name": "bucket name",
  "connection_name": "elasticsearch_connect/milvus_connect",
  "directory": "directory name",
  "index_name": "es index/ milvus collection name"
}
```

**Test via Swagger UI**
The API includes interactive documentation powered by FastAPI + Swagger.

1. Navigate to `/docs` → expand **POST /ingest-files**.
2. Click `Try it out` → fill in **bucket_name** where you have uploaded the files, **index_name** which is es index/ milvus collection name, **connection name** and **directory** where the files are loaded from cos.
3. Click `Execute`. Verify the 200 response and review any ingestion statistics returned.

**Sample Test Python endpoint:**

```
import json, requests
url = "http://127.0.0.1:4050/ingest-files"

payload = json.dumps({
  "bucket_name": "bucket name",
  "connection_name": "elasticsearch_connect/milvus_connect",
  "directory": "directory name",
  "index_name": "es index/ milvus collection name"
})

response = requests.request("POST", url, data=payload)

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
  "connection_name": "elasticsearch_connect/milvus_connect",
  "index_name": "es index/ milvus collection name used during ingestion",
  "query": "sample query"
}
```
**Test via Swagger UI**
The API includes interactive documentation powered by FastAPI + Swagger.

1. Navigate to `/docs` → expand **POST /ingest-files**.
2. Click `Try it out` → fill in **connection name**, **index_name** which is es index/ milvus collection name and **query**
3. Click `Execute`. Verify the 200 response and review any ingestion statistics returned.

**Sample Test Python endpoint:**

```
import json, requests
url = "http://127.0.0.1:4050/query"

payload = json.dumps({
  "connection_name": "elasticsearch_connect/milvus_connect",
  "index_name": "es index/ milvus collection name used during ingestion",
  "query": "sample query"
})

response = requests.request("POST", url, data=payload)

print(response.text)
```

Verify results through the Swagger UI or by checking the API response.

## QnA Query

Use the QnA query endpoint to execute the question using the prompt that is deployed in Watson Studio.

**Endpoint**

```
POST /ai/qna/query
```
**Required JSON Body**

```
{
  "question": "how to perform decision optimization?",
  "query_filter": {
    "additionalProp1": {}
  }
}
```
**Test via Swagger UI**
The API includes interactive documentation powered by FastAPI + Swagger.

1. Navigate to `/docs` → expand **POST /ai/qna/query**.
2. Click `Try it out` → fill in **question**, **query_filter** if any
3. Click `Execute`. Verify the 200 response and review any ingestion statistics returned.

**Sample Test Python endpoint:**

```
import json, requests
url = "http://127.0.0.1:4050/ai/qna/query"

payload = json.dumps({
    "question" : "how to perform decision optimization?"   
})

response = requests.request("POST", url, data=payload)

print(response.text)
```

Verify results through the Swagger UI or by checking the API response.


## Team

Rishit Barochia, Ashwini Nair, Susum R and Sharath Kumar RK

