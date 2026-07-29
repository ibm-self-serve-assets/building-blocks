# watsonx Orchestrate Tools and Toolkits
Guide to authoring, importing, packaging, and managing watsonx Orchestrate tools and toolkits with the ADK CLI.  Tools are executable capabilities that agents call. Toolkits are packaging units that expose multiple related tools and let you manage them together.

```text
Agent -> calls tool
Agent -> calls toolkit-exposed tool as toolkit_name:tool_name
Toolkit -> packages related Python or MCP tools
Connection -> supplies credentials/env values to tools/toolkits
```

## Tool types

| Type | Import kind | Use when |
|---|---:|---|
| OpenAPI tool | `openapi` | Remote service already has a clean OpenAPI 3.0 JSON API. |
| Python tool | `python` | You need custom logic, data shaping, SDK calls, or focused agent-friendly behavior. |
| Agentic workflow | `flow` | You need async, multi-step orchestration across agents, tools, people, decisions, loops, or approvals. |
| Langflow tool | `langflow` | You built a visual Langflow flow and want to expose it as a tool. |
| MCP toolkit | `mcp` | You want to expose tools from local/remote MCP servers. |
| Python toolkit | `python` toolkit | You want to package multiple Python tools into one shared runtime. |

## Tool naming

Rules:

- Prefer `snake_case`.
- Make names action-oriented and domain-specific.
- Avoid generic names like `run`, `process`, `helper`, or `fetch_data`.
- Design each tool to complete one focused task with clear inputs and outputs.

Toolkit-exposed tools are referenced as:

```text
toolkit_name:tool_name
```

Agent YAML example:

```yaml
tools:
  - github:list_issues
  - contract_tools:extract_clauses
  - get_vendor_record
```

## OpenAPI tools

Use OpenAPI tools when the API spec is agent-friendly.

Requirements:

- OpenAPI version `3.0`.
- Endpoints accept and return JSON.
- `servers` block contains exactly one URL.
- Server URL cannot be parameterized.
- Every exposed endpoint has an `operationId`; this becomes the tool name.
- Every exposed endpoint has a description that tells the agent when and why to use it.
- Prefer `snake_case` for `operationId`.

Minimal OpenAPI pattern:

```yaml
openapi: 3.0.0
info:
  title: Vendor API
  version: 1.0.0
servers:
  - url: https://api.example.com
paths:
  /vendors/{vendor_id}:
    get:
      operationId: get_vendor_record
      description: Retrieve vendor profile, risk status, and payment metadata by vendor ID.
      parameters:
        - name: vendor_id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Vendor record
          content:
            application/json:
              schema:
                type: object
```

Import:

```bash
orchestrate tools import -k openapi -f openapi/vendor-api.yaml -a vendor_api_connection
```

OpenAPI callback pattern for async tools:

```yaml
paths:
  /long-running-job:
    post:
      operationId: start_vendor_risk_scan
      description: Starts a long-running vendor risk scan and returns results through callbackUrl.
      parameters:
        - in: header
          name: callbackUrl
          description: Callback URL supplied by Orchestrate.
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
      callbacks:
        callback:
          '{$request.header.callbackUrl}':
            post:
              requestBody:
                content:
                  application/json:
                    schema:
                      type: object
              responses:
                "200":
                  description: Callback received
```

Prefer Python tools over OpenAPI tools when:

- the OpenAPI spec has many broad endpoints;
- endpoint descriptions are too thin;
- multiple API calls must be composed;
- inputs/outputs need transformation;
- the operation is not naturally a single API request.

## Python tools

A Python tool is a function decorated with `@tool`. The function name is the default tool name. Type hints and docstrings become the tool schema and model-facing description.

```python
# tools/vendor_tools.py
from ibm_watsonx_orchestrate.agent_builder.tools import tool

@tool()
def get_vendor_risk(vendor_id: str) -> dict:
    """Retrieve vendor risk status by vendor ID.

    Args:
        vendor_id (str): Unique vendor identifier from the procurement system.

    Returns:
        dict: Vendor risk score, status, and summary evidence.
    """
    return {
        "vendor_id": vendor_id,
        "risk_score": 72,
        "status": "medium",
        "evidence": ["late delivery trend", "contract renewal pending"],
    }
```

Best practices:

- Use Google-style docstrings.
- Use explicit type hints for every argument and return value.
- Prefer `async def` for I/O-heavy tools.
- Use async HTTP clients such as `httpx` or `aiohttp` for external calls.
- Keep each tool focused; do not hide a full agent loop inside a tool.
- Pin dependencies exactly in `requirements.txt`.
- Treat tool code as normal Python: unit test before importing.

