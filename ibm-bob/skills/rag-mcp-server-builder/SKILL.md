---
name: rag-mcp-server-builder
description: Expert guidance for building IBM RAG MCP servers (SSE and stdio transport) using the building-blocks mcp-server pattern — covers registerTool for ingest/retrieve/search operations, IBM watsonx.ai embedding calls, Milvus/OpenSearch connections, IBM COS source integration, SSE server deployment on IBM Code Engine, and integration with IBM Bob.
---

# IBM RAG MCP Server Builder

## Purpose

Expert guidance for building **Model Context Protocol (MCP) servers** that expose RAG capabilities (ingestion, retrieval, hybrid search) as tools consumable by IBM Bob, Claude, and other MCP-compatible AI assistants.

## IBM Cloud Product Coverage

| IBM Cloud Product | MCP Role |
|---|---|
| IBM watsonx.ai | Embedding generation tool |
| IBM watsonx.data (Milvus/OpenSearch) | Vector storage and retrieval tool |
| IBM Cloud Object Storage | Document ingestion source tool |
| IBM Code Engine | MCP server deployment (SSE transport) |
| IBM Cloud IAM | Authentication for all watsonx calls |

## Rules

- Use `fastmcp` or the `mcp` Python SDK for server implementation
- SSE transport: serve at `GET /sse` and `POST /messages/`
- stdio transport: pipe JSON-RPC messages through stdin/stdout
- Tool names: use `snake_case` (e.g. `ingest_documents`, `search_documents`, `hybrid_search`)
- Always validate inputs with Pydantic v2 before calling IBM services
- IBM Code Engine: expose port 8080; set `SSE_TRANSPORT=true` env var

---

## Scope

- RAG ingestion MCP tools (from IBM COS to Milvus/OpenSearch)
- RAG retrieval MCP tools (vector search, keyword search, hybrid search)
- Embedding generation MCP tools (IBM watsonx.ai)
- SSE transport server for remote deployment on IBM Code Engine
- stdio transport server for local IBM Bob integration

---

## Procedure

### Phase 1: MCP Server Structure (SSE)

```python
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from fastapi import FastAPI

server = Server("rag-retrieval-server")
app = FastAPI()
sse = SseServerTransport("/messages/")

@app.get("/sse")
async def handle_sse(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())
```

### Phase 2: Register Retrieval Tool

```python
from mcp.types import Tool, TextContent

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="search_documents",
            description="Semantic search over IBM watsonx.data vector store using IBM watsonx.ai embeddings",
            inputSchema={
                "type": "object",
                "properties": {
                    "query":      {"type": "string", "description": "Natural language search query"},
                    "index_name": {"type": "string", "description": "Vector index / collection name"},
                    "top_k":      {"type": "integer", "default": 5},
                    "search_type":{"type": "string", "enum": ["vector", "keyword", "hybrid"], "default": "hybrid"},
                },
                "required": ["query", "index_name"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "search_documents":
        results = await do_search(
            query=arguments["query"],
            index_name=arguments["index_name"],
            top_k=arguments.get("top_k", 5),
            search_type=arguments.get("search_type", "hybrid"),
        )
        return [TextContent(type="text", text=json.dumps(results, indent=2))]
```

### Phase 3: IBM watsonx.ai Embedding in Tool

```python
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Embeddings

async def embed_query(text: str) -> list[float]:
    embedder = Embeddings(
        model_id="ibm/slate-125m-english-rtrvr",
        credentials=Credentials(url=WATSONX_URL, api_key=IBM_API_KEY),
        project_id=WATSONX_PROJECT_ID,
    )
    return embedder.embed_query(text)
```

### Phase 4: IBM Code Engine Deployment

```bash
# Build and push container
ibmcloud ce build create --name rag-mcp --source . --dockerfile Dockerfile
ibmcloud ce application create \
  --name rag-mcp-server \
  --image us.icr.io/my-namespace/rag-mcp:latest \
  --port 8080 \
  --env IBM_API_KEY=$IBM_API_KEY \
  --env WATSONX_PROJECT_ID=$WATSONX_PROJECT_ID \
  --env OPENSEARCH_HOST=$OPENSEARCH_HOST
```

### Key IBM Cloud URLs

| Service | URL |
|---|---|
| IBM IAM Token | `https://iam.cloud.ibm.com/identity/token` |
| IBM watsonx.ai (us-south) | `https://us-south.ml.cloud.ibm.com` |
| IBM Code Engine (us-south) | `https://api.us-south.codeengine.cloud.ibm.com/v2` |
