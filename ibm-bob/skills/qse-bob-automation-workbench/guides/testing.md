# Testing guide

## When to use

Alongside every build phase (write tests as each guide finishes) and as phase 10 for the full gate. Use also to decide which acceptance criteria are covered and which are known gaps.

## Inputs you need

- [acceptance-criteria.md](../references/acceptance-criteria.md): SPEC 11.1-11.6 verbatim (inventory, infrastructure, commands, mock vs realtime, AC-01..AC-18, gaps).
- `BUILD_DECISIONS.md` (G15).
- The implemented backend and frontend.

## Requirements covered

| ID | Requirement | Acceptance test |
|---|---|---|
| (all FR/NFR evidence) | Every FR and NFR has at least a statement of evidence | The coverage table below has an entry for each AC, and uncovered ACs are listed explicitly (AC-06, AC-07, AC-18 in the reference). |
| NFR-01..NFR-03 | Security properties are tested | Redaction, SSRF, symlink and no-shell tests exist and pass. |

## Steps

### 1. Backend test setup

- Vitest 5.1.0: `environment: node`, include `tests/**/*.test.ts`, test and hook timeouts 30 s, `pool: forks` (`backend/vitest.config.ts`). supertest 7.3.2.
- `backend/tests/helpers/harness.ts`: builds the Express app against a temporary `DATA_DIR`, a test config and (for workflow tests) the fake Bob; exposes helpers to log in and get the CSRF token.
- `backend/tests/helpers/fake-bob.ts`: an in-process HTTP server implementing the Headless Bob **REST-threads contract** (healthz, capabilities, threads, messages, run events, run state, cancel, files, download). It is a **test double, not a product mock mode**; production code must contain no mock adapter (a security test asserts it).

### 2. Backend suites to write (reference counts: 110 tests in 7 files, all passing)

| File | Tests | Covers |
|---|---|---|
| `tests/integration/security.test.ts` | 30 | auth/CSRF, roles, secure headers, rate limit, probes (`/healthz`, `/readyz`); Bob connection (11: SSRF, allow-list, key rotation, removed mock adapter); GitHub (5); QSE (6) |
| `tests/integration/workflow.test.ts` | 6 | connect -> clone -> validate -> execute -> report -> history; fallback to the final answer; Bob failure; cancel; start preconditions; symlink-escape clone |
| `tests/integration/demo.test.ts` | 10 | mock replay, default mock, validation still applies, setup required, cancel mid-replay, missing recording fails fast, realtime never serves demo data (4) |
| `tests/unit/utils.test.ts` | 15 | Bob event helpers, SSRF classification, paths, redaction, SecretBox, passwords, safe-exec, config validation (4) |
| `tests/unit/report.test.ts` | 7 | report section parsing, PDF, prompt builder |
| `tests/unit/qse-validator.test.ts` | 6 | `extractVersion`, `validateQseCli` licence handling |
| `tests/unit/github.test.ts` | 3 | URL and branch parsing |

Add the observability probe tests explicitly: `/healthz` returns `{"status":"ok"}`; `/readyz` returns the keys `database`, `workspace`, `accepting` and 503 `not_ready` when not accepting; responses carry `x-request-id`.

### 3. Frontend test setup

- Vitest through `frontend/vite.config.ts`: jsdom, globals, `css: false`. `frontend/src/test/setup.ts`: jest-dom matchers plus `matchMedia`, `ResizeObserver`, `scrollIntoView` shims. `frontend/src/test/utils.tsx`: render helper with `QueryClientProvider` and `MemoryRouter`.
- Suites (36 tests in 6 files): `pages/pages.test.tsx` (10), `components/PipelineTwin.test.tsx` (5), `services/api.test.ts` (5), `stores/stores.test.ts` (4), `services/format.test.ts` (4), `components/components.test.tsx` (3 declared; `it.each` over `StatusTag` expands it).
- Digital twin tests (5) and the no-throw regression test belong to `digital-twin.md`; run them here.

### 4. Acceptance criteria coverage

| AC | Requirement | Verified by | Reference status |
|---|---|---|---|
| AC-01 | FR-01 | `security.test.ts` | covered |
| AC-02 | FR-01 | `security.test.ts` | covered |
| AC-03 | FR-02 | `security.test.ts` | covered |
| AC-04 | FR-03 | `workflow.test.ts` | covered |
| AC-05 | FR-03 | `workflow.test.ts` | covered |
| AC-06 | FR-04 | none | **not covered** |
| AC-07 | FR-05 | none | **not covered** |
| AC-08 | FR-06 | `workflow.test.ts` | covered |
| AC-09 | FR-07 | `workflow.test.ts` | covered |
| AC-10 | FR-08 | `demo.test.ts` | covered |
| AC-11 | FR-08 | `demo.test.ts` | covered |
| AC-12 | FR-09 | `workflow.test.ts`, `demo.test.ts` | covered |
| AC-13 | FR-11 | `security.test.ts` | covered |
| AC-14 | FR-12 | `PipelineTwin.test.tsx` | covered |
| AC-15 | NFR-02 | `security.test.ts`, `utils.test.ts` | covered |
| AC-16 | NFR-03 | `workflow.test.ts` | covered |
| AC-17 | NFR-05 | `utils.test.ts` | covered |
| AC-18 | FR-10 | none | **not covered** |

Full Given/When/Then wording is in [acceptance-criteria.md](../references/acceptance-criteria.md). A faithful clone may leave AC-06, AC-07 and AC-18 uncovered but must list them in `BUILD_DECISIONS.md`; a "clone + fixes" build (G15) should write them.

### 5. Mock vs realtime testing (SPEC 11.4)

Mock: no Bob/GitHub/QSE needed, separate DB file, `mock=true`, `-DEMO` filenames, `demo.test.ts`. Realtime: `workflow.test.ts` with the fake Bob; real end-to-end with real Bob and QSE is **manual only**.

### 6. Quality gate

```bash
cd backend  && npm run typecheck && npm test && npm run build && npm audit --omit=dev
cd frontend && npm run typecheck && npm test && npm run build && npm audit --omit=dev
./scripts/deploy_local.sh --check
./scripts/deploy_psh.sh   --check
```

A change is acceptable only when every command exits 0.

### 7. Documented test gaps (G15)

No browser E2E, no SSE protocol test (resume, heartbeat, terminal event), no queueing-beyond-limit test, no restart-recovery test, no pagination/sort test, no accessibility (axe) test, no coverage tooling, real Bob/QSE never exercised in CI.

## Verification (exit gate)

- The quality gate above passes. Record test counts per package in `BUILD_DECISIONS.md` (do not assert reference counts if yours differ).
- Every AC in the table has either a test name or an explicit "not covered" note.
- NFR-01..NFR-03 tests exist: token redaction in logs, blocked-IP classes, escaping symlink, `shell:false` (spawn arguments asserted).

## Pitfalls

- Turning the fake Bob into a production adapter.
- Tests that call the real network, git remotes or the real QSE CLI.
- Sharing one database across tests (use a temp `DATA_DIR` each).
- Counting `it.each` rows incorrectly when comparing to the reference numbers.

## Known gaps that apply

- G15: no SSE/pagination/E2E/a11y tests. User decision: <fix | keep as built>

## SPEC references

SPEC 11.1, SPEC 11.2, SPEC 11.3, SPEC 11.4, SPEC 11.5, SPEC 11.6. Detail: [acceptance-criteria.md](../references/acceptance-criteria.md).