Import individual Python tool:

```bash
orchestrate tools import \
  -k python \
  -f tools/vendor_tools.py \
  -r requirements.txt \
  -a vendor_api_connection
```

Multi-file Python tool/package:

```bash
orchestrate tools import \
  -k python \
  -f tools/vendor_tools.py \
  --package_root ./src \
  -r requirements.txt \
  -a vendor_api_connection
```

Auto-discover functions from ordinary Python code:

```bash
orchestrate tools auto-discover \
  --file src/vendor_api.py \
  --output tools/vendor_tools.py \
  --env-file .env \
  --llm groq/openai/gpt-oss-120b \
  --function get_vendor_risk \
  --function list_vendor_contracts
```

## Python tool credentials

Use `expected_credentials` when a tool expects a connection.

```python
from base64 import b64encode
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType
from ibm_watsonx_orchestrate.run import connections

@tool(expected_credentials=[{"app_id": "vendor_api", "type": ConnectionType.BASIC_AUTH}])
def get_vendor_record(vendor_id: str) -> dict:
    """Retrieve a vendor record from the vendor API.

    Args:
        vendor_id (str): Vendor ID.

    Returns:
        dict: Vendor record.
    """
    conn = connections.basic("vendor_api")
    token = b64encode(f"{conn.username}:{conn.password}".encode()).decode()
    headers = {"Authorization": f"Basic {token}"}
    # call API with headers
    return {"vendor_id": vendor_id, "headers_used": bool(headers)}
```

## Python tool logging

Use `SpanLogger` for tool-level observability.

```python
from ibm_watsonx_orchestrate.run.logging import SpanLogger

logger = SpanLogger()
logger.info("Starting vendor lookup")
logger.error("Vendor API returned an error")
```

Guidance:

- Logs are captured per tool invocation.
- Logs are associated with execution trace data.
- The most recent log data is capped; do not rely on tool logs as durable storage.
- For high-volume logs, write to external storage and correlate with request/thread IDs.

## Python tools with file input

Use `WXOFile` for uploaded files.

```python
from ibm_watsonx_orchestrate.agent_builder.tools import tool, WXOFile

@tool()
def read_uploaded_contract(contract_file: WXOFile) -> dict:
    """Read metadata and bytes from an uploaded contract file.

    Args:
        contract_file (WXOFile): Uploaded file reference.

    Returns:
        dict: File name, content type, and size.
    """
    return {
        "file_name": WXOFile.get_file_name(contract_file),
        "file_size": WXOFile.get_file_size(contract_file),
        "file_type": WXOFile.get_file_type(contract_file),
    }
```

Multiple files:

```python
from typing import Annotated, List
from ibm_watsonx_orchestrate.agent_builder.tools import tool, WXOFile, MultiFileConstraints

@tool()
def ingest_support_docs(
    files: Annotated[
        List[WXOFile],
        MultiFileConstraints(
            min_files=1,
            max_files=5,
            max_size_per_file=5_248_800,
            accepted_file_extensions=["pdf", "docx", "txt"],
        ),
    ]
) -> dict:
    """Ingest support documents and return file names.

    Args:
        files (List[WXOFile]): Uploaded files.

    Returns:
        dict: File names by index.
    """
    return {str(i): WXOFile.get_file_name(file) for i, file in enumerate(files)}
```

## Common Tool management CLI

```bash
orchestrate tools list -v
orchestrate tools import \
  -k python \
  -f tools/vendor_tools.py \
  -r requirements.txt \
  -a vendor_api_connection

orchestrate tools export -n get_vendor_record -o get_vendor_record.zip

orchestrate tools remove -n get_vendor_record
```

## Toolkits

Use toolkits to group related tools and manage them as one unit.

Supported toolkit types:

- MCP toolkits
- Python toolkits

### Toolkit naming convention

After import, tools are exposed individually:

```text
toolkit_name:tool_name
```

Agent YAML:

```yaml
tools:
  - github:list_issues
  - github:get_pull_request
  - procurement:get_vendor_record
```

## Python toolkits

Use Python toolkits when you have multiple Python tools that should share one runtime process.

Benefits:

- faster execution than launching a lightweight process per tool call;
- one package for related tools;
- easier reuse across agents.

Constraints:

- tools must be thread-safe and reentrant;
- package all required files in one folder;
- redeploy related agents after toolkit updates.

Folder pattern:

