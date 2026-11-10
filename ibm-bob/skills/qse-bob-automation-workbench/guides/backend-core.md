# Backend core guide

## When to use

After `foundation.md`. Use for everything in the backend that is not an external integration or the execution pipeline: persistence, identity, security middleware, the complete REST route table, Settings and observability.

## Inputs you need

- `BUILD_DECISIONS.md` (G1, G6, G13, G21 decisions).
- [api-and-errors.md](../references/api-and-errors.md): SPEC 6.1-6.3 and the error catalogue (SPEC 9).
- [data-model-and-security.md](../references/data-model-and-security.md): ER diagram, table notes, security controls and threats (SPEC 7, 8).
- Config object from `backend/src/config/env.ts`.

## Requirements covered

| ID | Requirement | Acceptance test |
|---|---|---|
| FR-01 | Auth on every `/api` route except `POST /api/auth/login` | Any other route without a session returns 401 `unauthorized` (AC-01). |
| FR-02 (store) | Secrets stored only encrypted, never returned | `GET /api/bob/status` carries `apiKeyHint` only (AC-03); stored `api_key_enc`/`token_enc` are SecretBox envelopes. |
| FR-11 | Admin can re-encrypt stored secrets with the active key | `POST /api/admin/rotate-secrets` returns `{activeKeyId, bobApiKeyReencrypted, repositoryTokensReencrypted}` and data still decrypts (AC-13). |
| NFR-01 | Secrets never in logs, responses, URLs or browser storage | Redaction unit tests; no response contains key or token. |
| NFR-04 | Graceful shutdown on SIGTERM/SIGINT, hard stop after 25 s | New executions get 503 `shutting_down`; process exits within 25 s. |

## Steps

### 1. Database (`backend/src/db/database.ts`)

- `DatabaseSync` from `node:sqlite`; pragmas `journal_mode=WAL`, `foreign_keys=ON`, `busy_timeout=5000`; migrations via `PRAGMA user_version` (one migration creating everything).
- Eleven tables: `users`, `sessions`, `bob_connection`, `repositories`, `qse_config`, `executions`, `execution_steps`, `execution_logs`, `reports`, `artifacts`, `prompt_history`. Copy columns from the ER diagram in data-model-and-security.md. Keep: `bob_connection` and `qse_config` have `CHECK (id = 1)`; `executions.repository_id` has **no** FK; cascades from `executions` to steps, logs, reports, artifacts and from `users` to sessions; indexes `executions_created (created_at DESC)` and `execution_logs_exec (execution_id, id)`.
- One repository class per aggregate under `backend/src/repositories/*.repository.ts` (auth, git-repository, bob-connection, qse-config, execution). SQL lives only here.

### 2. Auth and sessions (SPEC 4.0, 8.1)

- Password hashing: scrypt N=16384, r=8, p=1, with a dummy-hash verification for unknown users (uniform timing and text "Invalid username or password").
- Session id random; only its sha256 stored (`sessions.id_hash`). Cookie `qse_sid`: httpOnly, SameSite=Strict, `Secure` per `COOKIE_SECURE` (forced when `NODE_ENV=production`). Per-session CSRF token returned in the login body and `/auth/me`.
- Idle expiry `SESSION_IDLE_MINUTES` (60), absolute `SESSION_TTL_MINUTES` (480); expired sessions deleted on use; purge job every 5 minutes.
- Roles `viewer` < `operator` < `admin`. Bootstrap admin from `ADMIN_USERNAME`/`ADMIN_PASSWORD` created on first start if absent.
- `POST /api/auth/password`: `currentPassword`, `newPassword` 12-256; wrong current password is 403 `invalid_credentials` ("Current password is incorrect"); success is 204 and **revokes all sessions of that user**.
- No user-management API (G6): faithful clone has only the bootstrap admin.

### 3. Security middleware (`backend/src/middleware/*`)

- helmet: CSP `default-src 'none'`, CORP same-origin, Referrer-Policy no-referrer. CORS allow-list `CORS_ALLOWED_ORIGINS` with credentials.
- Origin check on non-safe methods: allow a missing Origin, one in `CORS_ALLOWED_ORIGINS`, or one whose host equals `x-forwarded-host`/`host`; otherwise 403 `forbidden` "Cross-origin request rejected".
- CSRF: `X-CSRF-Token` timing-safe compare; mismatch is 403 `csrf_invalid`.
- Rate limits (`standardHeaders: 'draft-7'`): API `RATE_LIMIT_MAX` (300) per `RATE_LIMIT_WINDOW_MS`; login `LOGIN_RATE_LIMIT_MAX` (10) per 15 minutes; "heavy" routes `max(10, floor(RATE_LIMIT_MAX/6))`. Messages are in api-and-errors.md.
- JSON body limit 64 kb. Path params `:id`, `:artifactId` must match `^[A-Za-z0-9-]{1,64}$`, else 400 `invalid_parameter` ("Invalid <name>").
- Responses under `/api` carry `Cache-Control: no-store` and `x-request-id`.

### 4. Error envelope (`middleware/error-handler.ts`, SPEC 6.1, 9)

