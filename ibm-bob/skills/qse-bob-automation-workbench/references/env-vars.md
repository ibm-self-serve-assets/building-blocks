# Environment variables

> Extracted verbatim from `SPEC.md` (section 10.5). Do not edit here; edit SPEC.md and re-extract.

## Environment variables

Source of truth: `backend/src/config/env.ts` plus `.env.example` and `deployment/docker-compose.yml`. "Sensitive" = must never be logged or committed.

### Backend runtime

| Variable | Purpose | Required | Default | Sensitive |
|---|---|---|---|---|
| `NODE_ENV` | Mode; `production` forces secure cookies | No | `development` | No |
| `HOST` | Bind address | No | `0.0.0.0` | No |
| `PORT` | Listen port | No | `8080` | No |
| `LOG_LEVEL` | pino level | No | `info` | No |
| `DATA_DIR` | Data root | No | `./data` | No |
| `WORKSPACE_ROOT` | Where repositories are cloned | No | derived from `DATA_DIR` (`workspaces`) | No |
| `DATABASE_PATH` | SQLite file | No | `<DATA_DIR>/db/workbench.sqlite` (realtime) or `workbench-demo.sqlite` (mock) | No |
| `STREAM_MODE` | `mock` or `realtime` | No | `mock` | No |
| `DEMO_DATA_DIR` | Location of `recorded-run.json` and the demo workspace | No | `demo-data` in the backend | No |
| `DEMO_STEP_DELAY_MS` | Replay pacing per step | No | `700` | No |
| `DEMO_BOB_WAIT_MS` | Replay duration for the Bob phase | No | `6000` | No |
| `DEMO_REPLAY_SPEED` | Event replay speed multiplier | No | `4` | No |
| `SECRETS_KEYS` | AES-256-GCM key ring `kid:base64(32 bytes)[,…]` | **Yes** | none | **Yes** |
| `ADMIN_USERNAME` | Bootstrap admin | No | `admin` | No |
| `ADMIN_PASSWORD` | Bootstrap admin password, at least 12 characters | **Yes** | none | **Yes** |
| `SESSION_TTL_MINUTES` | Absolute session lifetime | No | `480` | No |
| `SESSION_IDLE_MINUTES` | Idle timeout | No | `60` | No |
| `COOKIE_SECURE` | `Secure` cookie flag | No | `false` (forced `true` in production) | No |
| `TRUST_PROXY` | Reverse-proxy hop count | No | `1` | No |
| `CORS_ALLOWED_ORIGINS` | Comma-separated origins | No | empty | No |
| `TLS_KEY_FILE` / `TLS_CERT_FILE` | Serve HTTPS from Node (both needed) | No | unset | Path only |
| `BOB_ALLOWED_HOSTS` | Host allow-list for Bob | No | empty (any that pass SSRF checks) | No |
| `BOB_ALLOW_PRIVATE_NETWORK` | Permit private/loopback targets | No | `false` (compose default `true`) | No |
| `BOB_REQUEST_TIMEOUT_MS` | Bob HTTP timeout | No | `15000` | No |
| `GITHUB_ALLOWED_HOSTS` | Allowed Git hosts | No | `github.com` | No |
| `GIT_BIN` | git executable | No | `git` | No |
| `CLONE_TIMEOUT_MS` | Clone/ls-remote timeout | No | `600000` | No |
| `QSE_CLI_PATH` | Explicit CLI path for discovery | No | empty | No |
| `QSE_CLI_SEARCH_DIRS` | Discovery directories | No | `/opt/qse-cli,/usr/local/bin/qse-cli-artifacts` | No |
| `QSE_CLI_ALLOWED_DIRS` | Directories a CLI may live in | No | `/opt,/usr/local/bin,/usr/bin` | No |
| `QSE_CLI_EXECUTABLE_NAMES` | Allowed basenames | No | `qse-cli,cli.sh` | No |
| `QSE_CLI_VERSION_ARGS` | Version command arguments | No | `-v` | No |
| `QSE_VALIDATION_TIMEOUT_MS` | Version command timeout | No | `30000` | No |
| `QSE_USAGE_HINT` | Extra hint text in validation messages | No | unset | No |
| `EXECUTION_STRATEGY` | `shared-volume` or `colocated` | No | `shared-volume` | No |
| `QSE_MOUNT_DIR` | CLI mount inside the backend | No | `/opt/qse-cli` | No |
| `BOB_QSE_MOUNT_DIR` | CLI mount inside Bob | No | `/opt/qse-cli` | No |
| `BOB_WORKSPACE_MOUNT_DIR` | Workspace mount inside Bob | No | `/shared/workspaces` | No |
| `EXECUTION_TIMEOUT_MS` | Per-run timeout | No | `1800000` | No |
| `MAX_CONCURRENT_EXECUTIONS` | Parallel runs (max 16) | No | `1` | No |
| `MAX_PROMPT_CHARS` | Prompt cap (max 15000) | No | `8000` | No |
| `MAX_ARTIFACT_BYTES` | Max size per artifact | No | `26214400` (25 MiB) | No |
| `MAX_ARTIFACTS` | Max artifacts per run | No | `200` | No |
| `RATE_LIMIT_WINDOW_MS` | API limiter window | No | `60000` | No |
| `RATE_LIMIT_MAX` | API requests per window | No | `300` | No |
| `LOGIN_RATE_LIMIT_MAX` | Login attempts per 15 min | No | `10` | No |

### Compose / script-only variables

| Variable | Purpose | Required | Default | Sensitive |
|---|---|---|---|---|
| `HTTP_PORT` | Published NGINX HTTP port | No | `8080` | No |
| `HTTPS_PORT` | Published NGINX HTTPS port (TLS override) | No | `8443` | No |
| `PUBLIC_HOST` | Host in the HTTP→HTTPS redirect | No | `localhost` | No |
| `BACKEND_UPSTREAM` | NGINX upstream | No | `http://backend:8080` | No |
| `QSE_CLI_HOST_DIR` | Host directory bind-mounted at `/opt/qse-cli` | No | `./qse-cli` | No |
| `BACKEND_JAVA_PACKAGE` | Build arg `JAVA_PACKAGE` for the backend image | No | empty | No |
| `HEADLESS_BOB_IMAGE` | Image for the `bob` profile | No | `headlessbob:latest` | No |
| `BOB_API_KEY` | Bob Shell key inside the Bob container | No | empty | **Yes** |
| `AUTH_TOKENS` | Service tokens Bob accepts (JSON) | No | empty | **Yes** |
| `BOB_RUN_TIMEOUT_MS` | Bob's own run timeout | No | `1800000` | No |
| `BOB_WORKSPACE_MOUNT_MODE` / `BOB_QSE_MOUNT_MODE` | `ro` or `rw` mounts inside Bob | No | `ro` | No |
| `VITE_API_PROXY` | Dev proxy target for the Vite server | No | `http://127.0.0.1:8080` | No |

The Bob address and API key are **not** environment variables: they are entered in the UI and stored encrypted.
