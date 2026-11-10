# Deployment guide

## When to use

After the application code works (phases 1-8). Use for containers, NGINX, the two deploy scripts, mode documentation and the production-readiness review.

## Inputs you need

- [deployment.md](../references/deployment-ref.md): SPEC 5.1 (current vs target) and SPEC 10.1-10.4 verbatim.
- [env-vars.md](../references/env-vars.md): the full variable table (compose/script-only variables are in the second table).
- [production-readiness.md](../references/production-readiness.md).
- `BUILD_DECISIONS.md` (G7, G8, G16, G17, G20, G21).

## Requirements covered

| ID | Requirement | Acceptance test |
|---|---|---|
| NFR-07 | The system is single-node by design (SQLite, in-memory SSE bus, in-process queue) | Compose defines exactly one `backend` replica; docs state that scaling out is unsupported; no Postgres/broker service exists. |

## Steps

### 1. Modes (document each separately; SPEC 10.1)

| Mode | `STREAM_MODE` | Where | Entry point |
|---|---|---|---|
| Development | any | Host: `npm run dev` in `backend/` (tsx watch, 8080) and `frontend/` (Vite 5173, `/api` proxy) | README "Local development" |
| Test | n/a | `vitest` in each package | `npm test` |
| Local realtime | `realtime` | Host processes (so Bob and backend share a filesystem); `EXECUTION_STRATEGY=colocated` | `scripts/deploy_local.sh` |
| Containerised demo | `mock` | Compose: `frontend` (NGINX) + `backend` | `scripts/deploy_psh.sh`, `deployment/docker-compose.yml` |
| Production | `realtime` (set explicitly) | Compose + `docker-compose.tls.yml` (HTTPS 8443), `shared-volume`, optional `--profile bob` | compose files |

The default `STREAM_MODE` is `mock` (env.ts and compose; G16). A fresh install shows the demo.

### 2. Containers (SPEC 10.3)

| Service | Build/image | Ports | Volumes | Hardening | Health |
|---|---|---|---|---|---|
| `frontend` | `frontend/Dockerfile` -> `nginxinc/nginx-unprivileged:1.27-alpine` (uid 101), build stage `node:24-bookworm-slim`; `BACKEND_UPSTREAM=http://backend:8080` | `${HTTP_PORT:-8080}:8080` (TLS override adds `${HTTPS_PORT:-8443}:8443`) | tmpfs `/tmp`, `/etc/nginx/conf.d` | read-only, `cap_drop: ALL`, `no-new-privileges` | `wget --spider http://127.0.0.1:8080/nginx-health` |
| `backend` | `backend/Dockerfile`: `node:24-bookworm-slim` multi-stage + `git`, `ca-certificates`, `tini`, optional `${JAVA_PACKAGE}`; uid 1001 | `expose 8080` (not published) | `workbench-data:/data`, `workspaces:/data/workspaces`, `${QSE_CLI_HOST_DIR:-./qse-cli}:/opt/qse-cli:ro` | read-only, tmpfs `/tmp`, `stop_grace_period: 30s`, `cap_drop: ALL`, `no-new-privileges` | `fetch /readyz` |
| `headless-bob` (profile `bob`) | `${HEADLESS_BOB_IMAGE:-headlessbob:latest}` (not built here) | 8000 internal | `headless-bob-data:/data`, `workspaces:/shared/workspaces:${BOB_WORKSPACE_MOUNT_MODE:-ro}`, QSE dir at `/opt/qse-cli:${BOB_QSE_MOUNT_MODE:-ro}` | same | `fetch /healthz` |

Compose project name `qse-workbench`, network `qse-workbench-net`; volumes `qse-workbench-data`, `qse-workbench-workspaces` (fixed name so an external Bob can mount it), `qse-workbench-bob-data`. **No database or broker container.** Docker ignore files: the root one is an allow-list (`*`, `!frontend`, `!deployment/nginx`); the backend one excludes `node_modules`, `dist`, `data`, `tests`, `coverage`, `*.log`, `.env`, `.env.*`, `Dockerfile`, `.dockerignore`.

### 3. NGINX (SPEC 10.4) `deployment/nginx/default.conf.template`, `default.tls.conf.template`

| Location | Behaviour |
|---|---|
| `/nginx-health` | `200 ok` |
| `/healthz`, `/readyz` | proxied to backend |
| `~ ^/api/executions/[^/]+/stream$` | proxy, HTTP/1.1, `proxy_buffering off`, `gzip off`, read/send timeout 3600 s, `X-Accel-Buffering: no` |
| `/api/` | proxy, read timeout 120 s |
| `/assets/` | `expires 1y`, `immutable` |
| `/` | SPA fallback to `/index.html`, `Cache-Control: no-store`, CSP + security headers |
| TLS variant | `:8080` returns 308 to `https://${PUBLIC_HOST}:${PUBLIC_HTTPS_PORT}`; `:8443` terminates TLS 1.2/1.3 with `/etc/nginx/certs/tls.{crt,key}`, adds HSTS (1 year) |

CSP: `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'`; `X-Frame-Options: DENY`; `X-Content-Type-Options: nosniff`; `client_max_body_size 256k`.

### 4. Deploy scripts (SPEC 10.2)

