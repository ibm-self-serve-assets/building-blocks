# RAG Retrieval FastAPI Server

A production-ready FastAPI server for semantic search and keyword search over RAG (Retrieval-Augmented Generation) indexes. Supports both OpenSearch and Milvus vector databases with IBM Watsonx embeddings.

## Features

- **REST API Endpoints**: Simple HTTP endpoints for retrieval operations
- **Semantic Search**: Vector-based similarity search using Watsonx embeddings
- **Keyword Search**: Traditional text-based search (OpenSearch only)
- **Multi-Backend Support**: Works with OpenSearch or Milvus
- **Authentication**: Optional Bearer token authentication
- **Health Checks**: Built-in health monitoring endpoints
- **CORS Support**: Configurable cross-origin resource sharing
- **IBM Code Engine Ready**: Optimized for deployment on IBM Cloud

## Architecture

```
┌─────────────────┐
│   Client App    │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI Server │
│  (This Service) │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌──────────┐
│OpenSearch│ │  Milvus  │
└─────────┘ └──────────┘
         │
         ▼
┌─────────────────┐
│ Watsonx AI      │
│ (Embeddings)    │
└─────────────────┘
```

## API Endpoints

### Public Endpoints

- `GET /` - Server information and available endpoints
- `GET /health` - Health check endpoint
- `GET /info` - Detailed server information

### Protected Endpoints (require authentication if `APP_BEARER_TOKEN` is set)

- `GET /config` - View current configuration (secrets masked)
- `POST /retrieve` - Semantic search using vector embeddings
- `POST /keyword-search` - Keyword-based search (OpenSearch only)

## Quick Start

### Prerequisites

- Python 3.12+
- Access to IBM Watsonx AI
- OpenSearch or Milvus instance with ingested data
- Docker (for containerized deployment)

### Local Development

1. **Clone and navigate to the directory**:
   ```bash
   cd data-for-ai/rag-retrieval-fastapi-server
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r app/requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

5. **Run the server**:
   ```bash
   python app/server.py
   ```

6. **Test the server**:
   ```bash
   curl http://localhost:8080/health
   ```

## Configuration

### Required Environment Variables

```bash
# IBM Watsonx Embeddings
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_API_KEY=your_api_key
WATSONX_PROJECT_ID=your_project_id
EMBEDDING_MODEL_ID=intfloat/multilingual-e5-large

# Vector Database Selection
VECTOR_DB_TYPE=opensearch  # or milvus

# OpenSearch Configuration (if VECTOR_DB_TYPE=opensearch)
OPENSEARCH_HOST=your_host
OPENSEARCH_PORT=9200
OPENSEARCH_USERNAME=your_username
OPENSEARCH_PASSWORD=your_password
OPENSEARCH_INDEX=rag-index
OPENSEARCH_USE_SSL=true

# Milvus Configuration (if VECTOR_DB_TYPE=milvus)
MILVUS_HOST=your_host
MILVUS_PORT=19530
MILVUS_USER=your_username
MILVUS_PASSWORD=your_password
MILVUS_COLLECTION=rag_collection
```

### Optional Environment Variables

```bash
# Server Configuration
PORT=8080
SERVER_NAME=rag-retrieval-api
ENVIRONMENT=production

# Security
APP_BEARER_TOKEN=your_secret_token
ALLOWED_ORIGINS=*

# Milvus Advanced
MILVUS_DENSE_FIELD=vector
MILVUS_TEXT_FIELD=text
MILVUS_SECURE=false
```

## API Usage Examples

### Semantic Search

```bash
# Without authentication
curl -X POST http://localhost:8080/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the features of ThinkPad X1 Carbon?",
    "k": 5
  }'

# With authentication
curl -X POST http://localhost:8080/retrieve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token_here" \
  -d '{
    "query": "What are the features of ThinkPad X1 Carbon?",
    "k": 5
  }'
```

### Keyword Search (OpenSearch only)

```bash
curl -X POST http://localhost:8080/keyword-search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token_here" \
  -d '{
    "query": "laptop",
    "k": 10
  }'
```

### Response Format

```json
{
  "backend": "opensearch",
  "index": "rag-index",
  "k": 5,
  "results": [
    {
      "id": "doc_1_chunk_0",
      "score": 0.95,
      "title": "Lenovo ThinkPad X1 Carbon",
      "source": "1_Lenovo-ThinkPad-X1-Carbon.md",
      "page_number": "",
      "chunk_seq": "0",
      "document_url": "",
      "text": "The Lenovo ThinkPad X1 Carbon is a premium business laptop..."
    }
  ]
}
```

## Docker Deployment

### Build Docker Image

```bash
docker build -t rag-retrieval-api:latest .
```

### Run Docker Container

```bash
docker run -p 8080:8080 \
  --env-file .env \
  rag-retrieval-api:latest
