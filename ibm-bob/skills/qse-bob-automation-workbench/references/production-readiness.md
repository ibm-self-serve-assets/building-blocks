# Production readiness

> Extracted verbatim from `SPEC.md` (section 12). Do not edit here; edit SPEC.md and re-extract.

## 12. Non-functional and production readiness

No performance benchmark has been measured for this application, so none is stated here.

## 12.1 Readiness checklist

| Area | Item | Status | Evidence |
|---|---|---|---|
| Observability | Structured JSON logs with redaction (pino) | Implemented | `backend/src/utils/logger.ts`, `backend/src/utils/redact.ts` |
| Observability | Request id on every response (`x-request-id`) and in the error envelope | Implemented | `backend/src/middleware/context.ts` |
| Observability | Liveness `/healthz` and readiness `/readyz` (database, workspace, accepting) | Implemented | `backend/src/app.ts` |
| Observability | Metrics endpoint, tracing, alerting | **Planned** | not in code |
| Reliability | Graceful shutdown on SIGTERM/SIGINT, hard stop after 25 s, new executions refused with 503 `shutting_down` | Implemented | `backend/src/server.ts` |
| Reliability | Active executions marked failed after restart | Implemented | `backend/src/orchestrators/execution.orchestrator.ts` |
| Reliability | Queued executions restored after restart | **Not implemented** | in-memory queue |
| Reliability | Retry of Bob calls | Partial | Idempotency key on run start (`backend/src/integrations/headless-bob/rest-threads.adapter.ts`); event polling tolerates 10 consecutive failures; no general retry |
| Scalability | Horizontal scaling | **Not supported** | SQLite, in-memory SSE bus, queue and rate limiter (NFR-07) |
| Security | Secure headers, CSRF, Origin check, rate limits, SSRF guard, shell-free exec | Implemented | section 8 |
| Security | TLS | Partial: optional override `deployment/docker-compose.tls.yml`; certificates are supplied by the operator |
| Security | SSO, MFA, user management, audit log | **Planned** | not in code |
| Container hardening | Non-root uid 1001 (backend) / 101 (NGINX), `cap_drop: ALL`, `no-new-privileges`, read-only root FS with tmpfs | Implemented: `deployment/docker-compose.yml` (see section 8) |
| Data | Backup | Manual: copy the SQLite file(s) and the workspace volume while the service is stopped or using SQLite backup tooling; no automated backup |
| Data | Retention and cleanup of executions, logs, reports, workspaces | **Not implemented** (no delete API) |
| Data | Schema migrations | Partial: schema is created by `backend/src/db/database.ts` on start; no versioned migration framework |
| Upgrade | Rebuild images and restart; the `--check` scripts validate configuration first | Implemented |
| Quality | Typecheck, unit and integration tests, `npm audit --omit=dev` | Implemented |
| Quality | E2E, accessibility, load tests | **Not implemented** |

## 12.2 Operating limits (configurable, from section 10.5)

| Limit | Variable | Default |
|---|---|---|
| Concurrent executions | `MAX_CONCURRENT_EXECUTIONS` | 1 (max 16) |
| Execution timeout | `EXECUTION_TIMEOUT_MS` | 1800000 |
| Prompt size | `MAX_PROMPT_CHARS` | 8000 (max 15000) |
| Request rate | `RATE_LIMIT_MAX`, `LOGIN_RATE_LIMIT_MAX` | 300 per window; 10 per 15 min |
| Session lifetime | `SESSION_IDLE_MINUTES`, `SESSION_TTL_MINUTES` | 60 idle; 480 absolute |
| Bob run wait | Headless Bob's own run timeout (`RUN_TIMEOUT_MS` in Bob; README states a 5 minute default there; the compose `bob` profile sets `BOB_RUN_TIMEOUT_MS` to 1800000) | Raise it on the Bob side for large scans |

## 12.3 Production go/no-go blockers

1. Set `STREAM_MODE=realtime` explicitly; the default is `mock`.
2. Provide `SESSION_SECRET`, `ENCRYPTION_KEY` and a strong `ADMIN_PASSWORD`; serve over TLS so cookies are `Secure`.
3. Accept the single-node constraint and plan manual backups.
4. Accept that there is no retention policy and that the real analysis requires a reachable Headless Bob and QSE CLI.
