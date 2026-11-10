# Test inventory and acceptance criteria

> Extracted verbatim from `SPEC.md` (sections 11.1-11.6). Do not edit here; edit SPEC.md and re-extract.

## 11.1 Current test inventory (as run)

Last full run: backend **7 files, 110 tests passed**; frontend **6 files, 36 tests passed**. Counts for `it.each` suites are expanded, so they exceed the number of `it(` lines.

| Layer | Suite | Tests | Covers |
|---|---|---|---|
| Backend integration | `backend/tests/integration/security.test.ts` | 30 | Auth and CSRF, role enforcement, secure headers, rate limit, probes; Bob connection (11 tests: SSRF, allow-list, key rotation, removed mock adapter); GitHub (5); QSE (6) |
| Backend integration | `backend/tests/integration/workflow.test.ts` | 6 | connect → clone → validate → execute → report → history; fallback to final answer; Bob failure; cancel; start preconditions; symlink-escape clone |
| Backend integration | `backend/tests/integration/demo.test.ts` | 10 | Mock replay, default mock, validation still applies, setup required, cancel mid-replay, missing recording fails fast, realtime never serves demo data (4) |
| Backend unit | `backend/tests/unit/utils.test.ts` | 15 | Bob event helpers, SSRF classification, paths, redaction, SecretBox, passwords, safe-exec, config validation (requires secrets, defaults `STREAM_MODE=mock`, separate DB files, secure cookies in production) |
| Backend unit | `backend/tests/unit/report.test.ts` | 7 | Report section parsing, PDF, prompt builder |
| Backend unit | `backend/tests/unit/qse-validator.test.ts` | 6 | `extractVersion`, `validateQseCli` licence handling |
| Backend unit | `backend/tests/unit/github.test.ts` | 3 | GitHub URL and branch parsing |
| Frontend page | `frontend/src/pages/pages.test.tsx` | 10 | Login, Overview, Bob, Repository, Qse, Workspace, History, Reports, Settings rendering and actions |
| Frontend component | `frontend/src/components/PipelineTwin.test.tsx` | 5 | Digital twin nodes, edges, status mapping |
| Frontend component | `frontend/src/components/components.test.tsx` | 3 declared (expanded by `it.each` over `StatusTag`) | `StatusTag`, `LogViewer`, `Markdown` |
| Frontend unit | `frontend/src/services/api.test.ts` | 5 | CSRF header, error mapping, 401 handler |
| Frontend unit | `frontend/src/stores/stores.test.ts` | 4 | session, workspace, notifications stores |
| Frontend unit | `frontend/src/services/format.test.ts` | 4 | Formatting helpers |

## 11.2 Test infrastructure

| Item | Detail |
|---|---|
| Backend runner | Vitest, `environment: node`, include `tests/**/*.test.ts`, timeouts 30 s, `pool: forks` (`backend/vitest.config.ts`) |
| HTTP testing | `supertest` `^7.3.2` against the Express app built by `backend/tests/helpers/harness.ts` |
| Bob test double | `backend/tests/helpers/fake-bob.ts`: an in-process server that implements the Headless Bob REST-threads contract. It is a **contract double, not a product mock mode**; the production code contains no mock adapter (asserted by a security test) |
| Frontend runner | Vitest through `frontend/vite.config.ts` (jsdom, globals, `css: false`) |
| Frontend setup | `frontend/src/test/setup.ts` (jest-dom matchers; `matchMedia`, `ResizeObserver`, `scrollIntoView` shims); `frontend/src/test/utils.tsx` (render with providers) |
| Test data | Backend tests create temporary data directories; mock tests use `backend/demo-data/recorded-run.json` |

## 11.3 Commands and quality gate

```bash
cd backend  && npm run typecheck && npm test && npm run build && npm audit --omit=dev
cd frontend && npm run typecheck && npm test && npm run build && npm audit --omit=dev
./scripts/deploy_local.sh --check   # prerequisite and config check, realtime
./scripts/deploy_psh.sh   --check   # prerequisite and config check, mock
```

A change is acceptable only when all commands exit 0.

## 11.4 Testing mock versus realtime

