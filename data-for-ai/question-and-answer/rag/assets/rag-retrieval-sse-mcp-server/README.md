# RAG Retrieval MCP Server

Streamable HTTP MCP Server for semantic and keyword search across vector databases (OpenSearch or Milvus) using IBM Watsonx embeddings.

## Installation

### Prerequisites
- Python 3.12+
- IBM Watsonx AI instance (for embeddings)
- OpenSearch or Milvus vector database (pre-populated with documents)

### Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `mcp` - Model Context Protocol framework
- `fastmcp` - FastMCP server implementation
- `ibm-watsonx-ai` - IBM Watsonx AI SDK for embeddings
- `opensearchpy` - OpenSearch Python client
- `pymilvus` - Milvus Python SDK
- `python-dotenv` - Environment variable management

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

#### Required Configuration

**Server Settings**
```env
HOST=0.0.0.0
PORT=8080
SERVER_NAME=rag-retrieval-mcp
SERVER_VERSION=1.0.0
SERVER_DESCRIPTION=Retrieval MCP Server for querying RAG indexes (OpenSearch or Milvus)
ENVIRONMENT=development
```

**IBM Watsonx Embeddings** (Required)
```env
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_API_KEY=your_watsonx_api_key
WATSONX_PROJECT_ID=your_project_id
EMBEDDING_MODEL_ID=intfloat/multilingual-e5-large
```

**Vector Database Selection** (Required)
```env
VECTOR_DB_TYPE=opensearch  # or milvus
```

**OpenSearch Configuration** (Required if using OpenSearch)
```env
OPENSEARCH_HOST=your_opensearch_host
OPENSEARCH_PORT=9200
OPENSEARCH_USERNAME=your_username
OPENSEARCH_PASSWORD=your_password
OPENSEARCH_INDEX=rag-index
OPENSEARCH_USE_SSL=true
```

**Milvus Configuration** (Required if using Milvus)
```env
MILVUS_HOST=your_milvus_host
MILVUS_PORT=19530
MILVUS_USER=your_username
MILVUS_PASSWORD=your_password
MILVUS_SECURE=false
MILVUS_COLLECTION=rag_collection
MILVUS_DENSE_FIELD=vector
MILVUS_TEXT_FIELD=text
```

#### Optional Configuration

**Authentication**
```env
APP_BEARER_TOKEN=your_optional_bearer_token
```

**Network Security**
```env
PUBLIC_BASE_URL=https://your-server.com
ALLOWED_HOSTS=host1.com,host2.com
ALLOWED_ORIGINS=https://app1.com,https://app2.com
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

On startup, the server automatically validates connectivity to:
- IBM Watsonx Embeddings
- Vector Database (OpenSearch or Milvus)

Example output:
```
[BOOTSTRAP] WATSONX_EMBEDDINGS: OK - model=intfloat/multilingual-e5-large
[BOOTSTRAP] OPENSEARCH: OK - your-host:9200 ssl=True
```

If any service is misconfigured, you'll see detailed error messages:
```
[BOOTSTRAP] WATSONX_EMBEDDINGS: FAIL - AuthenticationError: Invalid API key
[BOOTSTRAP] OPENSEARCH: FAIL - ConnectionError: Connection refused
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
  "server": "rag-retrieval-mcp",
  "version": "1.0.0",
  "description": "Retrieval MCP Server for querying RAG indexes",
  "timestamp": "2026-02-13T10:00:00.000Z"
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

