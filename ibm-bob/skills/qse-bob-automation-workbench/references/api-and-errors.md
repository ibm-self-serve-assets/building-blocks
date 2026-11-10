# REST API, error envelope and error catalogue

> Extracted verbatim from `SPEC.md` (sections 6.1-6.3 and 9). Do not edit here; edit SPEC.md and re-extract. Paths are relative to the project root.

### 6.1 Error envelope

```json
{ "error": { "code": "bob_not_connected", "message": "Headless Bob is not connected. Test the connection first.", "details": null, "requestId": "6f1c2c1e-…" } }
```

Produced by `middleware/error-handler.ts`:

| Source | HTTP | `code` | `message` | `details` |
|---|---|---|---|---|
| `ZodError` | 400 | `validation_error` | "Request validation failed" | `[{ "path": "...", "message": "..." }]` |
| `AppError` | its own status | its own code | its message, passed through `redact()` | its own details or null |
| Body-parser 4xx | 400 (or the parser's status) | `bad_request` | "Request body is too large", "Malformed JSON body" or "Bad request" | null |
| Anything else | 500 | `internal_error` | "An unexpected error occurred" | null |

Unknown routes: 404 `route_not_found`. Rate limiters: 429 `rate_limited` ("Too many requests. Please slow down and retry shortly."; login: "Too many sign-in attempts. Try again later."), with `RateLimit` draft-7 headers. Invalid path parameter: 400 `invalid_parameter`, message "Invalid <name>". CSRF mismatch: 403 `csrf_invalid`. Cross-origin write: 403 `forbidden`, "Cross-origin request rejected".

### 6.2 Application REST endpoints

Role column: `any` = authenticated viewer or above; `op` = operator or admin; `adm` = admin. "Heavy" = additionally rate limited to `max(10, floor(RATE_LIMIT_MAX/6))` per window.

| Method | Path | Role | Heavy | Success | Notes |
|---|---|---|---|---|---|
| POST | `/auth/login` | public | login limiter | 200 | Sets `qse_sid` cookie |
| POST | `/auth/logout` | any | no | 204 | Clears cookie, deletes session |
| GET | `/auth/me` | any | no | 200 | `{user, csrfToken}` |
| POST | `/auth/password` | any | no | 204 | Revokes all sessions of the user |
| GET | `/bob/status` | any | no | 200 | `BobConnection` |
| POST | `/bob/connect` | op | yes | 200 | Saves then tests |
| POST | `/bob/test-connection` | op | yes | 200 | |
| POST | `/bob/disconnect` | op | no | 200 | 409 `execution_active` |
| GET | `/repositories` | any | no | 200 | `{items}` |
| POST | `/repositories/validate` | op | yes | 200 | `RepoValidation` |
| POST | `/repositories/clone` | op | yes | 202 | `Repository` |
| GET | `/repositories/:id` | any | no | 200 | |
| POST | `/repositories/:id/reclone` | op | yes | 202 | |
| DELETE | `/repositories/:id` | op | no | 204 | |
| GET | `/qse/discover` | op | no | 200 | `{candidates, searched}` |
| POST | `/qse/configure` | op | yes | 200 | |
| POST | `/qse/validate` | op | yes | 200 | |
| GET | `/qse/status` | any | no | 200 | |
| POST | `/executions` | op | yes | 202 | `Execution` |
| GET | `/executions` | any | no | 200 | `Page<Execution>` |
| GET | `/executions/prompts` | any | no | 200 | `{items}` |
| GET | `/executions/:id` | any | no | 200 | |
| GET | `/executions/:id/stream` | any | no | 200 SSE | See 6.5 |
| POST | `/executions/:id/cancel` | op | no | 202 | |
| GET | `/executions/:id/logs?after=` | any | no | 200 | `{items}` |
| GET | `/executions/:id/report` | any | no | 200 | 404 when no report |
| GET | `/executions/:id/artifacts` | any | no | 200 | `{items}` |
| GET | `/executions/:id/artifacts/:artifactId/download` | any | no | 200 | Binary attachment |
| GET | `/reports/:id` | any | no | 200 | |
| GET | `/reports/:id/download?format=` | any | no | 200 | `markdown` (default), `pdf`, `json` |
| GET | `/reports/:id/export` | any | no | 200 | `{report, logs}` JSON attachment |
| GET | `/settings` | any | no | 200 | |
| POST | `/admin/rotate-secrets` | adm | no | 200 | |

Path-parameter rule: `:id` and `:artifactId` must match `^[A-Za-z0-9-]{1,64}$`, otherwise 400 `invalid_parameter`.

Non-`/api` endpoints served by the backend: `GET /healthz` → `{"status":"ok"}`; `GET /readyz` → 200/503 `{"status":"ready"|"not_ready","checks":{"database","workspace","accepting"}}`. NGINX forwards both and also serves `GET /nginx-health` itself.

### 6.3 JSON examples

**Login**

```http
POST /api/auth/login
{ "username": "admin", "password": "…" }
```
```json
{ "user": { "id": "2d0f…", "username": "admin", "role": "admin" }, "csrfToken": "b3c1…" }
```

**Bob connect (request)**

```json
{ "endpoint": "http://127.0.0.1:8000", "adapter": "rest-threads", "apiBasePath": "/api/v1", "authMode": "bearer", "authHeaderName": "authorization", "apiKey": "<service token>" }
```

**BobConnection (response)**

```json
{
  "state": "connected", "configured": true, "endpoint": "http://127.0.0.1:8000", "adapter": "rest-threads",
  "apiBasePath": "/api/v1", "authMode": "bearer", "authHeaderName": "authorization", "apiKeyHint": "••••abcd",
  "message": "Connected", "lastTestedAt": "2026-11-10T08:00:00.000Z", "mock": false,
  "capabilities": {
    "adapter": "rest-threads", "runtimeReady": true,
    "features": { "streaming": true, "cancellation": true, "fileDownloads": true, "threads": true, "continuation": true },
    "limits": { "timeoutMs": 300000, "maxMessageCharacters": 20000, "maxConcurrentRuns": 2, "maxDownloadBytes": 26214400 }
  }
}
```

**Repository clone (request / response)**

```json
{ "url": "https://github.com/owner/repo", "branch": "main", "token": "ghp_…optional" }
```
```json
{ "id": "7c1e…", "url": "https://github.com/owner/repo", "name": "repo", "owner": "owner", "branch": "main", "status": "cloning",
  "error": null, "hasToken": true, "commit": null, "fileCount": null, "lastClonedAt": null, "createdAt": "…",
  "workspaceLabel": null, "progress": [] }
```

**QSE configure (request) / QseConfig (response)**

```json
{ "mode": "auto", "path": "/usr/local/bin/qse-cli-artifacts/cli.sh" }
```
```json
{ "status": "valid", "mode": "auto", "executablePath": "/usr/local/bin/qse-cli-artifacts/cli.sh", "bobVisiblePath": "/usr/local/bin/qse-cli-artifacts/cli.sh",
  "reachableFromBob": true, "version": "App Version : 2.3.1.0 Build Version : 202605.00095", "validatedAt": "…", "message": null,
  "versionArgs": ["-v"], "strategy": "colocated" }
```

**Create execution (request) / Execution (response, abbreviated)**

```json
{ "repositoryId": "7c1e4f9a-…-uuid", "prompt": "Analyze this repository using QSE CLI …" }
```
```json
{
  "id": "c0d229f4-…", "status": "queued", "currentActivity": null, "prompt": "…", "promptSummary": "Analyze this repository using QSE CLI …",
  "repositoryId": "7c1e…", "repositoryUrl": "https://github.com/owner/repo", "repositoryName": "repo", "branch": "main", "commit": "bcc625a…",
  "qseVersion": "App Version : 2.3.1.0 …", "adapter": "rest-threads", "mock": false, "bobRunId": null, "bobThreadId": null,
  "createdAt": "…", "startedAt": null, "finishedAt": null, "durationMs": null, "error": null, "warnings": [],
  "steps": [ { "key": "validate_config", "label": "Validating configuration", "source": "backend", "status": "pending", "startedAt": null, "finishedAt": null, "message": null } ],
  "reportId": null, "usage": null, "bobStreamedChars": 0
}
```

**Execution list**: `GET /api/executions?search=aws&status=completed&sort=createdAt&direction=desc&page=1&pageSize=10`

```json
{ "items": [ { "id": "…", "status": "completed", "…": "…" } ], "total": 1, "page": 1, "pageSize": 10 }
```

**Report (abbreviated)**

```json
{ "id": "…", "executionId": "…", "source": "headless-bob-file", "sourceDetail": "qse-e2e-report.md", "mock": false, "generatedAt": "…",
  "sections": [ { "key": "summary", "title": "Executive Summary", "markdown": "…" }, { "key": "findings", "title": "Quantum-Safe Assessment", "markdown": "…" } ],
  "bobMarkdown": "…", "markdown": "# QSE End-to-End Execution Report\n…", "execution": { "…": "…" },
  "artifacts": [ { "id": "…", "executionId": "…", "path": "qse-e2e-report.md", "size": 4096, "retrieved": true, "contentType": "text/markdown", "note": null } ] }
```

**Settings**

```json
{ "version": "1.0.0", "streamMode": "realtime", "executionStrategy": "colocated", "githubAllowedHosts": ["github.com"],
  "limits": { "maxPromptChars": 8000, "executionTimeoutMs": 1800000, "maxConcurrentExecutions": 1 },
  "sharedMounts": [ { "label": "…", "bobPath": "/shared/workspaces" } ], "encryptionKeyId": "k1",
  "session": { "ttlMinutes": 480, "idleMinutes": 60 } }
```

**Rotate secrets**: response `{ "activeKeyId": "k2", "bobApiKeyReencrypted": true, "repositoryTokensReencrypted": 1 }`.

## 9. Error-handling catalogue

Envelope: see 6.1. "User message" is what the UI shows (toast or inline notification) and is the server `message` unless noted. Logging: every error is logged by pino with `requestId`; 5xx at `error`, 4xx at `warn`/`info`, with redaction.

| Code | HTTP | Cause | Backend behaviour | User message | Recovery |
|---|---|---|---|---|---|
| `validation_error` | 400 | zod rejects body/query | Returns issues in `details` | Server message or first issue | Fix the input |
| `bad_request` | 400 | Malformed JSON / body-parser error | 400 with "Request body is too large", "Malformed JSON body" or "Bad request" | The server message | Resend valid JSON |
| `invalid_parameter` | 400 | Path param fails `^[A-Za-z0-9-]{1,64}$` | 400 | "Invalid <name>" (for example "Invalid id") | Use a valid id |
| `unauthorized` | 401 | Missing/expired/invalid session | 401; client handler clears state | Redirect to `/login` | Sign in |
| `invalid_credentials` | 401 / 403 | Wrong login (401) or wrong current password (403) | Generic message | "Invalid username or password" / "Current password is incorrect" | Retry |
| `forbidden` | 403 | Role too low or cross-origin request | 403 | Server message | Use a permitted role |
| `csrf_invalid` | 403 | Missing/mismatched `X-CSRF-Token` | 403 | "CSRF token missing or invalid" | Reload to refresh the token |
| `not_found` | 404 | Unknown execution/repo/report/artifact | 404 | e.g. "Execution not found" | Navigate back |
| `route_not_found` | 404 | Unknown route | 404 | "No route for METHOD /path" | n/a |
| `conflict` | 409 | Duplicate active run, clone/reclone conflicts | 409 | Server text | Wait or cancel |
| `execution_active` | 409 | Disconnect during an active execution | 409 | "Cancel the active execution before disconnecting." | Cancel first |
| `bob_not_configured` | 409 | Test/use before save | 409 | "Headless Bob is not configured" | Save settings |
| `qse_not_configured` | 409 | Validate with no path | 409 | "QSE CLI is not configured" | Configure |
| `rate_limited` | 429 | Limiter hit | 429 with `RateLimit-*` headers | "Too many requests…" / "Too many sign-in attempts. Try again later." | Wait |
| `invalid_endpoint` | 400 | Bob URL malformed/credentials/query/scheme | 400 | See `utils/ssrf.ts` messages | Correct URL |
| `endpoint_not_allowed` | 400 | Blocked address or host not in allow-list | 400 | "Endpoint resolves to a blocked address range…" | Adjust `BOB_ALLOWED_HOSTS` / `BOB_ALLOW_PRIVATE_NETWORK` |
| `invalid_base_path` | 400 | Base path not like `/api/v1` | 400 | "API base path must look like /api/v1" | Correct it |
| `invalid_header_name` | 400 | Bad custom header | 400 | "Authentication header name is invalid" | Correct it |
| `invalid_api_key` | 400 | Key length/whitespace | 400 | "API key format is invalid" | Re-enter |
| `api_key_required` | 400 | No key for new/changed endpoint | 400 | "An API key is required (re-enter it when the endpoint changes)." | Enter key |
| `secret_unreadable` | 500 | Stored ciphertext cannot be opened (key ring changed) | 500 | "The stored API key cannot be decrypted with the configured SECRETS_KEYS. Re-enter the API key." | Re-enter key or restore key ring |
| `demo_mode` | 500 | Adapter/test requested in mock mode | 500 | "Headless Bob is never contacted when STREAM_MODE=mock." | Use realtime |
| `invalid_repository_url` | 400 | URL not https/owner/repo, has credentials/query/port | 400 | e.g. "Enter a repository URL such as https://github.com/owner/repo" | Fix URL |
| `repository_host_not_allowed` | 400 | Host not in `GITHUB_ALLOWED_HOSTS` | 400 | `Host "x" is not allowed. Allowed hosts: …` | Add host |
| `invalid_branch` | 400 | Branch regex failure | 400 | "Branch name contains invalid characters" | Fix branch |
| `invalid_token` | 400 | Token not 8–255 chars or has whitespace | 400 | "Access token format is invalid" | Re-enter |
| `branch_not_found` | 422 | `ls-remote` finds no such head | 422 | `Branch "x" was not found in the repository` | Fix branch |
| `repository_unreachable` | 422 | Auth/DNS/not-found from git | 422 with explained stderr | Explained, redacted text | Check URL/token |
| `git_timeout` | 504 | `ls-remote` or clone timed out (`CLONE_TIMEOUT_MS`) | 504 | "Timed out contacting the repository" / "Clone timed out" | Retry |
| `clone_failed` | 422 | Non-zero git exit or no repo root | Repo status `failed`, `error` set | "Clone failed" notification with reason | Re-clone |
| `clone_cancelled` | 499 | Clone cancelled | Repo `failed` | "Clone was cancelled" | Re-clone |
| `repository_too_large` | 422 | More than 250 000 files | Repo `failed` | "Repository has more than 250000 files" | Use a smaller repo |
| `git_unavailable` | 500 | `git` binary missing | 500 | "The git CLI is not available on the server" | Install git / set `GIT_BIN` |
| `workspace_invalid` | 500 | Workspace path fails validation | 500 | "Repository workspace failed path validation" | Re-clone |
| `invalid_qse_path` | 400 | Path empty or not absolute | 400 | "Provide the absolute path to the QSE CLI executable" / "The QSE CLI path must be absolute" | Fix |
| `invalid_version_args` | 400 | More than 4 args or unsafe chars | 400 | "Version arguments must be at most 4 simple flags such as -v" | Fix |
| `not_a_candidate` | 400 | Chosen path not found by discovery | 400 | "The selected path was not found by discovery. …" | Re-run discovery |
| `qse_not_found` | 404 | Discovery finds nothing | 404 | "No QSE CLI was found in QSE_CLI_PATH, PATH or the configured search directories." | Install or use manual |
| `path_required` | 400 | Manual mode without a path | 400 | "Provide the absolute path to the QSE CLI executable" | Enter path |
| `prompt_required` | 422 | Empty prompt | 422 | "Enter a prompt before starting an execution" | Enter text |
| `prompt_too_long` | 422 | Over `MAX_PROMPT_CHARS` | 422 | "Prompt exceeds N characters" | Shorten |
| `bob_not_connected` | 422 | Bob not `connected` at start or run time | 422 | "Headless Bob is not connected. Test the connection first." | Test connection |
| `repository_not_cloned` | 422 | Repo not `cloned` | 422 | "The repository has not been cloned successfully." | Clone |
| `qse_not_validated` | 422 | QSE not valid | 422 | "The QSE CLI is not configured and validated." | Validate |
| `qse_not_reachable` | 422 | CLI outside shared mounts | 422 | "The QSE CLI is not located in a directory shared with the Headless Bob container…" | Move under mount |
| `repo_not_reachable` | 422 | Workspace outside shared mounts | Step fails | "Repository workspace is not in a directory shared with Headless Bob." | Fix mounts |
| `qse_invalid` | 422 | Re-validation failed inside the run | Step `validate_qse` fails | "QSE CLI validation failed: …" | Fix CLI |
| `shutting_down` | 503 | Start during shutdown | 503 | "The service is shutting down" | Retry later |
| `cancelled` | 499 | Run cancelled | Execution `cancelled` | "Execution cancelled" | n/a |
| `artifact_unavailable` | 502 | Bob cannot serve the file | 502 | "Could not download artifact from Headless Bob: …" | Retry; check Bob |
| `internal_error` | 500 | Unhandled exception | Logged with stack (redacted); generic body | "An unexpected error occurred" | Report the `requestId` |
| `network_error` (client only) | 0 | `fetch` rejected | `ApiError(0, …)` | "Cannot reach the Workbench backend. Check your connection." | Check network |
| Execution-level failures | n/a | Bob run failed, run timeout, adapter error, interrupted by restart | Execution `failed`, `error` text, failed step; no report invented; restart gives "Interrupted by a Workbench restart" | "Execution failed" notification with the error | Fix cause, start again |
