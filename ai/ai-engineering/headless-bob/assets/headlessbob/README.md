# headlessbob

A standalone TypeScript service that runs **Bob Shell 2.0.1** and implements the text subset of **Agent Communication Protocol (ACP) 0.2.0** over HTTP. Bob is the execution engine; no VS Code, Codex runtime, or OpenAI account is involved.

## Test UI and thread-based REST API

Open your deployment URL, or `http://127.0.0.1:8000` when running locally. The root page now serves a simple conversation UI. Connect with the **service token** (the `owner` value inside `AUTH_TOKENS` in `.env`), not the Bob API key. The token stays only in the page's memory; reload or Disconnect clears it. The UI and API share the same origin and require no separate frontend service.

- A **thread** is a saved conversation linked to one Bob session and workspace.
- A **message** is the task or follow-up you send to that thread.
- A **run** is one execution of Bob for that message, including status, streamed output, and cancellation.

The UI supports creating, searching, renaming, archiving/restoring, and deleting threads; sending follow-ups; live text; stopping a run; copying messages; and inspecting run JSON. History is paginated and persists across restarts. Only one run may be active per thread. Failed or cancelled sessions can require a new thread rather than silently losing Bob's context.

**Archive** is reversible. **Delete** requires confirmation in the UI and removes the thread plus wrapper message records permanently. The service's ACP run audit records, Bob's internal task history, and workspace files are retained separately. Deletion is rejected while the thread has an active run; it is not a filesystem wipe.

| REST endpoint | Purpose |
| --- | --- |
| `GET /api/v1/capabilities` | Caller, readiness, features, and limits |
| `POST /api/v1/threads` | Create with `{}` or `{"title":"My project"}` |
| `GET /api/v1/threads` | List/search; `q`, `archived`, `limit`, `cursor` |
| `GET /api/v1/threads/{id}` | Thread metadata and status |
| `PATCH /api/v1/threads/{id}` | Set `title` and/or `archived` |
| `DELETE /api/v1/threads/{id}` | Delete wrapper conversation; returns 204 |
| `POST /api/v1/threads/{id}/messages` | Send `{"content":"Your task"}`; returns 202 with run and events URL |
| `GET /api/v1/threads/{id}/messages` | Read messages; `limit` counts turns, `before` loads older turns |
| `GET /api/v1/runs/{id}` | Status/result |
| `GET /api/v1/runs/{id}/events` | SSE stream with replay |
| `POST /api/v1/runs/{id}/cancel` | Request cancellation |

All REST calls use `Authorization: Bearer TOKEN`. Errors use `{"error":{"code":"thread_busy","message":"..."}}`. Send an `Idempotency-Key` header when posting a message: retries with the same content return the original run; changing the content with that key returns 409. Event streams use per-run integer SSE IDs; reconnect with `Last-Event-ID` or `?after=` to avoid replaying already-received events. Disconnecting the UI or stream does not cancel a run.

The full OpenAPI contract is served at `/api/openapi.json`. Threads wrap the existing runtime directly; the ACP endpoints below remain available unchanged. The wrapper does not make HTTP calls to the ACP routes: both interfaces share the same run manager, scheduler, persistence, and Bob subprocess adapter. Node.js/TypeScript was retained for reuse and streaming support; no performance advantage over Python/FastAPI has been benchmarked. Older ACP-only runs are not automatically converted into threads because their original input messages were not stored by the earlier service.

## Run locally

Requires macOS/Linux, Node.js 22.22 or newer, Bob Shell 2.0.1, a Bob API key, and an accepted Bob license. Run `bob --show-license` to review the license and use Bob's interactive setup to accept it if needed.

```sh
npm ci
cp .env.example .env  # only for a new checkout; preserve an existing .env
# Set BOB_API_KEY in .env. Configure AUTH_TOKENS if sharing access.
npm run build
npm start
```

The default address is `http://127.0.0.1:8000`. `.env` is loaded by `start`, `dev`, and `smoke`. Store local credentials in `.env`, which is excluded from Git and Docker. Do not place keys in source files or request bodies.

```sh
npm run check  # TypeScript build and fixture/HTTP/contract/recovery tests
npm run smoke # real Bob: creates a file, continues the task, cancels a running tool
```

The live smoke test spends a small amount of Bob credit, uses temporary workspaces, and removes those workspaces afterwards. Bob's own task records remain in its task database.

