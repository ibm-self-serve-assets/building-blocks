# Integrations guide

## When to use

After `backend-core.md`. Use for the three features that talk to the outside world: Bob connection (4.1), GitHub repository management (4.2) and QSE CLI discovery and validation (4.3).

## Inputs you need

- [bob-github-qse.md](../references/bob-github-qse.md): SPEC 4.1-4.3 and 6.4-6.7 verbatim.
- Error codes from `../references/SPEC.md` section 9.
- `BUILD_DECISIONS.md` (G11, G18, G20).
- The core pieces from `backend-core.md`: SecretBox, redact, safe-exec, error classes, route stubs.

## Requirements covered

| ID | Requirement | Acceptance test |
|---|---|---|
| FR-02 (Bob key, repo tokens) | Sealed at rest, never returned | `Repository` exposes `hasToken` boolean only; `BobConnection` exposes `apiKeyHint` (`••••<last4>`) only. |
| NFR-02 | Outbound Bob HTTP is SSRF-guarded, redirects not followed | Blocked address classes are refused at save and at connect time (AC-15); undici is configured with `maxRedirections: 0`. |
| NFR-03 | No shell, repository content never executed | `git` and the QSE CLI run via `runFile` (`shell:false`); a repository with an escaping symlink is rejected or pruned (AC-16). |

## Steps

### 1. SSRF guard (`utils/ssrf.ts`, `integrations/headless-bob/http-client.ts`)

- Endpoint: http(s) only, no credentials/query/fragment, length <= 300 (`invalid_endpoint`).
- Hostname allow-list `BOB_ALLOWED_HOSTS`; DNS-time classification of every resolved IP via a guarded undici `lookup`; metadata, link-local and reserved ranges **always** blocked; private/loopback only when `BOB_ALLOW_PRIVATE_NETWORK=true` (`endpoint_not_allowed`).
- Limits: JSON response 4 MiB, SSE buffer 8 MiB; request timeout `BOB_REQUEST_TIMEOUT_MS` (15000).

### 2. Bob service and adapters (SPEC 4.1, 6.4, 6.7)

- `bobConnectSchema`: `endpoint` <= 300; `adapter` `rest-threads|acp`; `apiBasePath` default `/api/v1` (must look like `/api/v1`, else `invalid_base_path`); `authMode` `bearer|header|none`; `authHeaderName` default `authorization` (token chars only, else `invalid_header_name`); `apiKey` 8-512 chars, no whitespace (`invalid_api_key`).
- A key is required for a new or changed endpoint (`api_key_required`); unchanged endpoint with no key keeps the stored key. Store a SecretBox envelope plus hint.
- `save()` normalises, validates, seals, persists with state `connecting` and **immediately calls `test()`**. `test()` maps: success -> `connected`; HTTP 401/403 -> `auth_failed`; 404 or any other failure -> `connection_failed`. Persist state, message and capabilities. `disconnect()` deletes the row; 409 `execution_active` if a run is active.
- Adapter interface `HeadlessBobAdapter` (`integrations/headless-bob/types.ts`): `testConnection`, `createThread`, `sendMessage`, `streamEvents`, `getRun`, `cancel`, `listFiles`, `downloadFile`, `supportsFiles`; `startRun({prompt,title,idempotencyKey})` returns a run handle.
- `rest-threads` calls (all under `{base}` except healthz): `GET /healthz` (no auth, no base), `GET {base}/capabilities`, `POST {base}/threads`, `POST {base}/threads/{id}/messages` (header `idempotency-key`), `GET {base}/runs/{id}/events?after=` (SSE, poll fallback every 2000 ms, 10 consecutive failures tolerated), `GET {base}/runs/{id}`, `POST {base}/runs/{id}/cancel`, `GET {base}/threads/{id}/files?path=`, `GET {base}/threads/{id}/files/download?path=`.
- `acp` (ACP 0.2.0): `/ping`, `/agents` (needs agent `headlessbob`), `/readyz`, `POST /runs` (async), poll `/runs/{id}/events` and `/runs/{id}`, `POST /runs/{id}/cancel`. `supportsFiles=false` -> no artifacts and no report file (**Partial**, G18).
- `factory.ts` creates the adapter; it throws `demo_mode` unless `STREAM_MODE=realtime`.
- `events.ts`: helpers that turn Bob events into text deltas and statuses (unit-tested).
- Auth header: `bearer` -> `Authorization: Bearer <key>`; `header` -> `<authHeaderName>: <key>`; `none` -> no header.
- Bob's own run timeout defaults to 5 minutes (G20). It is configured on the Bob side. Document it; do not hide it.

### 3. GitHub repository service (SPEC 4.2, 6.6)

