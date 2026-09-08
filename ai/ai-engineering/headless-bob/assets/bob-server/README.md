# Bobserver

> **Demo UI** — open `bobui/index.html` directly in your browser (no build step needed).
> Point it at your running Bobserver instance and enter your credentials.

Bobserver is a protected REST and MCP service that wraps IBM Bob Shell in a managed API. It provides async Bob runs, guided 5-phase planning sessions (Bob+), Plan → Approve → Execute workflows, and an MCP JSON-RPC endpoint — all secured with Basic Auth or OAuth2 bearer tokens.

**Built with:** Python 3.11 · FastAPI · Bob Shell CLI · SQLite · OpenShift / Docker

**When to use it:**
- You want to call Bob Shell from automation, CI, or another LLM without managing workspaces yourself
- You want a guided planning assistant (Bob+) that steps through Describe → Discovery → Architecture → Spec
- You want to expose Bob as an MCP tool to Claude Desktop, Cursor, or any MCP-compatible client
- You want Plan → Approve → Execute workflows with human approval gates

### Core concepts

| | |
|---|---|
| ⚡ **Bob Runs** | Send a one-off prompt directly to Bob Shell and watch the output stream back in real time. |
| 🗺 **Bob+ Sessions** | A guided 5-phase planning conversation (Describe → Discovery → Architecture → Spec) where Bob helps you think through and document a project idea step by step. |
| 🔁 **Workflows** | Bob drafts a plan first, you review and approve it, then Bob executes — giving you a human checkpoint before anything runs. |

---

## Architecture

![Bobserver API Architecture](diagrams/Bobserver%20API%20Architecture%20Flowchart.png)

> Full source (Mermaid): [`diagrams/architecture.mmd`](diagrams/architecture.mmd)

---

## Authentication

### 1. Basic Auth (always on)
Every `/api/*` and `/mcp` request requires HTTP Basic Auth. Default credentials:

| Variable | Default |
|----------|---------|
| `BOBSERVER_ADMIN_USERNAME` | `admin` |
| `BOBSERVER_ADMIN_PASSWORD` | `nowibm` |

```bash
curl -u admin:nowibm http://localhost:8080/api/bob/jobs
```

### 2. OAuth 2.1 / PKCE (for MCP clients)
Bobserver runs its own OAuth authorization server — no external IdP needed. MCP clients (Claude Desktop, Cursor, Glama) use this to authenticate automatically.

| Endpoint | Purpose |
|----------|---------|
| `POST /oauth/register` | Dynamic client registration |
| `GET/POST /oauth/authorize` | Authorization code + PKCE flow |
| `POST /oauth/token` | Token exchange |
| `GET /.well-known/oauth-authorization-server` | Discovery metadata |

See [`docs/claude-desktop-mcp.md`](docs/claude-desktop-mcp.md) for a full walkthrough and smoke-test commands.

> **IBM App ID SSO** is also supported for enterprise deployments — set `BOBSERVER_APPID_CLIENT_ID` and `BOBSERVER_APPID_DISCOVERY_ENDPOINT` in [`.env.example`](.env.example).

---

## API Endpoints

### Core
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/healthz` | Liveness probe — returns `{"status":"ok"}` |
| `POST` | `/api/bob/prompt` | Run Bob synchronously and return the full result |
| `POST` | `/api/bob/stream` | Run Bob and stream output as Server-Sent Events |

### Async Bob Jobs
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/bob/jobs` | Start a Bob run asynchronously, returns a `jobId` |
| `GET` | `/api/bob/jobs` | List all jobs |
| `GET` | `/api/bob/jobs/{jobId}` | Poll job status and output (use `?offset=N` for incremental reads) |
| `POST` | `/api/bob/jobs/{jobId}/cancel` | Cancel a running job |
| `DELETE` | `/api/bob/jobs/{jobId}` | Delete a completed job and its workspace |
| `GET` | `/api/bob/jobs/{jobId}/artifacts/{name}` | Download a job artifact (`bob-run.json`, `workspace.zip`, or any markdown file) |

### Bob+ Planning Sessions
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/sessions` | Create a new 5-phase planning session |
| `GET` | `/api/sessions/current` | Get the currently active session |
| `POST` | `/api/sessions/{id}/message` | Send a message in the current phase |
| `POST` | `/api/sessions/{id}/advance` | Advance to the next phase |
| `GET` | `/api/sessions/{id}/artifact/{phaseId}` | Read the output artifact for a completed phase |
| `DELETE` | `/api/sessions/{id}` | Delete a session |

### Workflows (Plan → Approve → Execute)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/workflows` | Create a workflow and start the Plan phase |
| `GET` | `/api/workflows` | List all workflows |
| `GET` | `/api/workflows/{id}` | Get workflow status and details |
| `POST` | `/api/workflows/{id}/approve` | Approve (or reject) the plan to trigger execution |
| `POST` | `/api/workflows/{id}/cancel` | Cancel a workflow |
| `DELETE` | `/api/workflows/{id}` | Delete a workflow and its workspace |
| `GET` | `/api/workflows/{id}/artifacts/{name}` | Download a workflow artifact |

