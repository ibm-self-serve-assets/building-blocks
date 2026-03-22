# RAG Ingestion MCP Server

Streamable HTTP MCP Server for ingesting documents from IBM Cloud Object Storage into vector databases (OpenSearch or Milvus).

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
SERVER_DESCRIPTION=Base MCP Server for Data for AI Building Block (with RAG ingestion)
ENVIRONMENT=development
PUBLIC_BASE_URL=
ALLOWED_HOSTS=
ALLOWED_ORIGINS=
APP_BEARER_TOKEN=your_optional_bearer_token
LOG_LEVEL=INFO
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
MILVUS_SECURE=true
MILVUS_COLLECTION=rag_collection
MILVUS_HYBRID_SEARCH=false
MILVUS_USE_BULK_INGESTION=false

# Milvus bulk-writer remote storage (required for Milvus bulk ingestion)
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


## Adding to IBM Bob

This section explains how to configure IBM Bob to use this RAG Ingestion MCP Server.

### Prerequisites

1. **Start the MCP Server**:
   ```bash
   python app/server.py
   ```
   
   The server will start on `http://localhost:8080`

2. **Verify Server is Running**:
   ```bash
   curl http://localhost:8080/health
   ```

### Bob Configuration

Add the MCP server configuration to `.bob/mcp.json` in your workspace root.

#### For New Projects (No Existing MCP Servers)

If you don't have any MCP servers configured yet, create `.bob/mcp.json` with:

```json
{
	"mcpServers": {
		"rag-ingestion-local-mcp": {
			"command": "uvx",
			"args": [
				"mcp-proxy",
				"--transport",
				"streamablehttp",
				"http://localhost:8080/mcp"
			],
			"description": "RAG Ingestion MCP Server (Local) - Product Insights",
			"disabled": false,
			"alwaysAllow": [
				"get_server_info",
				"get_server_time",
				"get_hostname",
				"get_ingestion_configuration",
				"ingest_from_cos"
			],
			"timeout": 3600
		}
	}
}
```

#### For Existing Projects (With Other MCP Servers)

If you already have MCP servers configured, add the new server to your existing configuration:

**Example:** Adding to a project that already has `mcp-server-a`:

```json
{
	"mcpServers": {
		"mcp-server-a": {
			"command": "node",
			"args": ["/path/to/server-a/index.js"],
			"description": "Existing MCP Server A",
			"disabled": false
		},
		"rag-ingestion-local-mcp": {
			"command": "uvx",
			"args": [
				"mcp-proxy",
				"--transport",
				"streamablehttp",
				"http://localhost:8080/mcp"
			],
			"description": "RAG Ingestion MCP Server (Local) - Product Insights",
			"disabled": false,
			"alwaysAllow": [
				"get_server_info",
				"get_server_time",
				"get_hostname",
				"get_ingestion_configuration",
				"ingest_from_cos"
			],
			"timeout": 3600
		}
	}
}
```

**Note:** Simply add the `rag-ingestion-local-mcp` entry to your existing `mcpServers` object without removing other servers.

### Verification

After configuration, restart VS Code and verify the connection:

1. **Check Bob's MCP Status**:
   - Open Bob
   - Look for "rag-ingestion-local-mcp" in connected servers
   - Status should show "Connected"

2. **Test Server Directly**:
   ```bash
   curl http://localhost:8080/health
   ```

### Using the MCP Server with Bob

Once configured, you can ask Bob to perform ingestion tasks:

**Example Commands:**
- "Bob, show me the ingestion server configuration"
- "Bob, ingest documents from COS with prefix 'products/' into the product_insights collection"
- "Bob, get the current server time"

### Available Tools

| Tool | Description |
|------|-------------|
| `get_server_info` | Get server details |
| `get_server_time` | Get current server time |
| `get_hostname` | Get server hostname |
| `get_ingestion_configuration` | View configuration |
| `ingest_from_cos` | Ingest from COS |

### Troubleshooting

**Server Not Connecting:**
1. Verify server is running: `curl http://localhost:8080/health`
2. Check `.bob/mcp.json` syntax is correct
3. Restart VS Code after configuration changes

**Tools Not Appearing:**
- Restart VS Code/Bob after configuration changes
- Check server logs for errors

### Support

For issues with Bob integration:
1. Check server logs: `python app/server.py` output
2. Verify Bob configuration: `.bob/mcp.json`
3. Test server directly: `curl http://localhost:8080/health`
4. Review Bob logs in VS Code Developer Tools
