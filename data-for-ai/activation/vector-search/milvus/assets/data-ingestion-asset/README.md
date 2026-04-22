# Milvus Data Ingestion Service

FastAPI service for ingesting documents from IBM COS into Milvus with Docling-based parsing and IBM Watsonx embeddings.

## Getting Started
### Prerequisites
The following prerequisites are required to spin up the milvus ingest API:
1. watsonx.data environment set up with milvus DB (https://cloud.ibm.com/docs/watsonxdata?topic=watsonxdata-adding-milvus-service)
2. Python3.13 installed locally
3. git installed locally
4. watsonx.data Milvus DB host, port and log in (Note: your COS bucket must be public for this ingestion pipeline)
5. IBM COS Credentials

### Installation
1. Clone the repository
    ```
    git clone https://github.com/ibm-self-serve-assets/building-blocks.git
    ```

2. Change directory into `vector-search`
    ```
    cd building-blocks/data-for-ai/vector-search/
    ```

3. Create a python virtual environment
    ```
    python3 -m venv virtual-env
    source virtual-env/bin/activate
    pip3 install -r requirements.txt
    ```

4. Copy .env.example file to .env
    ```
    cp .env.example .env
    ```

5. Configure parameters in .env
    1. **Milvus credentials**: 
        * `WXD_MILVUS_HOST` (Milvus host URL from watsonx.data UI)
        * `WXD_MILVUS_PORT` (Milvus portf rom watsonx.data UI)
        * `WXD_MILVUS_USER` (value will be 'ibmlhapikey')
        * `WXD_MILVUS_PASSWORD` (IBM Cloud API Key associated with Milvus account (IBM cloud Service account created for Milvus))
    2. **IBM COS credentials**: 
        * `IBM_CLOUD_API_KEY` (IBM Cloud API Key associated with COS (IBM cloud Service account created for Milvus))
        * `COS_ENDPOINT` (Service endpoint URL for your COS instance)
        * `COS_SERVICE_INSTANCE_ID` (CRN value of COS Instance)
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
uvicorn app.main:app --host 127.0.0.1 --port 4050 --reload
```

### Swagger UI
The RAG Service API is built with FastAPI, which includes interactive docs with Swagger UI support. 
To view endpoints, http://127.0.0.1:4050/docs (replace with your configured host/port)
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

### **Coming Soon**
* .png and .jpg VLM Support
* Additional docling processing functions (image annotation, table exports)
* **Error Logging:** Structured logs with timestamp, line of code, and error response models

## Team
### Created and Architected By
Anand Das, Anindya Neogi, Joseph Kim, Shivam Solanki
