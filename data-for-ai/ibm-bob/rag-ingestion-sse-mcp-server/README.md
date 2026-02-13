# RAG Ingestion MCP Server

A Streamable HTTP MCP (Model Context Protocol) Server built with FastMCP that provides RAG (Retrieval-Augmented Generation) ingestion capabilities from IBM Cloud Object Storage (COS) into vector databases.

## Overview

This MCP server enables automated ingestion of documents from IBM Cloud Object Storage into vector databases (OpenSearch or Milvus) with support for:

- Multiple document formats (PDF, DOCX, PPTX, HTML, Markdown, TXT, TAR archives)
- Text chunking and embedding generation using IBM Watsonx
- Vector database indexing for RAG applications
- Environment-based configuration
- Bootstrap connectivity checks
- Optional bearer token authentication

## Features

### Document Processing
- **Supported Formats**: PDF, DOCX, PPTX, HTML, Markdown, TXT, and TAR archives
- **Text Chunking**: Configurable chunk size and overlap using RecursiveCharacterTextSplitter
- **Metadata Extraction**: Preserves document title, source, page numbers, and chunk sequences

### Vector Databases
- **OpenSearch**: Full support with automatic index creation and bulk ingestion
- **Milvus**: Support for both standard and hybrid search with bulk writer integration

### Embeddings
- **IBM Watsonx**: Integration with IBM Watsonx AI for generating embeddings
- **Configurable Models**: Support for various embedding models (default: `intfloat/multilingual-e5-large`)

### Security
- **Bearer Token Authentication**: Optional API authentication
- **DNS Rebinding Protection**: Built-in transport security
- **Secret Masking**: Configuration tool masks sensitive credentials

## Architecture

```
┌─────────────────┐
│  IBM COS        │
│  (Source)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MCP Server     │
│  - Document     │
│    Loading      │
│  - Chunking     │
│  - Embedding    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  IBM Watsonx    │
│  (Embeddings)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vector DB      │
│  - OpenSearch   │
│  - Milvus       │
└─────────────────┘
```

## Installation

### Prerequisites
- Python 3.12+
- IBM Cloud Object Storage instance
- IBM Watsonx AI instance
- OpenSearch or Milvus vector database

### Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `mcp` - Model Context Protocol framework
- `fastmcp` - FastMCP server implementation
- `ibm-watsonx-ai` - IBM Watsonx AI SDK
- `ibm-cos-sdk` - IBM Cloud Object Storage SDK
- `opensearchpy` - OpenSearch Python client
- `pymilvus` - Milvus Python SDK
- `langchain-community` - Document loaders
- `langchain-text-splitters` - Text chunking utilities

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

#### Server Configuration
```env
HOST=0.0.0.0
PORT=8080
SERVER_NAME=rag-ingestion-mcp
SERVER_VERSION=1.0.0
ENVIRONMENT=development
APP_BEARER_TOKEN=your_optional_bearer_token
```

#### IBM Cloud Object Storage
```env
COS_ENDPOINT=https://s3.us-south.cloud-object-storage.appdomain.cloud
COS_API_KEY=your_cos_api_key
COS_INSTANCE_CRN=your_cos_instance_crn
COS_BUCKET=your_bucket_name
COS_PREFIX=ingest
```

#### IBM Watsonx Embeddings
```env
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_API_KEY=your_watsonx_api_key
WATSONX_PROJECT_ID=your_project_id
EMBEDDING_MODEL_ID=intfloat/multilingual-e5-large
```

#### Chunking Configuration
```env
CHUNK_SIZE=256
CHUNK_OVERLAP=128
INCLUDE_ALL_HTML_TAGS=false
```

#### Vector Database Selection
```env
VECTOR_DB_TYPE=opensearch  # or milvus
```

#### OpenSearch Configuration
```env
OPENSEARCH_HOST=your_opensearch_host
OPENSEARCH_PORT=9200
OPENSEARCH_USERNAME=your_username
OPENSEARCH_PASSWORD=your_password
OPENSEARCH_INDEX=rag-index
OPENSEARCH_USE_SSL=true
```

#### Milvus Configuration
```env
MILVUS_HOST=your_milvus_host
MILVUS_PORT=19530
MILVUS_USER=your_username
MILVUS_PASSWORD=your_password
MILVUS_SECURE=false
MILVUS_COLLECTION=rag_collection
MILVUS_HYBRID_SEARCH=false

# Milvus bulk-writer remote storage (required for Milvus)
MILVUS_BULK_REMOTE_PATH=your_remote_path
MILVUS_BULK_COS_ENDPOINT=your_cos_endpoint
MILVUS_BULK_COS_ACCESS_KEY=your_access_key
MILVUS_BULK_COS_SECRET_KEY=your_secret_key
MILVUS_BULK_COS_BUCKET=your_bucket
MILVUS_BULK_COS_REGION=your_region
MILVUS_BULK_COS_IS_IBM=true
```