```

### Test Docker Container

```bash
curl http://localhost:8080/health
```

## IBM Code Engine Deployment

### Prerequisites

1. IBM Cloud account with Code Engine enabled
2. IBM Cloud CLI installed
3. Docker image pushed to a container registry (IBM Container Registry, Docker Hub, etc.)

### Step 1: Build and Push Docker Image

```bash
# Login to IBM Cloud
ibmcloud login

# Set target region
ibmcloud target -r us-south

# Login to IBM Container Registry
ibmcloud cr login

# Create namespace (if not exists)
ibmcloud cr namespace-add rag-retrieval

# Build and tag image
docker build -t us.icr.io/rag-retrieval/rag-retrieval-api:latest .

# Push to registry
docker push us.icr.io/rag-retrieval/rag-retrieval-api:latest
```

### Step 2: Create Code Engine Project

```bash
# Create project
ibmcloud ce project create --name rag-retrieval-project

# Select project
ibmcloud ce project select --name rag-retrieval-project
```

### Step 3: Create Secrets for Sensitive Data

```bash
# Create secret for Watsonx credentials
ibmcloud ce secret create --name watsonx-credentials \
  --from-literal WATSONX_API_KEY=your_api_key \
  --from-literal WATSONX_PROJECT_ID=your_project_id

# Create secret for OpenSearch credentials
ibmcloud ce secret create --name opensearch-credentials \
  --from-literal OPENSEARCH_USERNAME=your_username \
  --from-literal OPENSEARCH_PASSWORD=your_password

# Create secret for API authentication
ibmcloud ce secret create --name api-token \
  --from-literal APP_BEARER_TOKEN=your_bearer_token
```

### Step 4: Deploy Application

```bash
ibmcloud ce application create --name rag-retrieval-api \
  --image us.icr.io/rag-retrieval/rag-retrieval-api:latest \
  --registry-secret icr-secret \
  --port 8080 \
  --min-scale 1 \
  --max-scale 5 \
  --cpu 1 \
  --memory 2G \
  --env-from-secret watsonx-credentials \
  --env-from-secret opensearch-credentials \
  --env-from-secret api-token \
  --env WATSONX_URL=https://us-south.ml.cloud.ibm.com \
  --env EMBEDDING_MODEL_ID=intfloat/multilingual-e5-large \
  --env VECTOR_DB_TYPE=opensearch \
  --env OPENSEARCH_HOST=your_opensearch_host \
  --env OPENSEARCH_PORT=9200 \
  --env OPENSEARCH_INDEX=rag-index \
  --env OPENSEARCH_USE_SSL=true \
  --env ENVIRONMENT=production \
  --env SERVER_NAME=rag-retrieval-api
```

### Step 5: Get Application URL

```bash
ibmcloud ce application get --name rag-retrieval-api
```

### Step 6: Test Deployment

```bash
# Get the application URL from previous command
export APP_URL=$(ibmcloud ce application get --name rag-retrieval-api --output json | jq -r '.status.url')

# Test health endpoint
curl $APP_URL/health

# Test retrieval endpoint
curl -X POST $APP_URL/retrieve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token_here" \
  -d '{
    "query": "laptop features",
    "k": 5
  }'
```

### Update Deployment

```bash
# Update application with new image
ibmcloud ce application update --name rag-retrieval-api \
  --image us.icr.io/rag-retrieval/rag-retrieval-api:latest
```

### View Logs

```bash
# View application logs
ibmcloud ce application logs --name rag-retrieval-api

# Follow logs in real-time
ibmcloud ce application logs --name rag-retrieval-api --follow
```

### Scale Application

```bash
# Manual scaling
ibmcloud ce application update --name rag-retrieval-api \
  --min-scale 2 \
  --max-scale 10

# Auto-scaling based on CPU
ibmcloud ce application update --name rag-retrieval-api \
  --scale-down-delay 300 \
  --concurrency-target 100
```

## Alternative Deployment: Using ConfigMap

For non-sensitive configuration, you can use ConfigMaps:

```bash
# Create ConfigMap
ibmcloud ce configmap create --name rag-config \
  --from-literal WATSONX_URL=https://us-south.ml.cloud.ibm.com \
  --from-literal EMBEDDING_MODEL_ID=intfloat/multilingual-e5-large \
  --from-literal VECTOR_DB_TYPE=opensearch \
  --from-literal OPENSEARCH_HOST=your_host \
  --from-literal OPENSEARCH_PORT=9200 \
  --from-literal OPENSEARCH_INDEX=rag-index