```text
my_toolkit/
  requirements.txt
  pyproject.toml        # optional, if packaged
  vendor_tools.py
  contract_tools.py
  __init__.py
```

Add Python toolkit:

```bash
orchestrate toolkits add \
  --kind python \
  --name procurement \
  --description "Procurement and vendor-management tools" \
  --tier small \
  --package_root ./my_toolkit
```

Import Python toolkit from YAML:

```yaml
# procurement_toolkit.yaml
spec_version: v1
kind: python
name: procurement
description: Procurement and vendor-management tools
environment:
  LOG_LEVEL: INFO
```

```bash
orchestrate toolkits import -f procurement_toolkit.yaml --app-id procurement_env
```

## Local MCP toolkits

Use local MCP toolkits when the MCP server package runs inside the Orchestrate runtime through stdio.

Python MCP server folder:

```text
mcp_server/
  server.py
  requirements.txt
```

Import local Python MCP toolkit:

```bash
orchestrate connections add -a my_connection
for env in draft live; do
  orchestrate connections configure -a my_connection --env $env --type team --kind key_value
  orchestrate connections set-credentials -a my_connection --env $env -e "SECURE_ENVIRONMENT_VARIABLE=value"
done

orchestrate toolkits add \
  --kind mcp \
  --name local_docs \
  --description "Local document MCP tools" \
  --package_root ./mcp_server \
  --command "python server.py" \
  --tools "*" \
  --app-id "my_connection"
```

Node MCP server folder:

```text
my-mcp-server/
  package.json
  index.js
```

Import local Node MCP toolkit:

```bash
orchestrate toolkits add \
  --kind mcp \
  --name node_docs \
  --description "Node MCP document tools" \
  --package_root ./my-mcp-server \
  --command "node index.js" \
  --tools "*" \
  --app-id "my_connection"
```

Import local MCP toolkit from YAML:

```yaml
# toolkit_name.yaml
spec_version: v1
kind: mcp
name: toolkit_name
command: uvx ibm-watsonx-orchestrate-mcp-server
tools:
  - "*"
connections:
  - my_connection
package_root: ./my_toolkit_folder
```

```bash
orchestrate toolkits import -f toolkit_name.yaml -a my_connection
```

## Remote MCP toolkits

Use remote MCP when tools are hosted outside Orchestrate.

Supported transports:

- `sse`
- `streamable_http`

Import remote MCP over SSE:

```bash
orchestrate toolkits add \
  --kind mcp \
  --name coingecko \
  --description "CoinGecko toolkit" \
  --url "https://mcp.api.coingecko.com/sse" \
  --transport "sse" \
  --tools "get_range_coins_market_chart"
```

Import remote MCP over streamable HTTP:

```bash
orchestrate toolkits add \
  --kind mcp \
  --name github \
  --description "GitHub Copilot remote MCP tools" \
  --url "https://api.githubcopilot.com/mcp/" \
  --transport "streamable_http" \
  --tools "list-issues" \
  --app-id "mcpgithub"
```

Remote MCP YAML:

```yaml
spec_version: v1
kind: mcp
name: github
transport: streamable_http
server_url: https://api.githubcopilot.com/mcp/
tools:
  - list-issues
connections:
  - mcpgithub
```

```bash
orchestrate toolkits import -f github_mcp.yaml -a mcpgithub
```

Allowed context for remote MCP:

```yaml
spec_version: v1
kind: mcp
name: doc_mcp
description: Document MCP toolkit
url: https://example.com/mcp
transport: streamable_http
metadata:
  allowed_context:
    - tenant_id
    - agent_id
```

## Toolkit management CLI

List:

```bash
orchestrate toolkits list -v
```

Export:

```bash
orchestrate toolkits export -n my-toolkit -o my-toolkit.zip
```

Update Python toolkit by re-adding with same name:

```bash
orchestrate toolkits add \
  --kind python \
  --name procurement \
  --description "Updated procurement tools" \
  --tier small \
  --package_root ./my_toolkit
```

Update MCP toolkit by remove + re-add + re-import dependent agents:

```bash
orchestrate toolkits remove -n github

orchestrate toolkits add \
  --kind mcp \
  --name github \
  --description "Updated GitHub MCP tools" \
  --url "https://api.githubcopilot.com/mcp/" \
  --transport "streamable_http" \
  --tools "*" \
  --app-id "mcpgithub"

orchestrate agents import -f agents/dev_agent.yaml
```

Remove toolkit and all tools it provides:

```bash
orchestrate toolkits remove -n procurement
```