| Aspect | `STREAM_MODE=mock` | `STREAM_MODE=realtime` |
|---|---|---|
| Needs Headless Bob, GitHub, QSE CLI | No | Yes |
| Database file | Separate demo file | Real file |
| Expected evidence | Records carry `mock=true`; filenames contain `-DEMO`; UI shows DEMO chip | `mock=false`; report source is `headless-bob-file` or `headless-bob-output` |
| Automated coverage | `demo.test.ts` | `workflow.test.ts` with `fake-bob` |
| Real end-to-end | Not applicable | **Manual only**: the live chain with real Bob and QSE has been run end-to-end once (README, "Honest limitations") |

## 11.5 Acceptance criteria

| ID | Requirement | Acceptance criterion (Given/When/Then) | Verified by |
|---|---|---|---|
| AC-01 | FR-01 | Given no session cookie, when any `/api` route except login is called, then the response is 401 `unauthorized` | `security.test.ts` |
| AC-02 | FR-01 | Given a valid session, when a POST is sent without `X-CSRF-Token`, then 403 `csrf_invalid` | `security.test.ts` |
| AC-03 | FR-02 | Given a saved Bob key, when `GET /api/bob/status` is called, then the body contains only `apiKeyHint` (a masked hint) and no key material | `security.test.ts` |
| AC-04 | FR-03 | Given Bob not connected, when `POST /api/executions` is called, then 4xx with a precondition code and no execution is created | `workflow.test.ts` (start preconditions) |
| AC-05 | FR-03 | Given a valid chain, when an execution is started, then it finishes `completed` with a `reportId` | `workflow.test.ts` |
| AC-06 | FR-04 | Given `MAX_CONCURRENT_EXECUTIONS` active runs, when another is started, then it is `queued` | **Not covered** (see 11.6) |
| AC-07 | FR-05 | Given a running execution, when the stream is read with `Last-Event-ID`, then only newer events are delivered | **Not covered** (no SSE protocol test) |
| AC-08 | FR-06 | Given a finished execution, when `GET /api/executions/:id` and `/logs` are called, then steps and logs are returned | `workflow.test.ts` |
| AC-09 | FR-07 | Given Bob wrote no report file, when the run ends, then the report uses the final answer and `source=headless-bob-output` | `workflow.test.ts` (fallback) |
| AC-10 | FR-08 | Given `STREAM_MODE=mock`, when a run completes, then all rows have `mock=true` and exports are labelled DEMO | `demo.test.ts` |
| AC-11 | FR-08 | Given `STREAM_MODE=realtime`, when a run is started without Bob, then it fails and never serves demo data | `demo.test.ts` |
| AC-12 | FR-09 | Given a running execution, when cancel is called, then the final status is `cancelled` | `workflow.test.ts`, `demo.test.ts` |
| AC-13 | FR-11 | Given an admin, when `POST /api/admin/rotate-secrets` is called, then stored secrets are re-encrypted with the active key and still decrypt | `security.test.ts` (key rotation) |
| AC-14 | FR-12 | Given step events, when the Workspace renders, then twin nodes reflect only those statuses | `PipelineTwin.test.tsx` |
| AC-15 | NFR-02 | Given an endpoint on a blocked address class, when Bob connect is called, then it is refused | `security.test.ts`, `utils.test.ts` |
| AC-16 | NFR-03 | Given a repository containing a symlink that escapes the workspace, when cloned, then it is rejected | `workflow.test.ts` |
| AC-17 | NFR-05 | Given missing `SESSION_SECRET` or `ENCRYPTION_KEY`, when the config loads, then startup fails | `utils.test.ts` |
| AC-18 | FR-10 | Given executions marked running at shutdown, when the service starts, then they are `failed` | **Not covered** by a dedicated test |

## 11.6 Test gaps

| Gap | Impact | Priority |
|---|---|---|
| No browser E2E tests | UI regressions across routing and SSE are caught only manually | High |
| No SSE protocol test (resume, heartbeat, terminal event) | AC-07 unverified | High |
| No test for queueing beyond `MAX_CONCURRENT_EXECUTIONS` | AC-06 unverified | Medium |
| No restart-recovery test | AC-18 unverified | Medium |
| No pagination or sort test for `/executions` | Query bugs undetected | Low |
| No accessibility test (axe) | Keyboard and contrast regressions undetected | Medium |
| No coverage tooling | Coverage unknown | Low |
| Real Headless Bob and QSE are never exercised in CI | Contract drift undetected | High (needs an environment) |