Common rules for both: `#!/usr/bin/env bash`, `set -euo pipefail`, source `scripts/lib/common.sh`, `trap on_exit_hint EXIT`, `--check` runs prerequisites only and changes nothing, `-h|--help` prints the header comment, unknown options `die`. Never print secrets; never accept the QSE licence; idempotent `.env` handling (back up before editing; generate `SECRETS_KEYS` and `ADMIN_PASSWORD` only if missing).

**`scripts/deploy_local.sh` (STREAM_MODE=realtime, host processes, end-to-end).** Options: `--qse-dir DIR`, `--bob-url URL` (default `http://127.0.0.1:8000`), `--workspace DIR` (default `$HOME/qse-workspaces`), `--skip-install`, `--stop`, `--check`, `-h`. Flow: prerequisite and port checks (OS, tools, Node >= 22.13, git, lsof, Java, QSE CLI presence, Bob reachable) -> stop demo containers -> create/repair root `.env` (`STREAM_MODE=realtime`, `EXECUTION_STRATEGY=colocated`, generated secrets) -> `npm ci` + build -> start backend (8080) and Vite UI (5173) with pidfiles in `.run/` -> wait for `/readyz` -> verify the whole chain -> print URLs and the stop command. It never starts or modifies Headless Bob.

**`scripts/deploy_psh.sh` (STREAM_MODE=mock, containers, end-to-end).** Options: `--runtime podman|docker`, `--port N`, `--down`, `--check`, `-h`. Flow: check podman/docker and compose, port 8080 free, network reachability for base images, machine running (podman) -> write `deployment/.env` (generated secrets, `STREAM_MODE=mock`) -> `compose build` -> `compose up -d` -> wait for health -> optionally run a demo execution through the API to completion -> print URLs and `--down`.

**`scripts/lib/common.sh`** exports: `step/ok/note/warn/bad/die`, `have`, `version_ge`, `java_major`, `port_pids`, `stop_pid`, `wait_for_url`, `run_with_timeout`, `run_logged`, `json_get`, `gen_secrets_key`, `gen_password`, `env_get/env_set/env_ensure/env_default`, `check_os`, `check_tool`, `on_exit_hint`.

### 5. Single-node, retention, backup (NFR-07, G7, G8, G21)

- Document: one backend instance only; SQLite file + WAL; queue, SSE bus and rate-limit counters are in memory. Scaling out is unsupported.
- No retention or cleanup of executions, logs, reports or workspaces (G7). Document disk growth and manual cleanup. Backup is manual: stop the service or use SQLite backup tooling, copy the `workbench-data` volume (DB files) and the `workspaces` volume. Schema is created on start with no versioned migration framework beyond `PRAGMA user_version` (G21).
- Metrics, tracing and alerting are **Planned**; do not claim them.

### 6. Documentation consistency (G17, G20)

- Do not mention Postgres, a message broker or HA as available. If the architecture doc mentions Postgres as a future replacement for the `repositories/` layer, label it **Planned**.
- State that Headless Bob's own run timeout defaults to 5 minutes (configured on the Bob side, compose `BOB_RUN_TIMEOUT_MS` for the optional Bob profile) and that large scans need it raised.

### 7. Production readiness review

Walk through [production-readiness.md](../references/production-readiness.md) with the user. Go/no-go: set `STREAM_MODE=realtime` explicitly; supply `SECRETS_KEYS` and a strong `ADMIN_PASSWORD`; serve over TLS so cookies are `Secure`; accept single-node, manual backup and no retention. Record it in `BUILD_DECISIONS.md`.

## Verification (exit gate)

```bash
./scripts/deploy_local.sh --check     # exit 0 on a prepared host, or clear failures
./scripts/deploy_psh.sh   --check
bash -n scripts/deploy_local.sh scripts/deploy_psh.sh scripts/lib/common.sh
docker compose -f deployment/docker-compose.yml config   # or podman compose
```

- Build both images; start the demo with `deploy_psh.sh`; `GET /readyz` returns 200 with `database`, `workspace`, `accepting`; a mock execution completes through the UI; `--down` removes containers.
- NFR-07 statement: compose has one `backend` service and no DB/broker service; docs say single-node.
- Confirm no secret appears in script output (grep the run log for the generated password).
- Confirm the SSE location in NGINX is present (stream stays open past 60 s).

## Pitfalls

- Running real analysis in containers without sharing the workspace and QSE volumes with Bob (`qse_not_reachable`, `repo_not_reachable`).
- NGINX buffering the SSE stream.
- Publishing the backend port.
- Overwriting an existing `.env` instead of backing it up.
- Presenting the compose demo as a production deployment.

## Known gaps that apply

- G7: no retention/cleanup. User decision: <fix | keep as built>
- G8: SQLite single node, in-memory state. User decision: <fix | keep as built>
- G16: `STREAM_MODE` defaults to `mock` in compose. User decision: <fix | keep as built>
- G17: docs mention Postgres that does not exist. User decision: <fix | keep as built>
- G20: Headless Bob run timeout default 5 minutes. User decision: <fix | keep as built>
- G21: no metrics/tracing/alerts, automated backup or versioned migrations. User decision: <fix | keep as built>

## SPEC references

SPEC 5.1, SPEC 5.4, SPEC 8.1 (transport, container hardening), SPEC 10.1, SPEC 10.2, SPEC 10.3, SPEC 10.4, SPEC 10.5, SPEC 12.1, SPEC 12.2, SPEC 12.3. Detail: [deployment.md](../references/deployment-ref.md).