## API

Set `BASE` to the local address or your HTTPS route. If authentication is configured, set `TOKEN` to the appropriate value from `AUTH_TOKENS` in `.env`.

Set `HEADLESSBOB_URL` to your service URL (default: `http://127.0.0.1:8000`). The included client loads the token from `.env` automatically:

```sh
npm run client -- /agents
npm run client -- /runs examples/run.json
```

```sh
BASE=http://127.0.0.1:8000
curl -H "Authorization: Bearer $TOKEN" "$BASE/agents"

curl -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/runs" -d '{
    "agent_name":"headlessbob",
    "input":[{"role":"user","parts":[{"content_type":"text/plain","content":"Create hello.txt containing hello."}]}],
    "mode":"sync"
  }'
```

`sync` (the default) waits for a terminal run. `async` returns HTTP 202 immediately. `stream` returns HTTP 200 with ACP JSON events in SSE `data:` records; use `curl -N`. Streaming text excludes Bob reasoning and raw tool payloads. Disconnecting any response does not cancel the run. Slow streaming consumers are disconnected once their pending output exceeds 256 KiB; persisted events can be fetched afterwards.

The returned `session_id` identifies a service-assigned workspace. Pass it in a later `POST /runs` to continue the same Bob task. The service binds sessions to the authenticated caller and configured Bob mode. Never send Bob task IDs or server filesystem paths. Failed or interrupted executions invalidate continuation; omit `session_id` to start a fresh workspace.

| Endpoint | Behavior |
| --- | --- |
| `GET /ping`, `GET /healthz` | Public liveness |
| `GET /readyz` | Authenticated Bob executable/version/key readiness |
| `GET /agents`, `GET /agents/headlessbob` | Discovery and manifest |
| `POST /runs` | Create sync, async, or stream run |
| `GET /runs/{run_id}` | Current run, result, or explicit failure |
| `POST /runs/{run_id}/cancel` | Request cancellation, returns HTTP 202 |
| `GET /runs/{run_id}/events` | Persisted ACP events in order |
| `GET /session/{session_id}` | Session ID and run history as UUID URNs |

