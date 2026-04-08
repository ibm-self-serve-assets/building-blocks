# RAG Accelerator 2.0

A production-ready RAG (Retrieval-Augmented Generation) service built with FastAPI that supports multiple vector databases (Milvus and OpenSearch) for document ingestion, semantic search, and AI-powered question answering using IBM watsonx.ai.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [REST API Endpoints](#rest-api-endpoints)
- [Extending the Application](#extending-the-application)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)

## Overview

RAG Accelerator 2.0 is a flexible, extensible service that enables:
- Document ingestion from IBM Cloud Object Storage (COS)
- Vector embedding generation using IBM watsonx.ai
- Storage in Milvus or OpenSearch vector databases
- Semantic search and retrieval
- AI-powered question answering with context

## Architecture

### Core Components

```
rag-accelerator/
├── main.py                          # FastAPI application entry point
├── app/
│   ├── route/                       # API route definitions
│   │   ├── ingest/routes.py        # Document ingestion endpoints
│   │   ├── query/routes.py         # Vector search endpoints
│   │   └── qna/routes.py           # Q&A with LLM endpoints
│   └── src/
│       ├── model/                   # Pydantic data models
│       ├── services/                # Business logic layer
│       │   ├── IngestService.py    # Document processing & ingestion
│       │   ├── QueryService.py     # Vector search operations
│       │   └── QnAAIService.py     # watsonx.ai integration
│       └── utils/                   # Utility modules
│           ├── config.py           # Configuration management
│           ├── connection.py       # Abstract base connection class
│           ├── connection_factory.py # Connection factory pattern
│           ├── milvus_connection.py  # Milvus implementation
│           ├── opensearch_connection.py # OpenSearch implementation
│           ├── milvus_ops.py       # Milvus operations
│           ├── opensearch_ops.py   # OpenSearch operations
│           ├── cos_connector.py    # COS client setup
│           ├── cos_ops.py          # COS operations
│           └── ingestion_helper.py # Document processing utilities
```

### Connection Abstraction Layer

The application uses an extensible connection architecture based on the **Factory Pattern** and **Abstract Base Classes**.

#### `connection.py` - Base Connection Class

```python
class BaseConnection(ABC):
    """
    Abstract base class for all database/vector store connections.
    All connection implementations must inherit from this class.
    """
    
    def __init__(self, parameters: Dict[str, Any]):
        self.parameters = parameters
    
    @abstractmethod
    def connect(self) -> Any:
        """
        Establish the connection and return the client object.
        Must be implemented by all subclasses.
        
        Returns:
            tuple: (client, connection_args)
        """
        pass
```

**Purpose**: Provides a common interface for all database connections, ensuring consistency and enabling easy extension.

#### `connection_factory.py` - Factory Pattern

```python
class ConnectionFactory:
    """
    Factory class for creating database connections.
    Implements the Factory Pattern for connection instantiation.
    """
    
    @staticmethod
    def create_connection(connection_name: str, parameters: Dict[str, Any]) -> BaseConnection:
        """
        Create and return appropriate connection instance based on connection_name.
        
        Args:
            connection_name: Type of connection ('milvus_connect' or 'opensearch_connect')
            parameters: Configuration parameters from config.py
            
        Returns:
            BaseConnection: Instance of the appropriate connection class
            
        Raises:
            ValueError: If connection_name is not supported
        """
        if connection_name == "milvus_connect":
            return MilvusConnection(parameters)
        elif connection_name == "opensearch_connect":
            return OpenSearchConnection(parameters)
        
        raise ValueError(f"Unsupported connection type: {connection_name}")
```

**Purpose**: Centralizes connection creation logic, making it easy to add new database support.

#### Concrete Implementations

**MilvusConnection** (`milvus_connection.py`):
- Implements `BaseConnection` for Milvus vector database
- Handles SSL/TLS connections
- Returns `MilvusClient` instance

**OpenSearchConnection** (`opensearch_connection.py`):
- Implements `BaseConnection` for OpenSearch
- Supports SSL, certificate verification, and custom CA certificates
- Returns `OpenSearch` client instance

## Features

- **Multi-Database Support**: Milvus and OpenSearch vector databases
- **Flexible Document Processing**: Support for PDF, DOCX, PPTX, Markdown, HTML
- **Configurable Chunking**: Customizable chunk size and overlap
- **IBM watsonx.ai Integration**: Embeddings and LLM inference
- **Cloud Object Storage**: Document ingestion from IBM COS
- **REST API**: FastAPI-based with automatic OpenAPI documentation
- **Extensible Architecture**: Easy to add new vector databases or features
- **Production Ready**: Logging, error handling, and API key authentication

## Prerequisites

1. **Python 3.12+** installed locally
2. **Vector Database**: Either Milvus or OpenSearch instance with credentials
3. **IBM watsonx.ai**: Project with API access
4. **IBM Cloud Object Storage**: Bucket with documents
5. **Git** installed locally

## Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd rag-accelerator
```

2. **Create a Python virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

```bash
cp .env.example .env
# Edit .env with your credentials
```

## Configuration

### Environment Variables (`.env`)

The application uses a comprehensive configuration system managed through `config.py` and `.env` file.

#### Runtime Configuration

```bash
# Runtime Environment
RUNTIME_ENVIRONMENT=cloud                    # Environment type (cloud/on-prem)
RUNTIME_REGION=us-south                      # IBM Cloud region
IBM_IAM_URL=https://iam.cloud.ibm.com/identity/token
RUNTIME_ENV_APSX_URL=https://api.dataplatform.cloud.ibm.com
USER_ACCESS_TOKEN=""                         # For on-prem deployments
SERVER_URL=http://0.0.0.0:8080              # API server URL
ALLOWED_ORIGINS="*"                          # CORS allowed origins
```

#### Vector Database Selection

```bash
# Choose your vector database
CONNECTION_NAME=opensearch_connect           # Options: milvus_connect, opensearch_connect
```

#### Milvus Configuration

```bash
# Milvus Vector Database
MILVUS_HOST=<milvus-host>                   # Milvus server hostname
MILVUS_PORT=<milvus-port>                   # Milvus server port (typically 19530)
MILVUS_USER=ibmlhapikey_<username>          # Username (format: ibmlhapikey_<username>)
MILVUS_PASSWORD=<ibm-api-key>               # IBM Cloud API Key
MILVUS_DATABASE=<database-name>             # Database name (default: default)
MILVUS_SSL=true                             # Enable SSL/TLS
MILVUS_SSL_CERTIFICATE=<path-to-cert>       # Path to SSL certificate file
```

**Milvus Parameters Explained**:
- `MILVUS_HOST`: The hostname or IP address of your Milvus instance
- `MILVUS_PORT`: Port number (19530 for standard Milvus, 443 for cloud)
- `MILVUS_USER`: Authentication username (IBM Cloud format: `ibmlhapikey_<username>`)
- `MILVUS_PASSWORD`: Your IBM Cloud API key for authentication
- `MILVUS_DATABASE`: Target database name within Milvus
- `MILVUS_SSL`: Enable secure connections (true/false)
- `MILVUS_SSL_CERTIFICATE`: Path to certificate file for SSL verification

#### OpenSearch Configuration

```bash
# OpenSearch Vector Database
OPENSEARCH_HOST=your-host.com               # OpenSearch hostname
OPENSEARCH_PORT=9200                        # OpenSearch port (typically 9200)
OPENSEARCH_USER=admin                       # Username for authentication
OPENSEARCH_PASSWORD=<your-password>         # Password for authentication
OPENSEARCH_USE_SSL=true                     # Enable SSL/TLS
OPENSEARCH_VERIFY_CERTS=false               # Verify SSL certificates
OPENSEARCH_CA_CERTS=/path/to/ca.pem        # Path to CA certificate bundle
```

**OpenSearch Parameters Explained**:
- `OPENSEARCH_HOST`: Hostname or IP of your OpenSearch cluster
- `OPENSEARCH_PORT`: Port number (9200 for HTTP, 9300 for transport)
- `OPENSEARCH_USER`: Username for basic authentication
- `OPENSEARCH_PASSWORD`: Password for authentication
- `OPENSEARCH_USE_SSL`: Enable HTTPS connections (true/false)
- `OPENSEARCH_VERIFY_CERTS`: Verify SSL certificates (true/false)
- `OPENSEARCH_CA_CERTS`: Path to CA certificate file for custom SSL verification

#### IBM watsonx.ai Configuration

```bash
# watsonx.ai Credentials
RAG_WATSONX_AI_API_KEY=<ibm-api-key>        # IBM Cloud API Key
RAG_WATSONX_PROJECT_ID=<project-id>         # watsonx.ai project ID
RAG_WATSONX_URL=https://us-south.ml.cloud.ibm.com  # watsonx.ai endpoint
RAG_WATSONX_DEPLOYMENT_ID=<deployment-id>   # Model deployment ID
RAG_WATSONX_SPACE_ID=<space-id>            # watsonx.ai space ID
RAG_WATSONX_MIN_TOKENS=1                    # Minimum tokens for generation
RAG_WATSONX_MAX_TOKENS=512                  # Maximum tokens for generation
```

#### IBM Cloud Object Storage

```bash
# COS Configuration
COS_SERVICE_INSTANCE_ID=<instance-id>       # COS service instance ID
COS_ENDPOINT=https://s3.us-south.cloud-object-storage.appdomain.cloud
IBM_CLOUD_API_KEY=<ibm-api-key>            # IBM Cloud API Key
```

#### RAG Parameters

```bash
# RAG Configuration
RAG_VECTORSEARCH_TOP_N_RESULTS=5            # Number of results to retrieve
RAG_ES_NUMBER_OF_SHARDS=1                   # OpenSearch shards
RAG_ES_MIN_SCORE=10                         # Minimum relevance score
RAG_INCLUDE_ALL_HTML_TAGS=False             # Include HTML tags in processing
RAG_ELASTIC_SEARCH_TEMPLATE_FILE=""         # Custom OpenSearch template
```

#### Advanced Parameters

```bash
# Embedding Model
RAG_ADV_MILVUS_EMBEDDING_MODEL_ID=intfloat/multilingual-e5-large

# Milvus Advanced
RAG_ADV_MILVUS_HYBRID_SEARCH=false          # Enable hybrid search
RAG_ADV_MILVUS_RERANKER=""                  # Reranker model

# OpenSearch Advanced
RAG_ADV_ELASTIC_SEARCH_MODEL_ID=.elser_model_2_linux-x86_64
RAG_ADV_ELASTIC_SEARCH_VECTOR_TYPE=sparse   # Vector type (sparse/dense)

# Chunking Configuration
RAG_ADV_CHUNK_SIZE=256                      # Chunk size in tokens
RAG_ADV_CHUNK_OVERLAP=128                   # Overlap between chunks
RAG_ADV_INDEX_CHUNK_SIZE=256                # Batch size for indexing
```

#### Logging Configuration

```bash
# Logging
LOG_LEVEL=INFO                              # Log level (DEBUG, INFO, WARNING, ERROR)
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### `config.py` - Configuration Management

The `config.py` module centralizes all configuration parameters:

```python
PARAMETERS = {
    "RUNTIME": {
        "environment": os.getenv("RUNTIME_ENVIRONMENT"),
        "runtime_env_apsx_url": os.getenv("RUNTIME_ENV_APSX_URL"),
        # ... other runtime parameters
    },
    "RAG_parameter_set": {
        "vectorsearch_top_n_results": os.getenv("RAG_VECTORSEARCH_TOP_N_RESULTS"),
        "milvus_host": os.getenv("MILVUS_HOST"),
        "opensearch_host": os.getenv("OPENSEARCH_HOST"),
        # ... other RAG parameters
    },
    "RAG_advanced_parameter_set": {
        "embedding_model_id": os.getenv("RAG_ADV_MILVUS_EMBEDDING_MODEL_ID"),
        # ... other advanced parameters
    }
}
```

**Usage in Code**:
```python
from app.src.utils import config
from app.src.utils import rag_helper_functions

parameter_sets = config.PARAMETERS
parameter_sets_list = list(parameter_sets.keys())
parameters = rag_helper_functions.get_parameter_sets(parameter_sets_list)

# Access parameters
connection_name = parameters["connection_name"]
milvus_host = parameters["milvus_host"]
```

## REST API Endpoints

### 1. Document Ingestion

**Endpoint**: `POST /ingest-files`

**Description**: Ingest documents from IBM COS, process them, generate embeddings, and store in vector database.

**Headers**:
```
Content-Type: application/json
```

**Request Body Examples**:

**Example 1: Ingest from specific directory**
```json
{
    "bucket_name": "my-documents-bucket",
    "directory": "documents/pdfs/",
    "index_name": "pdf_docs_index",
    "connection_name": "opensearch_connect"
}
```
**Example 1:  Ingest all files from bucket root**
```json
{
    "bucket_name": "my-documents-bucket",
    "directory": "",
    "index_name": "all_docs_index",
    "connection_name": "opensearch_connect"
}
```

**Parameters**:
- `bucket_name` (required): IBM COS bucket name containing documents
- `directory` (required): Prefix/folder path within the bucket
- `index_name` (required): Name of the vector database index/collection to create
- `connection_name` (required): Vector database type (`milvus_connect` or `opensearch_connect`)

**Response**:
```json
{
    "status": "success",
    "message": "Data Ingestion successful for 150 document chunks into vector database!"
}
```

**Process Flow**:
1. Downloads files from COS bucket
2. Processes documents (PDF, DOCX, PPTX, etc.)
3. Chunks documents based on configuration
4. Generates embeddings using watsonx.ai
5. Creates index/collection in vector database
6. Inserts document chunks with embeddings

### 2. Vector Search

**Endpoint**: `POST /query`

**Description**: Perform semantic search against the vector database using natural language queries.

**Headers**:
```
REST_API_KEY: <your-secret-key>
Content-Type: application/json
```

**Request Body**:
```json
{
    "query": "What are the benefits of cloud computing?",
    "index_name": "my_index",
    "connection_name": "opensearch_connect",
    "num_results": 5,
    "num_rerank_results": 3
}
```

**Parameters**:
- `query` (required): Natural language search query
- `index_name` (required): Target index/collection name
- `connection_name` (required): Vector database type
- `num_results` (optional): Number of results to retrieve (default: 5)
- `num_rerank_results` (optional): Number of results after reranking

**Response**:
```json
{
    "data": {
        "answer": "Cloud computing offers scalability, cost-efficiency...",
        "context": [
            {
                "text": "Cloud computing provides on-demand access...",
                "metadata": {
                    "title": "Cloud Computing Guide",
                    "source": "guide.pdf",
                    "page_number": "5"
                },
                "score": 0.89
            }
        ]
    },
    "status": "success",
    "message": "Successfully queried Vector DB"
}
```

### 3. Q&A with LLM

**Endpoint**: `POST /ai/qna/query`

**Description**: Ask questions and get AI-generated answers using watsonx.ai LLM with retrieved context.

**Request Body**:
```json
{
    "question": "Explain the architecture of microservices",
    "query_filter": {}
}
```

**Parameters**:
- `question` (required): Question to ask the LLM
- `query_filter` (optional): Additional filters for retrieval

**Response**:
```json
{
    "answer": "Microservices architecture is a design pattern...",
    "documents": [
        {
            "text": "Microservices are independently deployable...",
            "metadata": {...}
        }
    ],
    "expert_answer": "Based on the retrieved context...",
    "log_id": "abc123"
}
```

### 4. Interactive Q&A Session

**Endpoint**: `POST /ai/qna/qa`

**Description**: Run an interactive Q&A session (programmatic access to notebook functionality).

**Response**:
```json
{
    "status": "qa invoked"
}
```

### API Authentication

All endpoints require the `REST_API_KEY` header for authentication. Set this in your `.env` file:

```bash
REST_API_KEY=your-secret-api-key-here
```

### Swagger UI Documentation

Access interactive API documentation at:
```
http://localhost:8080/docs
```

Features:
- Try out endpoints directly from browser
- View request/response schemas
- See all available parameters
- Test authentication

## Extending the Application

### Adding a New Vector Database

To add support for a new vector database (e.g., Pinecone, Weaviate):

1. **Create Connection Class** (`app/src/utils/newdb_connection.py`):

```python
from app.src.utils.connection import BaseConnection
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

class NewDBConnection(BaseConnection):
    """
    Connection implementation for NewDB vector database.
    """
    
    def connect(self) -> tuple:
        """
        Establish connection to NewDB.
        
        Returns:
            tuple: (client, connection_args)
        """
        if self.parameters.get("connection_name") != "newdb_connect":
            raise ValueError(f"Unsupported connection: {self.parameters.get('connection_name')}")
        
        logger.info("Connecting to NewDB")
        
        # Extract parameters
        host = self.parameters.get("newdb_host")
        api_key = self.parameters.get("newdb_api_key")
        
        # Create client
        from newdb import Client
        client = Client(host=host, api_key=api_key)
        
        # Connection args for compatibility
        connection_args = {
            "host": host,
            "api_key": api_key
        }
        
        logger.info("NewDB connection established")
        return client, connection_args
```

2. **Update Connection Factory** (`app/src/utils/connection_factory.py`):

```python
from app.src.utils.newdb_connection import NewDBConnection

class ConnectionFactory:
    @staticmethod
    def create_connection(connection_name: str, parameters: Dict[str, Any]) -> BaseConnection:
        if connection_name == "milvus_connect":
            return MilvusConnection(parameters)
        elif connection_name == "opensearch_connect":
            return OpenSearchConnection(parameters)
        elif connection_name == "newdb_connect":  # Add new connection
            return NewDBConnection(parameters)
        
        raise ValueError(f"Unsupported connection type: {connection_name}")
```

3. **Add Configuration** (`.env` and `config.py`):

```bash
# .env
NEWDB_HOST=api.newdb.com
NEWDB_API_KEY=your-api-key
```

```python
# config.py
"RAG_parameter_set": {
    # ... existing parameters
    "newdb_host": os.getenv("NEWDB_HOST"),
    "newdb_api_key": os.getenv("NEWDB_API_KEY"),
}
```

4. **Create Operations Class** (`app/src/utils/newdb_ops.py`):

```python
class NewDBOperations:
    def __init__(self, client, parameters):
        self.client = client
        self.parameters = parameters
    
    def create_index(self, embedding_dim: int, index_name: str):
        """Create index in NewDB"""
        # Implementation
        pass
    
    def insert_documents(self, index_name: str, documents: list):
        """Insert documents into NewDB"""
        # Implementation
        pass
    
    def search(self, index_name: str, query_vector: list, top_k: int):
        """Search in NewDB"""
        # Implementation
        pass
```

5. **Update Services** (`IngestService.py` and `QueryService.py`):

```python
# IngestService.py
elif connection_name == "newdb_connect":
    logger.info("Processing NewDB ingestion")
    newdb_ops = NewDBOperations(client=client, parameters=parameters)
    newdb_ops.create_index(embedding_dim=embedding_dim, index_name=index_name)
    # Insert documents...
```

### Adding a New API Endpoint

1. **Create Route File** (`app/route/newfeature/routes.py`):

```python
from fastapi import APIRouter, HTTPException, Security
from app.src.model.NewFeatureModel import NewFeatureInput, NewFeatureResponse
import app.src.services.NewFeatureService as service

new_feature_route = APIRouter(
    prefix="",
    tags=["New Feature"]
)

@new_feature_route.post("/new-feature", response_model=NewFeatureResponse)
async def new_feature_endpoint(
    input_data: NewFeatureInput,
    api_key: str = Security(get_api_key)
):
    try:
        result = service.process_new_feature(input_data)
        return NewFeatureResponse(status="success", data=result)
    except Exception as e:
        logger.exception("Error in new feature: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
```

2. **Register Route** (`main.py`):

```python
from app.route.newfeature import routes as new_feature_api

app.include_router(new_feature_api.new_feature_route)
```

### Adding Custom Document Processors

Extend `ingestion_helper.py` to support new document types:

```python
class CustomDocumentProcessor:
    def process_custom_format(self, file_path: str):
        """Process custom document format"""
        # Your processing logic
        return processed_documents
```

## Usage Examples

### Python Client Example

```python
import requests
import json

# Configuration
BASE_URL = "http://localhost:8080"
API_KEY = "your-secret-api-key"

headers = {
    "REST_API_KEY": API_KEY,
    "Content-Type": "application/json"
}

# 1. Ingest Documents
ingest_payload = {
    "bucket_name": "my-docs-bucket",
    "directory": "technical-docs/",
    "index_name": "tech_docs_index",
    "connection_name": "opensearch_connect"
}

response = requests.post(
    f"{BASE_URL}/ingest-files",
    headers=headers,
    json=ingest_payload
)
print("Ingestion:", response.json())

# 2. Search Documents
query_payload = {
    "query": "How do I configure SSL?",
    "index_name": "tech_docs_index",
    "connection_name": "opensearch_connect",
    "num_results": 5
}

response = requests.post(
    f"{BASE_URL}/query",
    headers=headers,
    json=query_payload
)
print("Search Results:", response.json())

# 3. Ask Question with LLM
qna_payload = {
    "question": "What are the SSL configuration steps?",
    "query_filter": {}
}

response = requests.post(
    f"{BASE_URL}/ai/qna/query",
    headers=headers,
    json=qna_payload
)
print("AI Answer:", response.json())
```

### cURL Examples

```bash
# Ingest documents
curl -X POST "http://localhost:8080/ingest-files" \
  -H "REST_API_KEY: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "bucket_name": "my-bucket",
    "directory": "docs/",
    "index_name": "my_index",
    "connection_name": "opensearch_connect"
  }'

# Query vector database
curl -X POST "http://localhost:8080/query" \
  -H "REST_API_KEY: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAG?",
    "index_name": "my_index",
    "connection_name": "opensearch_connect"
  }'
```

## Troubleshooting

### Common Issues

**1. Connection Errors**

```
Error: Failed to connect to Milvus/OpenSearch
```

**Solution**:
- Verify credentials in `.env`
- Check network connectivity
- Ensure SSL certificates are valid
- Verify firewall rules allow connections

**2. Embedding Generation Fails**

```
Error: Embedding batch failed
```

**Solution**:
- Check watsonx.ai API key and project ID
- Verify token limits in configuration
- Ensure embedding model ID is correct
- Check watsonx.ai service status

**3. Document Processing Errors**

```
Error: Failed to process document
```

**Solution**:
- Verify document format is supported
- Check file permissions in COS
- Ensure sufficient memory for large documents
- Review chunk size configuration

**4. API Authentication Fails**

```
Error: Invalid API credentials
```

**Solution**:
- Verify `REST_API_KEY` in `.env` matches request header
- Ensure `.env` file is loaded correctly
- Check for whitespace in API key

### Logging

Enable debug logging for detailed troubleshooting:

```bash
# .env
LOG_LEVEL=DEBUG
```

View logs in console output or configure file logging:

```python
# Add to main.py
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("rag-accelerator.log"),
        logging.StreamHandler()
    ]
)
```

## Starting the Application

### Local Development

```bash
# Activate virtual environment
source venv/bin/activate

# Start the server
python main.py

# Or use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### Docker Deployment

```bash
# Build image
docker build -t rag-accelerator:latest .

# Run container
docker run -p 8080:8080 --env-file .env rag-accelerator:latest
```

### Production Deployment

For production, consider:
- Using a production WSGI server (Gunicorn with Uvicorn workers)
- Setting up reverse proxy (Nginx)
- Implementing rate limiting
- Adding monitoring and alerting
- Using secrets management (HashiCorp Vault, AWS Secrets Manager)

## Dependencies

Key dependencies (see `requirements.txt` for complete list):

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **pymilvus**: Milvus client
- **opensearch-py**: OpenSearch client
- **ibm-watsonx-ai**: IBM watsonx.ai SDK
- **ibm-cos-sdk**: IBM Cloud Object Storage
- **langchain**: Document processing and RAG utilities
- **unstructured**: Document parsing

## License

[Add your license information]

## Contributing

[Add contribution guidelines]

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: [documentation-url]
- Email: [support-email]

## Team

**Created and Architected By**: Anand Das, Anindya Neogi, Joseph Kim, Shivam Solanki, Rishit Barochia, Himangshu Mech

---

**Version**: 1.0.1  
**Last Updated**: 2026-03-09