`{ "error": { code, message, details, requestId } }`. ZodError -> 400 `validation_error` ("Request validation failed", `details` = `[{path, message}]`); `AppError` -> own status/code with `redact()`ed message; body-parser 4xx -> `bad_request` ("Request body is too large" / "Malformed JSON body" / "Bad request"); anything else -> 500 `internal_error` ("An unexpected error occurred"). Unknown routes 404 `route_not_found`. Define `AppError` in `utils/errors.ts`.

### 5. Utilities

- `utils/secret-box.ts`: AES-256-GCM key ring from `SECRETS_KEYS` (`kid:base64(32 bytes)`); envelope `{v, kid, iv, tag, ct}` with the kid as AAD; `seal`, `open`, `activeKeyId`; failure surfaces as `secret_unreadable`.
- `utils/redact.ts` + `utils/logger.ts`: pino redact paths plus a regex redactor for GitHub tokens, Bearer/Basic, URL credentials, `authorization`, `api_key`/`token`/`secret`/`password`, plus registered live secrets.
- `utils/safe-exec.ts` (`runFile`): `spawn` with `shell:false`, detached group, timeout then SIGKILL after 2 s, output cap 1 MiB, `minimalEnv()`.
- `utils/ssrf.ts` and `utils/paths.ts` are used by `integrations.md`; create the files here only if that guide has not been followed yet.

### 6. Routes (`backend/src/routes/index.ts`, controllers in `controllers/index.ts`)

Implement every row of SPEC 6.2 with the exact role and status code (table is in api-and-errors.md; "Heavy" = additional heavy limiter):

- Auth: `POST /auth/login` (public, login limiter), `POST /auth/logout` (204), `GET /auth/me`, `POST /auth/password` (204).
- Settings: `GET /settings` (any), `POST /admin/rotate-secrets` (admin).
- All other rows (bob, repositories, qse, executions, reports) are wired here but their handlers are implemented by the integration and execution guides. Stub with the correct role middleware first, then fill in.
- `router.use(authenticate)` after the explicit login route, so everything else is protected.

### 7. Settings (SPEC 4.9)

- `GET /api/settings` returns `version` (hard-coded `"1.0.0"` in the reference, G13), `streamMode`, `executionStrategy`, `githubAllowedHosts`, `limits{maxPromptChars, executionTimeoutMs, maxConcurrentExecutions}`, `sharedMounts[{label, bobPath}]`, `encryptionKeyId`, `session{ttlMinutes, idleMinutes}`. Never include internal filesystem paths.
- `POST /api/admin/rotate-secrets` re-encrypts the Bob key and every repository token with the first key in `SECRETS_KEYS`. Procedure: put a new `kid:key` first, restart, call the endpoint; old keys stay in the list for decryption. Non-admin gets 403.
- If BUILD_DECISIONS says "fix" for G13, read the version from `package.json` instead of hard-coding it.

### 8. Observability and lifecycle (`app.ts`, `server.ts`)

- pino JSON logs with redaction; `x-request-id` generated or taken from the incoming header, set on every response and included in the error envelope.
- `GET /healthz` -> `{"status":"ok"}`. `GET /readyz` -> 200 or 503 `{"status":"ready"|"not_ready","checks":{"database","workspace","accepting"}}` (`workspace` = repository list works; `accepting` = not shutting down).
- Optional HTTPS in the Node server when `TLS_KEY_FILE`/`TLS_CERT_FILE` are set.
- SIGTERM/SIGINT: stop accepting, wait for in-flight work, hard exit after 25 s (NFR-04).
- Metrics, tracing and alerting are **Planned** (G21). Do not implement them in a faithful clone.

## Verification (exit gate)

```bash
cd backend && npm run typecheck && npm test && npm run build && npm audit --omit=dev
```

- FR-01: test that every route except login returns 401 without a cookie; CSRF and Origin tests (AC-01, AC-02).
- FR-02/NFR-01: test that `GET /bob/status` has no key material; logger test that a token string is redacted (AC-03).
- FR-11: rotation test (AC-13).
- NFR-04: start the built server, send SIGTERM, confirm it exits and that `/readyz` reports `accepting:false` before exit.
- Observability: `GET /healthz` 200, `GET /readyz` has the three keys, a response has `x-request-id`.
- Route audit: every method+path in SPEC 6.2 exists with the same role.

## Pitfalls

- Returning `apiKey` or tokens anywhere, including in error `details`.
- Different text for unknown user vs bad password (breaks uniform errors).
- Forgetting `Cache-Control: no-store` on `/api`.
- Applying `authenticate` before the login route.
- Adding an FK from `executions.repository_id` (history must survive repository deletion).
- Implementing metrics or user management in a faithful clone.

## Known gaps that apply

- G1: prompt limit mismatch (zod 1-20000 in `models/schemas.ts` vs `MAX_PROMPT_CHARS`). User decision: <fix | keep as built>
- G6: no user-management API/UI. User decision: <fix | keep as built>
- G13: `/settings` version hard-coded "1.0.0". User decision: <fix | keep as built>
- G21: no metrics/tracing/alerts, automated backup or versioned migrations. User decision: <fix | keep as built>

## SPEC references

SPEC 4.0, SPEC 4.9, SPEC 6.1, SPEC 6.2, SPEC 6.3, SPEC 6.7, SPEC 7, SPEC 8, SPEC 9, SPEC 12.1. Detail: [api-and-errors.md](../references/api-and-errors.md), [data-model-and-security.md](../references/data-model-and-security.md).
