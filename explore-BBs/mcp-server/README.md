# Building Blocks MCP Server (Remote)

Remote MCP server for discovering and exploring [IBM Technology Building Blocks](https://github.com/ibm-self-serve-assets/building-blocks/) — designed for deployment on IBM Code Engine (or any container platform).

Uses **Streamable HTTP** transport. No authentication required (read-only, public data).

## Tools

| Tool | Description |
|------|-------------|
| `list_building_blocks` | List/filter all building blocks by group, capability, or tag |
| `search_building_blocks` | Search across building block names, docs, and code |
| `get_building_block` | Get full details about a building block (metadata + README) |
| `get_building_block_readme` | Fetch README for a block or sub-component |
| `list_docs_pages` | List documentation pages from the docs site |
| `get_docs_page` | Fetch raw markdown content of a docs page |
| `list_assets` | Browse code files and configs within a building block |
| `get_asset_file` | Retrieve content of a specific code/config file |
| `list_bob_modes` | List Bob Modes (watsonx Orchestrate configs) |
| `get_bob_mode_info` | Get README and details for a specific Bob Mode |
| `download_bob_mode` | Get the direct download URL for a Bob Mode ZIP file |

## Architecture

- **Transport**: Streamable HTTP (`/mcp` endpoint)
- **Health check**: `GET /health` (for Code Engine probes)
- **Stateless**: `stateless_http=True` — safe for multi-instance auto-scaling
- **Port**: 9247 (override with `PORT` env var)

### Request flow

```
MCP client (Bob / Claude / etc.)
   │  POST /mcp  (Streamable HTTP, JSON-RPC)
   ▼
server.py — FastMCP app on port 9247
   │
   ├─► tools/discover.py    ─┐
   ├─► tools/details.py      │  each tool does one of:
   ├─► tools/docs.py         │    a) read registry.py (instant, zero API calls)
   ├─► tools/assets.py       │    b) call github_client.py (cached httpx)
   └─► tools/bob_modes.py   ─┘
                              │
                              ▼
              GitHub API + raw.githubusercontent.com
```

### Two-tier data design

- **`registry.py`** is a hand-maintained static catalog (3 capabilities → 8 groups → 24 building blocks + docs pages). Discovery/listing tools answer from this — no network round-trip. Update it when upstream adds new blocks (see [Updating the catalog](#updating-the-catalog)).
- **`github_client.py`** is a lazy-singleton `httpx` client used for live file fetches (READMEs, code, directory listings) with a TTL cache (5 min default, 10 min for repo trees, 2 min for code search) and capped at 500 entries.

### File map

| File | Role |
|------|------|
| `src/building_blocks_mcp_remote/server.py` | Entry point. Creates the `FastMCP` app, registers `/health`, imports tool modules, runs `streamable-http` transport. |
| `src/building_blocks_mcp_remote/registry.py` | Static catalog of capabilities, groups, blocks, docs pages. |
| `src/building_blocks_mcp_remote/github_client.py` | Singleton httpx client + TTL cache. Exposes `fetch_raw_file`, `fetch_contents`, `fetch_tree`, `search_code`. |
| `src/building_blocks_mcp_remote/tools/discover.py` | `list_building_blocks`, `search_building_blocks`. |
| `src/building_blocks_mcp_remote/tools/details.py` | `get_building_block`, `get_building_block_readme`. |
| `src/building_blocks_mcp_remote/tools/docs.py` | `list_docs_pages`, `get_docs_page`. |
| `src/building_blocks_mcp_remote/tools/assets.py` | `list_assets`, `get_asset_file`. |
| `src/building_blocks_mcp_remote/tools/bob_modes.py` | `list_bob_modes`, `get_bob_mode_info`, `download_bob_mode`. |
| `pyproject.toml` | Deps + CLI script (`building-blocks-mcp-remote` → `server.main`). |
| `Dockerfile` | Container image. Python 3.12-slim + `uv sync`, exposes 9247. |

### How tools register

Each tool module does `from building_blocks_mcp_remote.server import mcp` and decorates functions with `@mcp.tool()`. `server.py` imports the tool modules *after* creating the `mcp` instance (see the `# noqa: E402` lines at the bottom of `server.py`). There is no central tool registry — importing a module is what registers its tools.

The function's **docstring becomes the description the LLM sees**, so write it for an LLM audience: state purpose, args, return shape, and (when useful) when to prefer this tool over another.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_TOKEN` | Recommended | — | GitHub PAT for higher rate limits (60 -> 5,000 req/hr) |
| `PORT` | No | 9247 | HTTP port to listen on |

## Token Setup

The `GITHUB_TOKEN` is technically optional but practically required — without it you get 60 req/hr (shared across all clients of the deployment) and no code search.

### Required scope

Only `public_repo` is needed. The upstream `ibm-self-serve-assets/building-blocks` repo is public; do **not** grant `repo` (full private access) — it's unnecessary and increases blast radius if the token leaks.

### Who uses what token

- **Local dev**: each contributor mints their own PAT and exports it in their shell. Don't share personal PATs — they're tied to one GitHub identity and silently break when that person rotates them or leaves.
- **Deployed app**: use a **dedicated service-account PAT** owned by the team (a "machine user" GitHub account), stored in a team vault (1Password / shared secret store) and injected via the platform's secret mechanism — never committed to the repo.

### Minting a PAT

GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token. Set repository access to "Public repositories (read-only)". Expiration: 90 days is a reasonable default; calendar a rotation.

### Rotating the production token

```bash
ibmcloud ce app update --name building-blocks-mcp --env GITHUB_TOKEN=<new-pat>
```

Code Engine performs a rolling restart — no downtime if `max-scale > 1`.

## Local Development

### 1. Install dependencies

```bash
cd mcp-server
uv sync
```

### 2. Run locally

```bash
export GITHUB_TOKEN="ghp_..."  # optional
uv run building-blocks-mcp-remote
```

### 3. Test

```bash
# Health check
curl http://localhost:9247/health

# MCP endpoint
curl -X POST http://localhost:9247/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

### 4. Connect from an MCP client

```json
{
  "mcpServers": {
    "building-blocks": {
      "url": "http://localhost:9247/mcp"
    }
  }
}
```

## Deploy to IBM Code Engine

### 1. Target the right region & resource group

```bash
ibmcloud target -r us-south -g <your-resource-group>
```

### 2. Log in and set up

```bash
ibmcloud login
ibmcloud plugin install code-engine   # if not already installed
ibmcloud ce project create --name building-blocks-mcp
```

### 3. Deploy from source

```bash
ibmcloud ce app create \
  --name building-blocks-mcp \
  --build-source . \
  --port 9247 \
  --min-scale 0 \
  --max-scale 3 \
  --env GITHUB_TOKEN=<your-github-pat>
```

### 4. Get the app URL

```bash
ibmcloud ce app get --name building-blocks-mcp --output url
```

### 5. Connect clients

```json
{
  "mcpServers": {
    "building-blocks": {
      "url": "https://building-blocks-mcp.<project-id>.codeengine.appdomain.cloud/mcp"
    }
  }
}
```

## Operations

### Update an existing deployment

```bash
ibmcloud ce app update \
  --name building-blocks-mcp \
  --build-source .
```

### View logs

```bash
ibmcloud ce app logs --name building-blocks-mcp --follow
```

### Tear down

```bash
ibmcloud ce app delete --name building-blocks-mcp --force
ibmcloud ce project delete --name building-blocks-mcp --force   # only if you also want to drop the project
```

## Extending

### Adding a new tool

1. Create `src/building_blocks_mcp_remote/tools/your_tool.py`:

   ```python
   from building_blocks_mcp_remote.server import mcp
   from building_blocks_mcp_remote.github_client import fetch_raw_file  # or whichever helper

   @mcp.tool()
   def your_tool(arg: str) -> dict:
       """One-line summary the LLM will read.

       Longer description: when to use this, when not to.

       Args:
           arg: what it means.

       Returns:
           Shape of the dict.
       """
       ...
   ```

2. Register it by adding one import in `server.py` alongside the others:

   ```python
   from building_blocks_mcp_remote.tools import your_tool  # noqa: E402, F401
   ```

3. Add a row to the **Tools** table at the top of this README.

Prefer the helpers in `github_client.py` over raw `httpx` calls — you get caching and the shared auth header for free.

### Updating the catalog

When a new building block is added upstream, edit `BUILDING_BLOCKS` in `registry.py`. The dict key **must match the GitHub folder name** under `ibm-self-serve-assets/building-blocks/` — that's how `fetch_raw_file` resolves paths. Add the block to the correct `group`, set `capability`, and include any tags users might search by.

If a new top-level group or capability is introduced, also update `GROUPS` / `CORE_CAPABILITIES` and the `instructions=...` string in `server.py` (which is the system prompt the LLM sees on connect).

### Testing changes locally

```bash
uv run building-blocks-mcp-remote
# in another terminal:
curl -X POST http://localhost:9247/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | jq
```

For end-to-end testing, point a local MCP client at `http://localhost:9247/mcp` using `client_configs/local_test.json`.

## Troubleshooting

| Symptom | Likely cause | Check |
|---------|--------------|-------|
| `403 rate limit exceeded` from GitHub | Token missing or unauthenticated requests over 60/hr | Look in logs for `GitHub client initialized with authentication`. If you see the warning `GITHUB_TOKEN not set`, the env var isn't reaching the container. |
| Stale data after upstream change | TTL cache (5–10 min) | Restart the app: `ibmcloud ce app update --name building-blocks-mcp` — the cache is in-process. |
| `search_building_blocks` with `mode="code"` returns empty | Code search requires authentication | Confirm `GITHUB_TOKEN` is set on the deployment. |
| Health check failing on Code Engine | Wrong port or app not listening on `0.0.0.0` | The `--port` flag must match `PORT` env (default 9247). Server already binds `0.0.0.0`. |
| New tool not showing up in `tools/list` | Module not imported in `server.py` | Add the `from ... import your_tool` line — see [Adding a new tool](#adding-a-new-tool). |

## License

Apache 2.0