**Response:**
```json
{
  "hostname": "server-hostname",
  "server_time": "2026-02-13T10:00:00.000Z",
  "timezone": "UTC",
  "server_name": "rag-retrieval-mcp",
  "server_version": "1.0.0",
  "description": "Retrieval MCP Server for querying RAG indexes",
  "environment": "development",
  "platform": "Linux",
  "platform_release": "5.15.0",
  "python_version": "3.12.0"
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

**Response:**
```json
{
  "server_time": "2026-02-13T10:00:00.000Z",
  "timezone": "UTC"
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

**Response:**
```json
{
  "hostname": "server-hostname"
}
```

#### 4. get_retrieval_configuration
View current retrieval configuration with secrets masked.

```json
{
  "name": "get_retrieval_configuration",
  "arguments": {}
}
```

**Response:**
```json
{
  "embedding": {
    "configured": true,
    "watsonx_url": "https://us-south.ml.cloud.ibm.com",
    "project_id": "14431c61-b5a8-4d06-81e4-a3b55bbea942",
    "embedding_model_id": "intfloat/multilingual-e5-large",
    "watsonx_api_key": "D9***v0"
  },
  "vector_db": {
    "configured": true,
    "db_type": "opensearch",
    "opensearch": {
      "host": "your-host.appdomain.cloud",
      "port": 9200,
      "use_ssl": true,
      "index": "rag-index",
      "username": "ib***om",
      "password_set": true
    },
    "milvus": {
      "host": "",
      "port": 19530,
      "secure": false,
      "collection": "rag_collection",
      "dense_field": "vector",
      "text_field": "text",
      "username": "",
      "password_set": false
    }
  }
}
```

#### 5. retrieve (Semantic Search)
Perform semantic search using vector embeddings.

```json
{
  "name": "retrieve",
  "arguments": {
    "query": "how to change the wiper blade",
    "k": 5,
    "destination_index": ""
  }
}
```

**Parameters:**
- `query` (required): Search query string
- `k` (optional): Number of results to return (default: 5)
- `destination_index` (optional): Override default index/collection name

**Response (OpenSearch):**
```json
{
  "backend": "opensearch",
  "index": "rag-index",
  "k": 5,
  "results": [
    {
      "id": "b4f38d884159809b075b3d9bdbee77f7",
      "score": 7.670346,
      "title": "MODEL X",
      "source": "/tmp/tmpkypvl7u5.pdf",
      "page_number": "215",
      "chunk_seq": 1141,
      "document_url": "",
      "text": "To replace the wiper blades:\n1. Shift into Park..."
    }
  ]
}
```

**Response (Milvus):**
```json
{
  "backend": "milvus",
  "collection": "rag_collection",
  "k": 5,
  "results": [
    {
      "id": "doc_123",
      "score": 0.234,
      "title": "User Manual",
      "source": "manual.pdf",
      "page_number": "42",
      "chunk_seq": 15,
      "document_url": "https://example.com/manual.pdf",
      "text": "Step-by-step instructions..."
    }
  ]
}
```

#### 6. keyword_search (OpenSearch Only)
Perform traditional keyword-based search.

```json
{
  "name": "keyword_search",
  "arguments": {
    "query": "wiper blade replacement",
    "k": 5,
    "destination_index": ""
  }
}
```

**Parameters:**
- `query` (required): Search query string
- `k` (optional): Number of results to return (default: 5)
- `destination_index` (optional): Override default index name

**Response:**
```json
{
  "backend": "opensearch",
  "index": "rag-index",
  "k": 5,
  "results": [
    {
      "id": "129a92cae83ab3d838d8b19e7ebeec92",
      "score": 7.491938,
      "title": "MODEL X",
      "source": "/tmp/tmpkypvl7u5.pdf",
      "page_number": "214",
      "chunk_seq": 1139,
      "document_url": "",
      "text": "For optimum performance, replace the wiper blades..."
    }
  ]
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

## Search Strategies

### When to Use Semantic Search (retrieve)

Use semantic search when:
- You need conceptual/meaning-based matching
- Query and documents may use different terminology
- You want to find semantically similar content
- Example: "how to replace windshield wipers" matches "wiper blade installation"

### When to Use Keyword Search (keyword_search)

Use keyword search when:
- You need exact term matching
- You're searching for specific product names, codes, or identifiers
- You want traditional full-text search behavior
- Example: "Model X wiper blade 26 inches"

### Hybrid Approach

For best results, consider:
1. Try semantic search first for conceptual queries
2. Fall back to keyword search if semantic results are insufficient
3. Combine results from both methods for comprehensive coverage

## Vector Database Details

### OpenSearch

- **KNN Search**: Uses `knn` query with `content_vector` field
- **Keyword Search**: Uses `match` query on `content` field
- **SSL Support**: Configurable SSL/TLS connections
- **Authentication**: Username/password or API key
- **Metadata Fields**: id, title, source, page_number, chunk_seq, document_url, text

### Milvus

- **Vector Search**: L2 distance metric with configurable nprobe
- **Collection Loading**: Automatically loads collection before search
- **Field Mapping**: Configurable dense vector and text field names
- **Authentication**: Optional username/password
- **Metadata Fields**: id, title, source, page_number, chunk_seq, document_url, text

## Error Handling

The server includes comprehensive error handling:

- **Configuration Validation**: Checks required environment variables on startup
- **Connection Checks**: Bootstrap validates all service connections
- **Detailed Error Messages**: Includes exception type and message
- **Secret Masking**: Sensitive data masked in error responses
- **Graceful Failures**: Returns structured error responses

Common error scenarios:
```json
{
  "error": "ValueError",
  "message": "Embedding config missing. Set WATSONX_URL, WATSONX_API_KEY, WATSONX_PROJECT_ID, EMBEDDING_MODEL_ID."
}
```

## Development

### Project Structure

```
.
├── app/
│   ├── server.py          # Main MCP server implementation
│   └── requirements.txt   # Python dependencies
├── .env                   # Environment configuration (not in git)
├── .env.example          # Example environment configuration
└── README.md             # This file
```

### Running Tests

Test the retrieval functionality:

```python
# Using MCP client
from mcp import ClientSession

async with ClientSession(server_url="http://localhost:8080/mcp") as session:
    result = await session.call_tool(
        "retrieve",
        arguments={"query": "how to change wiper blade", "k": 5}
    )
    print(result)
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
docker build -t rag-retrieval-mcp .
docker run -p 8080:8080 --env-file .env rag-retrieval-mcp
```

### IBM Code Engine

Deploy to IBM Code Engine:

```bash
# Create application
ibmcloud ce application create \
  --name rag-retrieval-mcp \
  --image your-registry/rag-retrieval-mcp:latest \
  --port 8080 \
  --env-from-secret rag-retrieval-secrets

# Update application
ibmcloud ce application update \
  --name rag-retrieval-mcp \
  --image your-registry/rag-retrieval-mcp:latest
```

## Monitoring

### Health Checks

Monitor server health:
```bash
curl http://localhost:8080/health
```

### Logs

The server logs bootstrap checks and query execution:
```
[BOOTSTRAP] WATSONX_EMBEDDINGS: OK - model=intfloat/multilingual-e5-large
[BOOTSTRAP] OPENSEARCH: OK - your-host:9200 ssl=True
```

## Troubleshooting

### Common Issues

**Watsonx Embeddings Failed**
- Verify `WATSONX_API_KEY` and `WATSONX_PROJECT_ID`
- Check model ID is correct and available in your project
- Ensure project has access to embedding model
- Test with: `get_retrieval_configuration` tool

**Vector DB Connection Failed**
- Verify host, port, and credentials
- Check SSL/TLS settings match your database configuration
- Ensure index/collection exists and is accessible
- For OpenSearch: Verify index has `content_vector` field for semantic search
- For Milvus: Ensure collection is loaded and has proper schema

**No Results Returned**
- Verify index/collection contains documents
- Check if query matches document content
- Try keyword_search if semantic search returns no results
- Increase `k` parameter to get more results
- Review document metadata to ensure proper indexing

**Field Not Built for ANN Search**
```
Error: Field 'content_vector' is not built for ANN search
```
- This means the OpenSearch index doesn't have proper KNN mapping
- Use keyword_search instead, or re-index with proper vector field mapping
- Check ingestion server configuration

## Performance Considerations

- **Embedding Latency**: Watsonx API calls add ~100-500ms per query
- **Vector Search Speed**: OpenSearch KNN and Milvus are both fast (<100ms)
- **Result Size**: Larger `k` values increase response time and size
- **Connection Pooling**: Reuses connections for better performance
- **Rate Limits**: Watsonx API has rate limits (check your plan)

## Security Best Practices

1. **Never commit `.env` file** - Use `.env.example` as template
2. **Rotate API keys regularly** - Update Watsonx credentials periodically
3. **Use bearer token authentication** - Set `APP_BEARER_TOKEN` in production
4. **Enable SSL/TLS** - Use HTTPS endpoints for all services
5. **Restrict network access** - Use firewalls and security groups
6. **Monitor access logs** - Track API usage and errors
7. **Mask sensitive data** - Use `get_retrieval_configuration` to verify masking

## Integration Examples

### Using with MCP Proxy

```bash
# Connect via mcp-proxy
uvx mcp-proxy --transport streamablehttp http://localhost:8080/mcp
```

### Using with Roo Cline

Add to your MCP settings:
```json
{
  "mcpServers": {
    "rag-retrieval": {
      "command": "uvx",
      "args": [
        "mcp-proxy",
        "--transport",
        "streamablehttp",
        "http://localhost:8080/mcp"
      ]
    }
  }
}
```

### Using Programmatically

```python
import requests

# Semantic search
response = requests.post(
    "http://localhost:8080/mcp",
    json={
        "method": "tools/call",
        "params": {
            "name": "retrieve",
            "arguments": {
                "query": "how to change wiper blade",
                "k": 5
            }
        }
    },
    headers={"Authorization": "Bearer your_token"}
)

results = response.json()
```

## Contributing

When contributing to this project:

1. Follow Python PEP 8 style guidelines
2. Add type hints to function signatures
3. Update documentation for new features
4. Test with both OpenSearch and Milvus
5. Ensure bootstrap checks pass
6. Add error handling for edge cases

## License

This project is part of the IBM Data for AI Building Block.

## Support

For issues and questions:
- Check bootstrap logs for connectivity issues
- Review configuration with `get_retrieval_configuration` tool
- Verify environment variables match `.env.example`
- Test with simple queries first
- Check vector database has indexed documents

## Version History

- **1.0.0** - Initial release
  - FastMCP server implementation
  - Semantic search with Watsonx embeddings
  - Keyword search (OpenSearch)
  - OpenSearch and Milvus support
  - Bootstrap connectivity checks
  - Bearer token authentication
  - Configuration masking

## Adding to IBM Bob

This section explains how to configure IBM Bob to use this RAG Retrieval MCP Server.

### Prerequisites

1. **Start Milvus** (if using local Milvus):
   ```bash
   cd data-for-ai/milvus
   ./run-local.sh start
   ```

2. **Ensure Data is Ingested**:
   Make sure you've already ingested documents using the RAG Ingestion MCP Server.

3. **Configure Environment**:
   Ensure `.env` file is properly configured with Milvus connection details.

4. **Start the MCP Server**:
   ```bash
   cd data-for-ai/rag-retrieval-sse-mcp-server
   python app/server.py
   ```
   
   The server will start on `http://localhost:8081`

### Bob Configuration

#### Option 1: Using Bob's MCP Settings UI

1. Open Bob in VS Code
2. Click on the Bob icon in the sidebar
3. Navigate to **Settings** → **MCP Servers**
4. Click **Add Server**
5. Configure the server:

   **Server Configuration:**
   ```json
   {
     "name": "rag-retrieval-local-mcp",
     "transport": "streamablehttp",
     "url": "http://localhost:8081/mcp"
   }
   ```

6. Click **Save** and **Restart Bob**

#### Option 2: Manual Configuration (bob_mcp_settings.json)

Add the following configuration to your Bob MCP settings file:

**Location:** `.bob/bob_mcp_settings.json` (in your workspace root)

```json
{
  "mcpServers": {
    "rag-retrieval-local-mcp": {
      "transport": "streamablehttp",
      "url": "http://localhost:8081/mcp"
    }
  }
}
```

**Complete Example with Both Ingestion and Retrieval:**

```json
{
  "mcpServers": {
    "rag-ingestion-local-mcp": {
      "transport": "streamablehttp",
      "url": "http://localhost:8080/mcp"
    },
    "rag-retrieval-local-mcp": {
      "transport": "streamablehttp",
      "url": "http://localhost:8081/mcp"
    }
  }
}
```

#### Option 3: VS Code Settings (settings.json)

Add to your VS Code workspace settings:

**Location:** `.vscode/settings.json`

```json
{
  "bob.mcpServers": {
    "rag-retrieval-local-mcp": {
      "transport": "streamablehttp",
      "url": "http://localhost:8081/mcp"
    }
  }
}
```

### Authentication (Optional)

If you've set `APP_BEARER_TOKEN` in your `.env` file, configure authentication:

```json
{
  "mcpServers": {
    "rag-retrieval-local-mcp": {
      "transport": "streamablehttp",
      "url": "http://localhost:8081/mcp",
      "headers": {
        "Authorization": "Bearer your_token_here"
      }
    }
  }
}
```

### Verification

After configuration, verify the connection:

1. **Check Bob's MCP Status**:
   - Open Bob
   - Look for "rag-retrieval-local-mcp" in connected servers
   - Status should show "Connected"

2. **Test with Bob**:
   Ask Bob to use the retrieval tools:
   ```
   Can you show me the available retrieval tools?
   ```

3. **Test Server Directly**:
   ```bash
   # Health check
   curl http://localhost:8081/health
   
   # Server info
   curl http://localhost:8081/
   ```

### Using the MCP Server with Bob

Once configured, you can ask Bob to perform retrieval tasks:

#### Example 1: Get Server Information
```
Bob, can you get the retrieval server information?
```

Bob will use the `get_server_info` tool.

#### Example 2: View Configuration
```
Bob, show me the current retrieval configuration.
```

Bob will use the `get_retrieval_configuration` tool.

#### Example 3: Semantic Search
```
Bob, search for information about "how to change wiper blades" in the product_insights collection.
```

Bob will use the `retrieve` tool with:
```json
{
  "query": "how to change wiper blades",
  "k": 5,
  "destination_index": "product_insights"
}
```

#### Example 4: Keyword Search (OpenSearch only)
```
Bob, do a keyword search for "Model X wiper blade" in the documentation.
```

Bob will use the `keyword_search` tool with:
```json
{
  "query": "Model X wiper blade",
  "k": 5
}
```

### Available Tools in Bob

Once connected, Bob can use these tools:

| Tool | Description | Usage |
|------|-------------|-------|
| `get_server_info` | Get server details | "Show me server info" |
| `get_server_time` | Get current server time | "What time is it on the server?" |
| `get_hostname` | Get server hostname | "What's the server hostname?" |
| `get_retrieval_configuration` | View configuration | "Show retrieval config" |
| `retrieve` | Semantic search | "Search for 'wiper blade replacement'" |
| `keyword_search` | Keyword search (OpenSearch) | "Keyword search for 'Model X'" |

### Troubleshooting Bob Integration

#### Server Not Connecting

1. **Verify Server is Running**:
   ```bash
   curl http://localhost:8081/health
   ```
   
   Expected response:
   ```json
   {
     "status": "healthy",
     "server": "rag-retrieval-mcp-local",
     "version": "1.0.0"
   }
   ```

2. **Check Port Availability**:
   ```bash
   # Windows
   netstat -ano | findstr :8081
   
   # Linux/Mac
   lsof -i :8081
   ```

3. **Verify Configuration**:
   - Check `bob_mcp_settings.json` syntax
   - Ensure URL is correct: `http://localhost:8081/mcp`
   - Verify transport type: `streamablehttp`

4. **Check Bob Logs**:
   - Open VS Code Developer Tools (Help → Toggle Developer Tools)
   - Look for MCP connection errors in Console

#### No Search Results

1. **Verify Data is Ingested**:
   - Check if documents were successfully ingested
   - Use ingestion server's tools to verify

2. **Check Collection/Index**:
   ```
   Bob, show me the retrieval configuration
   ```
   Verify the collection/index name matches your ingested data

3. **Try Different Search Types**:
   - If semantic search returns nothing, try keyword search
   - Adjust the `k` parameter to get more results

#### Authentication Errors

If using bearer token authentication:

1. **Verify Token in .env**:
   ```env
   APP_BEARER_TOKEN=your_secret_token
   ```

2. **Add to Bob Configuration**:
   ```json
   {
     "headers": {
       "Authorization": "Bearer your_secret_token"
     }
   }
   ```

3. **Test with curl**:
   ```bash
   curl -H "Authorization: Bearer your_secret_token" http://localhost:8081/health
   ```

### Production Deployment

For production use with Bob:

#### Deploy to IBM Code Engine

1. **Build and Push Image**:
   ```bash
   docker build -t us.icr.io/your-namespace/rag-retrieval-mcp:latest .
   docker push us.icr.io/your-namespace/rag-retrieval-mcp:latest
   ```

2. **Create Code Engine Application**:
   ```bash
   ibmcloud ce application create \
     --name rag-retrieval-mcp \
     --image us.icr.io/your-namespace/rag-retrieval-mcp:latest \
     --port 8080 \
     --env-from-secret rag-retrieval-secrets \
     --min-scale 1 \
     --max-scale 3
   ```

3. **Get Application URL**:
   ```bash
   ibmcloud ce application get --name rag-retrieval-mcp
   ```

4. **Update Bob Configuration**:
   ```json
   {
     "mcpServers": {
       "rag-retrieval-remote-mcp": {
         "transport": "streamablehttp",
         "url": "https://rag-retrieval-mcp.your-region.codeengine.appdomain.cloud/mcp",
         "headers": {
           "Authorization": "Bearer your_production_token"
         }
       }
     }
   }
   ```

### Complete Setup Example

Here's a complete step-by-step setup:

```bash
# 1. Start Milvus
cd data-for-ai/milvus
./run-local.sh start

# 2. Ingest documents (using ingestion server)
cd ../rag-ingestion-sse-mcp-server
python app/server.py &
# Use Bob or API to ingest documents

# 3. Configure retrieval environment
cd ../rag-retrieval-sse-mcp-server
cp .env.example .env
# Edit .env with your credentials

# 4. Start retrieval MCP server
python app/server.py

# 5. In another terminal, verify server
curl http://localhost:8081/health

# 6. Configure Bob (create/edit .bob/bob_mcp_settings.json)
cat > ../../.bob/bob_mcp_settings.json << 'EOF'
{
  "mcpServers": {
    "rag-ingestion-local-mcp": {
      "transport": "streamablehttp",
      "url": "http://localhost:8080/mcp"
    },
    "rag-retrieval-local-mcp": {
      "transport": "streamablehttp",
      "url": "http://localhost:8081/mcp"
    }
  }
}
EOF

# 7. Restart VS Code/Bob

# 8. Test with Bob
# Ask: "Bob, search for 'product features' in the documentation"
```

### Environment-Specific Configurations

#### Development (Local)
```json
{
  "mcpServers": {
    "rag-retrieval-local-mcp": {
      "transport": "streamablehttp",
      "url": "http://localhost:8081/mcp"
    }
  }
}
```

#### Staging
```json
{
  "mcpServers": {
    "rag-retrieval-staging-mcp": {
      "transport": "streamablehttp",
      "url": "https://rag-retrieval-staging.your-domain.com/mcp",
      "headers": {
        "Authorization": "Bearer staging_token"
      }
    }
  }
}
```

#### Production
```json
{
  "mcpServers": {
    "rag-retrieval-remote-mcp": {
      "transport": "streamablehttp",
      "url": "https://rag-retrieval.your-domain.com/mcp",
      "headers": {
        "Authorization": "Bearer production_token"
      }
    }
  }
}
```

### Support

For issues with Bob integration:
1. Check server logs: `python app/server.py` output
2. Verify Bob configuration: `.bob/bob_mcp_settings.json`
3. Test server directly: `curl http://localhost:8081/health`
4. Review Bob logs in VS Code Developer Tools
5. Ensure Milvus is running and has ingested data
6. Verify Watsonx credentials are valid