# Deploy with ConfigMap
ibmcloud ce application create --name rag-retrieval-api \
  --image us.icr.io/rag-retrieval/rag-retrieval-api:latest \
  --env-from-configmap rag-config \
  --env-from-secret watsonx-credentials \
  --env-from-secret opensearch-credentials
```

## Monitoring and Troubleshooting

### Health Checks

The application includes built-in health checks:

```bash
# Basic health check
curl http://your-app-url/health

# Detailed server info
curl http://your-app-url/info

# Configuration check (requires auth)
curl -H "Authorization: Bearer your_token" http://your-app-url/config
```

### Common Issues

1. **Connection Errors**:
   - Verify network connectivity to OpenSearch/Milvus
   - Check firewall rules and security groups
   - Ensure correct host and port configuration

2. **Authentication Errors**:
   - Verify Watsonx API key is valid
   - Check OpenSearch/Milvus credentials
   - Ensure Bearer token matches if authentication is enabled

3. **Embedding Errors**:
   - Verify Watsonx project ID is correct
   - Check embedding model ID matches ingestion
   - Ensure sufficient Watsonx quota

4. **Search Returns No Results**:
   - Verify index/collection name matches ingestion
   - Check that data was successfully ingested
   - Ensure embedding model matches ingestion model

### Bootstrap Logs

The server performs connectivity checks on startup:

```
[BOOTSTRAP] WATSONX_EMBEDDINGS: OK - model=intfloat/multilingual-e5-large
[BOOTSTRAP] OPENSEARCH: OK - your-host:9200 ssl=True
```

## Performance Tuning

### Code Engine Settings

```bash
# High-performance configuration
ibmcloud ce application update --name rag-retrieval-api \
  --cpu 2 \
  --memory 4G \
  --min-scale 2 \
  --max-scale 10 \
  --concurrency 100 \
  --concurrency-target 80
```

### Request Optimization

- Use appropriate `k` values (5-10 for most use cases)
- Implement caching for frequently searched queries
- Consider batch processing for multiple queries

## Security Best Practices

1. **Always use Bearer token authentication in production**:
   ```bash
   APP_BEARER_TOKEN=your_strong_random_token
   ```

2. **Use secrets for sensitive data**:
   - Never commit `.env` files
   - Use Code Engine secrets for credentials
   - Rotate tokens regularly

3. **Enable SSL/TLS**:
   ```bash
   OPENSEARCH_USE_SSL=true
   MILVUS_SECURE=true
   ```

4. **Restrict CORS origins**:
   ```bash
   ALLOWED_ORIGINS=https://your-app.com,https://your-other-app.com
   ```

## Integration with Frontend

### JavaScript/TypeScript Example

```typescript
const API_URL = 'https://your-app-url';
const API_TOKEN = 'your_bearer_token';

async function searchDocuments(query: string, k: number = 5) {
  const response = await fetch(`${API_URL}/retrieve`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_TOKEN}`
    },
    body: JSON.stringify({ query, k })
  });
  
  if (!response.ok) {
    throw new Error(`Search failed: ${response.statusText}`);
  }
  
  return await response.json();
}

// Usage
const results = await searchDocuments('laptop features', 5);
console.log(results.results);
```

### Python Example

```python
import requests

API_URL = 'https://your-app-url'
API_TOKEN = 'your_bearer_token'

def search_documents(query: str, k: int = 5):
    response = requests.post(
        f'{API_URL}/retrieve',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_TOKEN}'
        },
        json={'query': query, 'k': k}
    )
    response.raise_for_status()
    return response.json()

# Usage
results = search_documents('laptop features', 5)
for result in results['results']:
    print(f"{result['title']}: {result['text'][:100]}...")
```

## Cost Optimization

### Code Engine Pricing Considerations

1. **Scale to Zero**: Set `--min-scale 0` for development environments
2. **Right-size Resources**: Start with minimal CPU/memory and scale up as needed
3. **Request Batching**: Combine multiple queries when possible
4. **Caching**: Implement response caching for common queries

## Support and Documentation

- **FastAPI Docs**: Available at `http://your-app-url/docs` (auto-generated)
- **OpenAPI Spec**: Available at `http://your-app-url/openapi.json`
- **IBM Code Engine Docs**: https://cloud.ibm.com/docs/codeengine

## License

This project is part of the RAG retrieval system for the retail application.

## Related Projects

- **RAG Ingestion MCP Server**: For ingesting documents into vector databases
- **RAG Retrieval MCP Server**: MCP protocol version of this server
- **Retail Application**: Frontend application using this API