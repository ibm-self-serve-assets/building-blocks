# Deployment and infrastructure

> Extracted verbatim from `SPEC.md` (sections 10.1-10.4 and 5.1). Do not edit here; edit SPEC.md and re-extract. Paths are relative to the project root.

### 5.1 Current implementation vs target production architecture

| Aspect | Current implementation (as built) | Target production architecture (**Planned**, not built) |
|---|---|---|
| Processes | One Node process (Express) + NGINX for static files and reverse proxy | Same, behind an ingress / load balancer |
| Persistence | Embedded SQLite file, single writer, WAL | Managed database (docs mention Postgres as a replacement for the `repositories/` layer only) |
| Scaling | Single node. Queue, SSE bus and rate-limit counters are in process memory | Shared queue and pub/sub; sticky or shared state |
| Identity | Local users, scrypt, one bootstrap admin | SSO/OIDC, user management, MFA |
| Headless Bob | External service, optional compose profile `bob` using an image not built here | Managed Bob service |
| Execution isolation | Workspace and QSE CLI shared by volume or by co-location (`EXECUTION_STRATEGY`) | Per-run ephemeral workspaces |
| Data lifecycle | No retention or deletion of executions, logs or reports | Retention policy and purge job |
| Observability | pino JSON logs, `x-request-id`, `/healthz`, `/readyz` | Metrics, tracing, alerting |
| Secrets | `SECRETS_KEYS` env var, AES-256-GCM key ring | KMS / vault |

Anything in the right column must not be assumed to exist.

## 10. Deployment and infrastructure

### 10.1 Modes

| Mode | `STREAM_MODE` | Where it runs | Entry point | Purpose |
|---|---|---|---|---|
| Development | any | Host: `npm run dev` in `backend/` (tsx watch, port 8080) and `frontend/` (Vite, port 5173, `/api` proxy) | `README.md` "Local development" | Coding |
| Test | n/a | `vitest` in each package | `npm test` | Automated tests (see 11) |
| Local realtime | `realtime` | **Host process** (not containers) so Bob and the backend see the same filesystem; `EXECUTION_STRATEGY=colocated` | `scripts/deploy_local.sh` | Real end-to-end analysis next to a local Headless Bob and QSE CLI |
| Containerised demo | `mock` | Podman or Docker Compose: `frontend` (NGINX) + `backend` | `scripts/deploy_psh.sh`, `deployment/docker-compose.yml` | Demonstration with a recorded run |
| Production | `realtime` (set explicitly) | Compose with `docker-compose.tls.yml` (HTTPS on 8443) and `shared-volume`, optional `--profile bob` | `deployment/docker-compose.yml` + `docker-compose.tls.yml` | Containerised realtime; requires Bob to share the two volumes |

Note: the **default** `STREAM_MODE` is `mock` (both in `env.ts` and in `docker-compose.yml`). A fresh install shows the demo until the variable is changed. The README states real analysis is intended to run on the user's machine (Setup A) and containers are the demo only.

### 10.2 Deployment scripts (`scripts/`)

| Script | Mode | Behaviour |
|---|---|---|
| `scripts/deploy_local.sh` | `STREAM_MODE=realtime`, host processes | Prereq and port checks (OS, tools, Node ≥ 22.13, git, lsof, Java), creates/updates the root `.env` idempotently (backs it up, generates `SECRETS_KEYS` and `ADMIN_PASSWORD` if missing, sets `EXECUTION_STRATEGY=colocated`), installs dependencies, builds, starts backend (8080) and Vite UI (5173) with pidfiles in `.run/`, waits for `/readyz`, prints URLs. Has `--check` (prereqs only) and stop options. |
| `scripts/deploy_psh.sh` | `STREAM_MODE=mock`, containers | Checks podman/docker and compose, port 8080, writes `deployment/.env` (generated secrets, `STREAM_MODE=mock`), builds and starts compose, waits for health. Has `--check` and down options. |
| `scripts/lib/common.sh` | shared | `step/ok/note/warn/bad/die`, `have`, `version_ge`, `java_major`, `port_pids`, `stop_pid`, `wait_for_url`, `run_with_timeout`, `run_logged`, `json_get`, `gen_secrets_key`, `gen_password`, `env_get/env_set/env_ensure/env_default`, `check_os`, `check_tool`, `on_exit_hint` |

Both scripts pass `--check` on the author's macOS arm64 host (podman 6.0.0, Node 26.4.0).

### 10.3 Containers

| Service | Image / build | Ports | Volumes | Hardening | Health check |
|---|---|---|---|---|---|
| `frontend` | `frontend/Dockerfile` → `nginxinc/nginx-unprivileged:1.27-alpine`; `BACKEND_UPSTREAM=http://backend:8080` | `${HTTP_PORT:-8080}:8080` (TLS override adds `${HTTPS_PORT:-8443}:8443`) | tmpfs `/tmp`, `/etc/nginx/conf.d` | read-only, `cap_drop: ALL`, `no-new-privileges` | `wget --spider http://127.0.0.1:8080/nginx-health` |
| `backend` | `backend/Dockerfile` (`node:24-bookworm-slim` + `git`, `tini`, optional `JAVA_PACKAGE`) | `expose 8080` (not published) | `workbench-data:/data`, `workspaces:/data/workspaces`, `${QSE_CLI_HOST_DIR:-./qse-cli}:/opt/qse-cli:ro` | read-only, tmpfs `/tmp`, `stop_grace_period: 30s` | `fetch /readyz` |
| `headless-bob` (profile `bob`) | `${HEADLESS_BOB_IMAGE:-headlessbob:latest}` (not built here) | 8000 internal | `headless-bob-data:/data`, `workspaces:/shared/workspaces:${BOB_WORKSPACE_MOUNT_MODE:-ro}`, QSE dir at `/opt/qse-cli:${BOB_QSE_MOUNT_MODE:-ro}` | same hardening | `fetch /healthz` |

Network `qse-workbench-net`. Volumes: `qse-workbench-data`, `qse-workbench-workspaces` (fixed name so an external Bob can mount it), `qse-workbench-bob-data`. **There is no database or message-broker container**; the compose file defines no Postgres.

### 10.4 NGINX behaviour

| Location | Behaviour |
|---|---|
| `/nginx-health` | `200 ok` |
| `/healthz`, `/readyz` | Proxied to the backend |
| `~ ^/api/executions/[^/]+/stream$` | Proxy, HTTP/1.1, `proxy_buffering off`, `gzip off`, read/send timeout 3600 s, `X-Accel-Buffering: no` |
| `/api/` | Proxy, read timeout 120 s |
| `/assets/` | `expires 1y`, `immutable` |
| `/` | SPA fallback to `/index.html`, `Cache-Control: no-store`, CSP and security headers |
| TLS variant | `:8080` returns 308 to `https://${PUBLIC_HOST}:${PUBLIC_HTTPS_PORT}`; `:8443` terminates TLS 1.2/1.3 with `/etc/nginx/certs/tls.{crt,key}` and adds HSTS |
