# Feature specs 4.1-4.3 and outbound interfaces 6.4-6.7

> Extracted verbatim from `SPEC.md` (sections 4.1, 4.2, 4.3, 6.4-6.7). Do not edit here; edit SPEC.md and re-extract. Paths are relative to the project root.

### 4.1 Bob connection

| Item | Detail |
|---|---|
| Overview | Store the address and API key of a Headless Bob service (encrypted) and test it. The browser never calls Bob; the backend does. |
| Journey | `/bob` → enter address and key → **Save configuration** → **Test connection** → capabilities appear → `Connected`. |
| Preconditions | Session; role operator or admin for connect/test/disconnect. Realtime only for real calls. |
| Inputs and validation | `bobConnectSchema`: `endpoint` ≤ 300; `adapter` `rest-threads`\|`acp`; `apiBasePath` default `/api/v1` (must look like `/api/v1`, else `invalid_base_path`); `authMode` `bearer`\|`header`\|`none`; `authHeaderName` default `authorization` (token chars only, else `invalid_header_name`); `apiKey` ≤ 512, 8–512 chars, no whitespace (else `invalid_api_key`). Endpoint SSRF rules in [8](#8-security). A key is required for a new or changed endpoint (`api_key_required`); if the endpoint is unchanged and no key is sent, the stored key is kept. |
| Processing | `save()` normalises and validates, seals the key with AES-256-GCM, stores a hint `••••<last4>`, persists the row with state `connecting`, and then **immediately calls `test()`**, so "Save configuration" also performs a connection test (the toast text "Run Test Connection to verify" understates this). `test()` sets `connecting`, builds an adapter, runs the adapter's connection test, stores state, message and capabilities. State mapping: success → `connected`; HTTP 401/403 → `auth_failed`; 404 (wrong base path) or any other failure → `connection_failed`. `rest-threads` probes `GET /healthz` (no auth, no base path) then `GET {base}/capabilities`. `acp` probes `/ping`, `/agents` (needs agent `headlessbob`) and `/readyz`. `disconnect()` deletes the row (and so the key). |
| API | `GET /api/bob/status`, `POST /api/bob/connect`, `POST /api/bob/test-connection`, `POST /api/bob/disconnect` |
| Persistence | `bob_connection` (single row `id=1`), `api_key_enc`, `api_key_hint`, `capabilities` JSON |
| Success | `BobConnection` JSON (never contains the key). |
| Failure | `invalid_endpoint`, `endpoint_not_allowed`, `invalid_base_path`, `invalid_header_name`, `invalid_api_key`, `api_key_required`, `secret_unreadable`, `bob_not_configured` (409), 409 `execution_active` on disconnect during a run, network errors mapped to readable messages (connection refused, host not found, timeout, TLS). |
| UI transitions | not_configured → (save, which also tests) connecting → connected \| auth_failed \| connection_failed; **Test connection** repeats the last step. |
| Security | SSRF guard at save and at connect time (DNS-level); redirects are not followed; response size caps (JSON 4 MiB). Key never returned, logged or placed in a URL. |
| Mock behaviour | Endpoint is the constant `demo://recorded-run`; the state is always `connected`; the key is never stored; recorded capabilities are returned; save/test/disconnect do not touch the network. UI shows "Demo —" in the header and a DEMO-specific toast. |
| Tests | `security.test.ts` (Bob connection suite, 11 tests); `demo.test.ts`; `pages.test.tsx` BobConnectionPage (4 tests) |
| Status | Implemented (realtime); Mocked (mock). `acp` supports no file retrieval, so report source falls back to the final answer (**Partial** for that adapter). |

### 4.2 GitHub repository management

| Item | Detail |
|---|---|
| Overview | Validate reachability of a repository and branch, then shallow-clone it into an isolated workspace directory. |
| Journey | `/repository` → URL + branch (+ optional token) → **Validate** (optional) → **Clone** → progress lines → `Cloned` with commit and file count. |
| Preconditions | Session; operator role for validate. Realtime needs `git` on the backend host. |
| Inputs and validation | `repoInput`: `url` ≤ 300, `branch` default `main` (≤ 200), `token` ≤ 255 (8–255 chars, no whitespace else `invalid_token`). URL: `https` only; no credentials, query, hash or port; host in `GITHUB_ALLOWED_HOSTS`; exactly `owner/repo`; owner/name and branch regex checked (`invalid_repository_url`, `repository_host_not_allowed`, `invalid_branch`). |
| Processing | **Validate:** `git ls-remote --exit-code --heads <url> <branch>`; returns owner, name, branch and head commit. **Clone** (202, background): status `cloning` → `git clone --depth 1 --single-branch --no-tags --progress --branch <b>` into `<dir>.new` under `WORKSPACE_ROOT/repo-<hex>/`, then rename to `repo`; validates the tree (removes symlinks that escape, counts files; cap 250 000), removes the remote `origin`, reads HEAD commit; status `cloned`. Token is passed through `GIT_CONFIG_*` `http.extraHeader` as Basic `x-access-token:<token>`, never in argv or URL. `GIT_ALLOW_PROTOCOL=https`, hooks disabled, empty `credential.helper`. Progress keeps the last 30 lines with paths scrubbed. **Re-clone:** same, optionally new branch/token. **Remove:** deletes the work dir and row. |
| API | `GET /api/repositories`, `POST /api/repositories/validate`, `POST /api/repositories/clone` (202), `GET /api/repositories/:id`, `POST /api/repositories/:id/reclone` (202), `DELETE /api/repositories/:id` (204) |
| Persistence | `repositories` (`token_enc`, generated `dir_name`, `status`, `commit_sha`, `file_count`); files under `WORKSPACE_ROOT` |
| Success | `Repository` JSON; `hasToken` boolean only; `workspaceLabel` is a non-path label. |
| Failure | `branch_not_found`, `repository_unreachable`, `git_timeout` (504), `clone_failed`, `clone_cancelled`, `repository_too_large`, `git_unavailable` (500), `workspace_invalid`, 409 conflicts (clone already running; repo in use by an execution). On restart, repos left in `cloning`/`validating` are marked `failed`. |
| UI transitions | pending → validating → validated → cloning → cloned \| failed. |
| Security | Repository content is treated as untrusted data: never executed; the prompt tells Bob to treat it as data. Paths validated with `isInside`/`realpathInside`. Clone errors are redacted. |
| Mock behaviour | No git call; the recorded repository (`SunilManika/crypto-inventory-demo@main`, commit `bcc625a1…`, 55 files) is reported as cloned regardless of the URL entered. |
| Tests | `security.test.ts` (GitHub suite, 5 tests), `tests/unit/github.test.ts` (3 tests incl. `it.each`), `workflow.test.ts` (symlink clone) |
| Status | Implemented (realtime); Mocked (mock). The list is global (not per user). |

### 4.3 QSE CLI discovery and validation

| Item | Detail |
|---|---|
| Overview | Locate the QSE CLI executable, prove it runs, and ensure Headless Bob can reach the same path. |
| Journey | `/qse` → **Run discovery** → pick a candidate (or enter an absolute path) → **Use selected and validate** → `Valid` with version. |
| Preconditions | Session; operator role for configure/validate/discover. |
| Inputs and validation | `qseConfigureSchema`: `mode` `auto`\|`manual`; `path` ≤ 1024; `versionArgs` ≤ 4 items, each ≤ 40 chars and matching `^[A-Za-z0-9._=-]{1,40}$` (`invalid_version_args`). Manual path must be absolute (`invalid_qse_path`). |
| Processing | **Discover** (never executes anything): candidates from `QSE_CLI_PATH`, then `PATH`, then `QSE_CLI_SEARCH_DIRS`. A candidate is `allowed` when its real path lies inside `QSE_CLI_ALLOWED_DIRS` **and** its basename is in `QSE_CLI_EXECUTABLE_NAMES`; `executable` from file mode. **Configure:** `auto` requires the chosen path to be a candidate that is `allowed && executable` (`not_a_candidate`; none → `qse_not_found`); `manual` requires `path` (`path_required`). Then validates. **Validate:** runs the CLI directly (no shell) with `QSE_CLI_VERSION_ARGS` (default `-v`), cwd = the CLI directory, `minimalEnv()` plus the real `HOME` (the CLI keeps licence state in `$HOME/qs-explorer`), timeout `QSE_VALIDATION_TIMEOUT_MS`. Output containing "license agreement has not been accepted" yields `invalid` even with exit code 0; the workbench never accepts the licence. `extractVersion` prefers a line like `version: <digits>`, else the first non-empty line. Result view adds `bobVisiblePath` (via `PathMapper`), `reachableFromBob`, `strategy`. |
| API | `GET /api/qse/discover`, `POST /api/qse/configure`, `POST /api/qse/validate`, `GET /api/qse/status` |
| Persistence | `qse_config` (single row) |
| Success | `QseConfig` with `status: 'valid'`, `version`, `validatedAt`. |
| Failure | `status: 'invalid'` with a `message`; `qse_not_configured` (409) when validating with no path; symlink escaping the allowed dir is refused. |
| UI transitions | not_configured → discovered → (validate) valid \| invalid. A `valid` CLI outside the shared mounts shows the "Not reachable from Headless Bob" warning and blocks execution. |
| Security | Directory + basename allow-listing, `realpath` checks, shell-free exec, output cap 1 MiB, timeout then SIGKILL after 2 s. |
| Mock behaviour | Recorded values: path `/usr/local/bin/qse-cli-artifacts/cli.sh`, version `App Version : 2.3.1.0 Build Version : 202605.00095`. |
| Tests | `security.test.ts` (QSE suite, 6 tests), `tests/unit/qse-validator.test.ts` (6 tests) |
| Status | Implemented (realtime); Mocked (mock). The 4 version args are not editable in the UI (only via API/`QSE_CLI_VERSION_ARGS`). |

### 6.4 Headless Bob interfaces (outbound, adapter `rest-threads`)

All calls go through the SSRF-guarded undici client (`maxRedirections: 0`, JSON limit 4 MiB, SSE buffer limit 8 MiB). Auth: `bearer` → `Authorization: Bearer <key>`; `header` → `<authHeaderName>: <key>`; `none` → no header.

| Purpose | Request | Notes |
|---|---|---|
| Liveness | `GET /healthz` (origin root, no base path, no auth) | |
| Capabilities | `GET {base}/capabilities` | 401/403 → `auth_failed` |
| Create thread | `POST {base}/threads` body `{ "title": "…" }` | |
| Send prompt | `POST {base}/threads/{threadId}/messages` body `{ "content": "<built prompt>" }`, header `idempotency-key` | Returns a run id |
| Events | `GET {base}/runs/{runId}/events?after=<n>` (SSE) | Fallback: poll every 2000 ms; 10 consecutive failures tolerated |
| Run state | `GET {base}/runs/{runId}` | |
| Cancel | `POST {base}/runs/{runId}/cancel` | |
| List files | `GET {base}/threads/{threadId}/files?path=` | Walked to depth 3 |
| Download file | `GET {base}/threads/{threadId}/files/download?path=` | Limited by `MAX_ARTIFACT_BYTES` |

Adapter `acp` (ACP 0.2.0): `/ping`, `/agents` (needs agent `headlessbob`), `/readyz`, `POST /runs` (async), poll `/runs/{id}/events` and `/runs/{id}`, `POST /runs/{id}/cancel`. `supportsFiles=false`, so no artifacts or report file.

### 6.5 SSE contract (`GET /api/executions/:id/stream`)

Response headers: `Content-Type: text/event-stream`, `Cache-Control: no-cache, no-transform`, `Connection: keep-alive`, `X-Accel-Buffering: no`.

```text
event: execution
data: {"id":"…","status":"running","steps":[…],"…":"…"}

id: 42
event: log
data: {"id":42,"executionId":"…","ts":"2026-11-10T08:00:01.000Z","source":"headless-bob","level":"info","step":"bob_processing","message":"…"}

: heartbeat
```

- `execution` events contain the full `Execution` view; `log` events contain one `ExecutionLog` and an SSE `id:` equal to the log id.
- Resume cursor: `Last-Event-ID` header or `?after=<id>`.
- Heartbeat comment every 15 s.
- No `retry:` field is sent; the client implements its own 2 s reconnect.

### 6.6 GitHub interactions

Done with the `git` CLI only (no GitHub REST API, no GitHub App/OAuth):

| Operation | Command |
|---|---|
| Validate | `git ls-remote --exit-code --heads <url> <branch>` |
| Clone | `git clone --depth 1 --single-branch --no-tags --progress --branch <branch> <url> <dir>.new` |
| Auth | `GIT_CONFIG_COUNT/KEY_0/VALUE_0` = `http.extraHeader: Authorization: Basic base64("x-access-token:<token>")` |
| Hardening | `GIT_ALLOW_PROTOCOL=https`, `GIT_TERMINAL_PROMPT=0`, hooks path disabled, `credential.helper=` empty, remote `origin` removed after clone |

### 6.7 Internal interfaces

| Interface | File | Contract |
|---|---|---|
| `HeadlessBobAdapter` | `backend/src/integrations/headless-bob/types.ts` | `testConnection`, `createThread`, `sendMessage`, `streamEvents`, `getRun`, `cancel`, `listFiles`, `downloadFile`, `supportsFiles` |
| Adapter factory | `…/factory.ts` | Creates `rest-threads` or `acp` adapters; throws `demo_mode` unless `STREAM_MODE=realtime` |
| `PathMapper` | `backend/src/utils/paths.ts` | `toBob(path)`, `list()`; longest-prefix |
| `SecretBox` | `backend/src/utils/secret-box.ts` | `seal`, `open`, `activeKeyId`; envelope `{v, kid, iv, tag, ct}` with the kid as AAD |
| `ExecutionLogService` | `backend/src/services/execution-log.service.ts` | `append`, `list(id, after)`, `subscribe(id, fn)` |
| `runFile` | `backend/src/utils/safe-exec.ts` | `spawn` with `shell:false`, detached group, timeout then SIGKILL after 2 s, output cap 1 MiB, `minimalEnv()` |