ACP Await/resume (`POST /runs/{run_id}`), imported session state/history, non-text media, URL inputs, artifact transfer, and A2A are not implemented. Unsupported inputs return ACP error envelopes. The source schema is pinned in [spec/PROVENANCE.md](spec/PROVENANCE.md); [the upstream ACP specification](https://github.com/i-am-bee/acp/blob/main/docs/spec/openapi.yaml) defines the wire contract. A2A remains a later adapter, as a possible future adapter.

## Limits, persistence, and trust

SQLite stores run metadata, session ownership, task mappings, and ordered events in `DATA_DIR`. Workspaces are UUID directories under `DATA_DIR/workspaces`. Bob's separate history database lives under `$HOME/.bob`; persist **both** locations. An exclusive SQLite lock permits one service process per data directory and releases automatically on process death. Unfinished runs become failed/interrupted on restart and are never replayed automatically.

The scheduler serializes each session/workspace and bounds total execution and queue capacity. Defaults: 2 concurrent runs, 100 queued, 5-minute timeout, 20 turns, $1 Bob cost limit, 2 MiB each of stdout/stderr, 10,000 events, and a 64 KiB request body. Bob enforces cost/turn limits; the service enforces timeout/output/event limits. `KILL_GRACE_MS` defaults to 2 seconds, followed by process-group SIGKILL. Public errors omit raw stderr to avoid exposing credentials.

Use this service with trusted operators. Bob can execute shell commands; assigned workspaces and ownership checks are **not an OS sandbox**. Different API tokens prevent cross-caller API access, but do not isolate mutually untrusted code within the same worker. The OpenShift deployment runs a single trusted owner in a dedicated non-root pod with no Kubernetes service-account token or RBAC permissions. Untrusted multi-user service requires separate worker containers and stronger filesystem/network isolation.

Only `PATH`, `HOME`, `TMPDIR`, locale, `BOB_API_KEY`, proxy settings, and `NODE_EXTRA_CA_CERTS` are inherited by Bob; the service bearer tokens are omitted from the child environment. MCP and Bob subagents are disabled. ACP endpoints reject browser-origin requests. The REST wrapper accepts same-origin browser requests and rejects cross-origin calls; no permissive CORS support is exposed. Non-loopback binding requires `AUTH_TOKENS` and `ALLOW_TRUSTED_NETWORK=true`.

Run readiness checks verify the key is present and the binary reports version 2.0.1; they do not make a billable API call or guarantee that a key is valid/unexpired. Completed runs/events are retained without automatic pruning. Monitor disk usage and back up the whole persistent volume while the service is stopped. Do not scale the SQLite deployment above one replica.

## OpenShift (`binb`)

The supplied manifests use unique `headlessbob` resource names, a 10 GiB block PVC, a Recreate deployment, one concurrent Bob execution, a TLS edge route, and an ingress policy allowing the OpenShift router. The Docker build uses your licensed Bob tarball at `vendor/bobshell-2.0.1.tgz`; it is not distributed in Git. The image includes `tini` to reap orphaned subprocesses.

```sh
# Log into your cluster with oc, then:
oc apply -n binb -f openshift/build.yaml
tar -czf /tmp/headlessbob-build.tgz Dockerfile package.json package-lock.json \
  tsconfig.json src browser spec public scripts/container-entrypoint.sh vendor/bobshell-2.0.1.tgz
oc start-build headlessbob -n binb --from-archive=/tmp/headlessbob-build.tgz --follow

# Import only .env credentials and the already-accepted local Bob license flag.
node --env-file=.env scripts/configure-cluster.mjs
oc apply -n binb -f openshift/app.yaml
oc rollout status deployment/headlessbob -n binb
oc get route headlessbob -n binb
```

The archive allowlist excludes `.env`, API-key JSON files, personal Bob history, and unrelated workspace files. The Secret contains the Bob key and service tokens. The ConfigMap contains only the existing `licenseConsent` flag. Mounting the PVC at `/data` preserves service data and Bob's home directory across pod replacement.

For subsequent builds, update the deployment to the resulting immutable image digest (preferred), or use `oc rollout restart deployment/headlessbob -n binb` after rebuilding the mutable tag. Restarting cancels active work; check run status first. Adjust the namespace/image registry path and storage class before using these manifests on another cluster.

## Markdown and workspace downloads

Assistant messages render sanitized Markdown headings, lists, tables, links and code blocks. Relative file links download from that thread's workspace using the current service token. Workspace files appear in a right-hand panel on desktop (below the chat on small screens). Use **Files** to focus the panel and browse folders or download files; downloaded HTML can be opened locally. Generated HTML is never executed inside the service UI.

Authenticated REST endpoints:
- `GET /api/v1/threads/{id}/files?path=folder` lists the current workspace (omit path for root).
- `GET /api/v1/threads/{id}/files/download?path=tetris.html` returns a binary attachment.

Both use `Authorization: Bearer <service-token>`. Downloads are limited to 25 MiB each and eight concurrent transfers; listings return at most 500 entries and inspect at most 2,000. Files are available once active execution ends. Hidden files, traversal paths, symlinks and hard links are excluded. These are current workspace files, not immutable run snapshots. Archived threads retain access; deleted threads lose these API routes while underlying files remain retained.

**Cancel run** stays visible beside Send message. It is enabled for queued or running tasks, shows Cancelling while a stop is pending, and is disabled when there is no active run.

## Usage statistics

New completed responses show a Usage section with Bob-reported duration, session cost and tool calls. Input/output/total and cache token counts appear when Bob supplies them. Bob Shell 2.0.1 gates token reporting behind its developer mode, so unavailable token metrics are omitted from the UI. The wrapper does not enable developer mode or estimate missing token counts. Session cost is preserved as reported, without treating it as a per-message charge or assuming a currency.

`GET /api/v1/runs/{id}` returns an optional `usage` object, also included on assistant messages from `GET /api/v1/threads/{id}/messages` and in the completed run SSE event. ACP run responses expose the same additive field. Fields: `duration_ms`, `session_costs`, `max_cost`, `tool_calls`, `input_tokens`, `output_tokens`, `total_tokens`, `cache_read_tokens`, `cache_write_tokens`, `cache_ratio`. Only finite nonnegative reported values are preserved; counts must be integers. Missing values are omitted. Usage is persisted with runs and survives restart. Old runs and runs that do not emit a successful final result have no recorded usage; the UI says so explicitly.