- URL rules (`integrations/github/url.ts`): https only; no credentials, query, hash or port; host in `GITHUB_ALLOWED_HOSTS`; exactly `owner/repo`; branch regex. Errors: `invalid_repository_url`, `repository_host_not_allowed`, `invalid_branch`. Token 8-255 chars, no whitespace (`invalid_token`).
- Validate: `git ls-remote --exit-code --heads <url> <branch>` -> owner, name, branch, head commit (`branch_not_found` 422, `repository_unreachable` 422, `git_timeout` 504).
- Clone (202, background): status `cloning`; `git clone --depth 1 --single-branch --no-tags --progress --branch <b>` into `<dir>.new` under `WORKSPACE_ROOT/repo-<hex>/`, then rename to `repo`; remove escaping symlinks, count files (cap 250 000, `repository_too_large`), remove remote `origin`, read HEAD; status `cloned`.
- Hardening env: `GIT_ALLOW_PROTOCOL=https`, `GIT_TERMINAL_PROMPT=0`, hooks path disabled, empty `credential.helper`. Token only via `GIT_CONFIG_COUNT/KEY_0/VALUE_0` = `http.extraHeader: Authorization: Basic base64("x-access-token:<token>")`, never argv or URL.
- Progress keeps the last 30 sanitised lines (paths scrubbed). Re-clone (202), remove (204, deletes work dir and row). `workspaceLabel` is `<dirName>/repo`, never a host path.
- On restart, repositories left in `cloning`/`validating` become `failed`. The repository list is global (not per user).

### 4. QSE CLI service (SPEC 4.3)

- Discovery never executes anything: candidates from `QSE_CLI_PATH`, then `PATH`, then `QSE_CLI_SEARCH_DIRS`. `allowed` = real path inside `QSE_CLI_ALLOWED_DIRS` **and** basename in `QSE_CLI_EXECUTABLE_NAMES`; `executable` from file mode.
- Configure: `qseConfigureSchema` `mode auto|manual`, `path` <= 1024, `versionArgs` <= 4 items each matching `^[A-Za-z0-9._=-]{1,40}$` (`invalid_version_args`). Auto requires a candidate that is `allowed && executable` (`not_a_candidate`; none -> `qse_not_found`). Manual requires an absolute `path` (`path_required`, `invalid_qse_path`).
- Validate: `runFile` with `QSE_CLI_VERSION_ARGS` (default `-v`), cwd = the CLI directory, `minimalEnv()` plus the real `HOME` (the CLI keeps licence state in `$HOME/qs-explorer`), timeout `QSE_VALIDATION_TIMEOUT_MS` (30000), output cap 1 MiB. Output containing "license agreement has not been accepted" -> `invalid` even with exit 0. **The workbench never accepts the licence.** `extractVersion` prefers a line like `version: <digits>`, else the first non-empty line.
- `PathMapper` (`utils/paths.ts`): longest-prefix mapping; adds `bobVisiblePath`, `reachableFromBob` and `strategy` to the result. Strategies: `shared-volume` (explicit mounts) and `colocated` (identity). A path outside every mount is not reachable.
- Endpoints: `GET /qse/discover`, `POST /qse/configure`, `POST /qse/validate`, `GET /qse/status`.

### 5. Controllers and tests

Wire the handlers into the route stubs from backend-core (roles per SPEC 6.2: validate/clone/reclone/connect/test/configure are operator + heavy; delete repo and disconnect operator, not heavy).

## Verification (exit gate)

```bash
cd backend && npm run typecheck && npm test
```

Tests to write or confirm (names mirror the reference suites):

- Bob (11): connect/test states, SSRF classes, allow-list, key rotation, no key in responses, removed mock adapter (no mock adapter class exists in production code).
- GitHub (5 + 3 unit): URL, branch and token validation, host allow-list, clone with a fake git or local bare repo, symlink escape (AC-16).
- QSE (6 + 6 unit): discovery, allow-listing, licence text, `extractVersion`.
- FR-02/NFR-02/NFR-03 statements above each have a passing test.

## Pitfalls

- Passing the token in a URL or argv. Use the header env only.
- Following redirects from Bob.
- Executing candidates during discovery.
- Accepting the QSE licence automatically.
- Treating ACP as equal to rest-threads. It cannot return files (G18).
- Using a shell for `git`.

## Known gaps that apply

- G11: QSE `versionArgs` not editable in the UI (API/env only). User decision: <fix | keep as built>
- G18: ACP adapter has no file API. User decision: <fix | keep as built>
- G20: Headless Bob run timeout defaults to 5 minutes. User decision: <fix | keep as built>

## SPEC references

SPEC 4.1, SPEC 4.2, SPEC 4.3, SPEC 5.4, SPEC 5.5.1, SPEC 5.5.2, SPEC 5.5.3, SPEC 6.4, SPEC 6.6, SPEC 6.7, SPEC 8.1. Detail: [bob-github-qse.md](../references/bob-github-qse.md).