### MCP (JSON-RPC)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/mcp` | MCP JSON-RPC endpoint — exposes `bob_prompt_start`, `bob_prompt_status`, `bob_prompt_cancel` |

See [`docs/claude-desktop-mcp.md`](docs/claude-desktop-mcp.md) for full MCP usage, OAuth 2.1/PKCE setup, and smoke-test `curl` commands.

### OAuth & Auth
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/.well-known/oauth-protected-resource` | OAuth resource metadata |
| `GET` | `/.well-known/oauth-authorization-server` | OAuth authorization server metadata |
| `POST` | `/oauth/register` | Dynamic client registration |
| `GET/POST` | `/oauth/authorize` | Authorization code + PKCE flow |
| `POST` | `/oauth/token` | Token exchange |
| `GET` | `/auth/login` | IBM App ID SSO login (optional) |
| `GET` | `/auth/logout` | Clear App ID session |

### Slack Integration
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/slack/command` | Slash command handler — runs Bob and posts result via `response_url` |
| `POST` | `/slack/events` | Event subscription handler for app mentions |
| `POST` | `/slack/interactivity` | Interactivity handler |

---

## Install & Run

### Prerequisites
- Python 3.11+
- Bob Shell (`bob`) — installed inside the Docker image; locally use `BOBSERVER_BOB_COMMAND=cat` to mock
- A `BOBSHELL_API_KEY`

### Skills Configuration

Bobserver can automatically load custom Bob skills into its execution workspaces. To make skills available to Bobserver:
1. Choose the skills you need from the central repository at [`building-blocks/ibm-bob/skills/`](../../../../../ibm-bob/skills/).
2. Copy the desired skill folders into [`skills/`](skills/):
   ```bash
   # Example: copy the agent skill into bob-server/skills
   cp -r ../../../../../ibm-bob/skills/agent skills/
   ```
3. When Bobserver provisions workspaces for runs or jobs, it will automatically make these skills accessible to Bob.

### Local (Python)

```bash
cd bobserver
python -m venv ../venv && source ../venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env
# Fill in BOBSHELL_API_KEY and set BOBSERVER_BOB_COMMAND=cat for local testing

mkdir -p /tmp/bobserver-workspace
uvicorn bobserver.main:app --host 0.0.0.0 --port 8080 --reload
```

API and interactive docs available at:
- `http://localhost:8080/docs` — Swagger UI
- `http://localhost:8080/redoc` — ReDoc

### Docker

```bash
docker build -t bobserver:local .

docker run -p 18080:8080 \
  -e BOBSERVER_ADMIN_USERNAME=admin \
  -e BOBSERVER_ADMIN_PASSWORD=nowibm \
  -e BOBSHELL_API_KEY="$BOBSHELL_API_KEY" \
  bobserver:local
```

### OpenShift

```bash
oc apply -f openshift/bobserver.yaml
oc set env deploy/bobserver BOBSHELL_API_KEY="$BOBSHELL_API_KEY"
```

---

## Key Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `BOBSHELL_API_KEY` | — | **Required.** Bob Shell authentication key |
| `BOBSERVER_ADMIN_USERNAME` | `admin` | Basic Auth username |
| `BOBSERVER_ADMIN_PASSWORD` | `nowibm` | Basic Auth password |
| `BOBSERVER_BOB_COMMAND` | `bob` | Bob CLI binary — set to `cat` to mock locally |
| `BOBSERVER_WORKSPACE_ROOT` | `/workspace` | Root for all Bob run workspaces; set to `/tmp/bobserver-workspace` locally |
| `BOBSERVER_BOB_MCP_CONFIG` | `.bob/mcp.json` | MCP config file seeded into every Bob run workspace |
| `BOBSERVER_BOB_MAX_COINS` | `30` | Max Bob token budget per run |
| `BOBSERVER_EXECUTOR_TIMEOUT_SECONDS` | `900` | Max runtime for a Bob job |

For App ID SSO, Slack, and SMTP options see [`.env.example`](.env.example).

---

## Reference

| Resource | Description |
|----------|-------------|
| [`docs/claude-desktop-mcp.md`](docs/claude-desktop-mcp.md) | MCP endpoint, OAuth 2.1/PKCE, smoke-test curl commands |
| [`docs/our-approach.html`](docs/our-approach.html) | Architecture overview |
| [`docs/bob_mcp_plus_ansible.html`](docs/bob_mcp_plus_ansible.html) | MCP consumer guide |
| [`docs/api-reference.html`](docs/api-reference.html) | Full REST API reference (print-to-PDF) |
| [`diagrams/architecture.mmd`](diagrams/architecture.mmd) | System architecture diagram (Mermaid) |
| [`openshift/bobserver.yaml`](openshift/bobserver.yaml) | OpenShift deployment manifest |
| [`.env.example`](.env.example) | All supported environment variables |
| [`scripts/`](scripts/) | Dev tools: `debug_skills.py`, `test_startup.py`, `test_sanitize.py`, `test_mcp_seed.py` |