## Usage

### Starting the Server

Run the server locally:

```bash
python app/server.py
```

Or using uvicorn directly:

```bash
uvicorn app.server:app --host 0.0.0.0 --port 8080
```

### Bootstrap Checks

On startup, the server automatically checks connectivity to:
- IBM Cloud Object Storage
- IBM Watsonx Embeddings
- Vector Database (OpenSearch or Milvus)

Example output:
```
[BOOTSTRAP] COS: OK - bucket=your-bucket-name
[BOOTSTRAP] WATSONX_EMBEDDINGS: OK - model=intfloat/multilingual-e5-large
[BOOTSTRAP] OPENSEARCH: OK - host=your-host:9200
```

### API Endpoints

#### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "server": "rag-ingestion-mcp",
  "version": "1.0.0",
  "timestamp": "2026-02-13T09:00:00.000Z"
}
```

#### Server Info
```bash
GET /
```

Returns server metadata, available tools, and configuration.

#### MCP Endpoint
```bash
POST /mcp
```

The main MCP endpoint for tool invocations.

### MCP Tools

#### 1. get_server_info
Get comprehensive server information including hostname, time, environment, and platform details.

```json
{
  "name": "get_server_info",
  "arguments": {}
}
```

#### 2. get_server_time
Get the current server time in UTC timezone.

```json
{
  "name": "get_server_time",
  "arguments": {}
}
```

#### 3. get_hostname
Get the server hostname.

```json
{
  "name": "get_hostname",
  "arguments": {}
}
```

#### 4. get_ingestion_configuration
View current ingestion configuration with secrets masked.

```json
{
  "name": "get_ingestion_configuration",
  "arguments": {}
}
```

Returns masked configuration for:
- COS settings
- Embedding configuration
- Chunking parameters
- Vector database settings

#### 5. ingest_from_cos
Ingest files from COS into the configured vector database.

```json
{
  "name": "ingest_from_cos",
  "arguments": {
    "prefix": "optional/path/prefix",
    "bucket": "optional-bucket-override",
    "destination_index": "optional-index-override"
  }
}
```

**Parameters:**
- `prefix` (optional): COS prefix/path to filter files
- `bucket` (optional): Override default COS bucket
- `destination_index` (optional): Override default index/collection name

**Response (OpenSearch):**
```json
{
  "status": "success",
  "vector_db": "opensearch",
  "destination_index": "rag-index",
  "cos_bucket": "your-bucket",
  "cos_prefix": "ingest",
  "files_seen": 10,
  "files_processed": 10,
  "chunks_created": 150
}
```

**Response (Milvus):**
```json
{
  "status": "started",
  "vector_db": "milvus",
  "destination_collection": "rag_collection",
  "cos_bucket": "your-bucket",
  "cos_prefix": "ingest",
  "files_seen": 10,
  "files_processed": 10,
  "chunks_created": 150,
  "bulk_tasks": ["task_id_1", "task_id_2"]
}
```

## Authentication

### Bearer Token

If `APP_BEARER_TOKEN` is set, all requests to protected endpoints must include:

```bash
Authorization: Bearer your_token_here
```

Protected endpoints:
- `/` (root)
- `/health`
- `/mcp/*`

Example with curl:
```bash
curl -H "Authorization: Bearer your_token" http://localhost:8080/health
```

## Document Processing Pipeline

1. **File Discovery**: Lists objects in COS bucket with specified prefix
2. **File Download**: Downloads files from COS (supports TAR archives)
3. **Document Loading**: Uses appropriate loader based on file type
4. **Text Chunking**: Splits documents into chunks with overlap
5. **Embedding Generation**: Generates embeddings using Watsonx
6. **Vector Storage**: Indexes documents in vector database

### Supported File Types

| Format | Extension | Loader |
|--------|-----------|--------|
| PDF | `.pdf` | PyPDFLoader |
| Word | `.docx` | Docx2txtLoader |
| PowerPoint | `.pptx` | UnstructuredPowerPointLoader |
| HTML | `.html` | BSHTMLLoader |
| Markdown | `.md` | UnstructuredFileLoader |
| Text | `.txt` | UnstructuredFileLoader |
| Archive | `.tar` | tarfile (extracts supported formats) |

## Vector Database Details

### OpenSearch

- **Auto-index Creation**: Automatically creates index with proper mappings
- **Bulk Ingestion**: Uses bulk API for efficient indexing
- **KNN Support**: Configures knn_vector field for embeddings
- **Metadata Fields**: Stores title, source, page_number, chunk_seq

### Milvus

- **Collection Management**: Auto-creates collections with proper schema
- **Hybrid Search**: Optional BM25 + dense vector search
- **Bulk Writer**: Uses RemoteBulkWriter for efficient ingestion
- **Remote Storage**: Supports COS/S3 for bulk import files

## Error Handling

The server includes comprehensive error handling:

- Configuration validation on startup
- Connection checks with detailed error messages
- Graceful failure reporting in tool responses
- Secret masking in error messages

## Development

### Project Structure

```
.
├── app/
│   ├── server.py          # Main MCP server implementation
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Environment configuration (not in git)
├── readme/
│   └── README.md         # This file
├── .env.example          # Example environment configuration
└── notebooks/            # Jupyter notebooks for testing
```

### Running Tests

Test the ingestion pipeline using the provided notebook:

```bash
jupyter notebook notebooks/notebook_Process_and_Ingest_Data_from_COS_into_vector_DB.ipynb
```

## Deployment

### Docker

Create a Dockerfile using UBI Python 3.12 base image:

```dockerfile
FROM registry.access.redhat.com/ubi9/python-312

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

EXPOSE 8080

CMD ["python", "server.py"]
```

Build and run:
```bash
docker build -t rag-mcp-server .
docker run -p 8080:8080 --env-file .env rag-mcp-server
```

### IBM Code Engine

Deploy to IBM Code Engine:

```bash
# Create application
ibmcloud ce application create \
  --name rag-mcp-server \
  --image your-registry/rag-mcp-server:latest \
  --port 8080 \
  --env-from-secret rag-mcp-secrets

# Update application
ibmcloud ce application update \
  --name rag-mcp-server \
  --image your-registry/rag-mcp-server:latest
```

## Monitoring

### Health Checks

Monitor server health:
```bash
curl http://localhost:8080/health
```

### Logs

The server logs bootstrap checks and ingestion progress:
```
[BOOTSTRAP] COS: OK - bucket=your-bucket
[BOOTSTRAP] WATSONX_EMBEDDINGS: OK - model=intfloat/multilingual-e5-large
[BOOTSTRAP] OPENSEARCH: OK - host=your-host:9200
```

## Troubleshooting

### Common Issues

**COS Connection Failed**
- Verify `COS_API_KEY` and `COS_INSTANCE_CRN`
- Check network connectivity to COS endpoint
- Ensure bucket exists and is accessible

**Watsonx Embeddings Failed**
- Verify `WATSONX_API_KEY` and `WATSONX_PROJECT_ID`
- Check model ID is correct
- Ensure project has access to embedding model

**Vector DB Connection Failed**
- Verify host, port, and credentials
- Check SSL/TLS settings
- Ensure index/collection permissions

**Ingestion Errors**
- Check file formats are supported
- Verify sufficient memory for large files
- Review chunking configuration

## Performance Considerations

- **Batch Size**: Adjust chunk size based on memory constraints
- **Concurrent Processing**: Server processes files sequentially
- **Embedding Rate Limits**: Watsonx API has rate limits
- **Vector DB Throughput**: Bulk operations are more efficient

## Security Best Practices

1. **Never commit `.env` file** - Use `.env.example` as template
2. **Rotate API keys regularly** - Update COS and Watsonx credentials
3. **Use bearer token authentication** - Set `APP_BEARER_TOKEN` in production
4. **Enable SSL/TLS** - Use HTTPS endpoints for all services
5. **Restrict network access** - Use firewalls and security groups
6. **Monitor access logs** - Track API usage and errors

## Contributing

When contributing to this project:

1. Follow Python PEP 8 style guidelines
2. Add type hints to function signatures
3. Update documentation for new features
4. Test with both OpenSearch and Milvus
5. Ensure bootstrap checks pass

## License

This project is part of the IBM Data for AI Building Block.

## Support

For issues and questions:
- Check bootstrap logs for connectivity issues
- Review configuration with `get_ingestion_configuration` tool
- Verify environment variables match `.env.example`
- Test with sample documents first

## Version History

- **1.0.0** - Initial release
  - FastMCP server implementation
  - COS ingestion support
  - OpenSearch and Milvus integration
  - Watsonx embeddings
  - Bootstrap connectivity checks