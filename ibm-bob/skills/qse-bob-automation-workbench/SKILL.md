---
name: qse-bob-automation-workbench
description: Recreates the QSE Automation Workbench (React/Carbon UI, Express/SQLite backend, Headless Bob + QSE CLI integration, mock demo mode, Pipeline digital twin) from the bundled SPEC.md using ordered build guides. Use when asked to "recreate", "rebuild", "clone", "scaffold" or "audit" the QSE workbench, or to plan which build guide to read next.
---

# QSE Workbench: orchestrator

Recreates the QSE Automation Workbench functionally and visually from `references/SPEC.md`. This skill decides the build mode, fixes the build order, owns the feature coverage matrix and defines "done". Every build guide in `guides/` is read from here. This is the only `SKILL.md` in the pack.

## When to use

- The user wants to rebuild or clone the QSE Automation Workbench, or any part of it.
- You need to know which guide in `guides/` to read next, or whether the build is finished.
- Start here even if the user names a single feature: the matrix below shows which guides it touches.

## Inputs you need

1. An empty or new target project directory (all paths below are relative to it).
2. The bundled references in this skill's `references/` folder (guide-specific extracts are linked from each guide):
   - [SPEC.md](references/SPEC.md): the as-built specification (15 sections). Cite sections as "SPEC 6.2".
   - [requirements.md](references/requirements.md): objectives, FR-01..FR-12, NFR-01..NFR-08, out of scope.
   - [production-readiness.md](references/production-readiness.md): readiness checklist and go/no-go blockers.
   - [gap-register.md](references/gap-register.md): gaps G1..G21 with owner guides.
   - [glossary.md](references/glossary.md): terms.
3. The user's answers to the two questions in Step 1.
4. Node.js >= 22.13 (the backend uses built-in `node:sqlite`), `git`, and Docker or Podman for the deployment phase.

## Requirements covered

| ID | Owner here | Acceptance test |
|---|---|---|
| NFR-08 | this file | No document, comment or UI text in the new project states a latency, throughput or capacity figure. Say "none measured". |

**NFR-08: no performance figures were measured; do not invent any.**

All other FR/NFR items are owned by the guides in the ownership table below; this file checks that each owner reported evidence.

## Steps

### Step 1. Ask two questions and record the answers

1. **Build mode:** "faithful clone" (reproduce SPEC as built, including documented gaps) or "clone + fixes" (apply the P1/P2 fixes in SPEC 14).
2. **Demo recording:** is a real `recorded-run.json` available to copy, or should the `guides/mock-mode.md` guide generate a clearly labelled synthetic one? (The original recording names a real repository; do not copy it unless the user confirms they may share it.)

Write `BUILD_DECISIONS.md` in the new project root:

```markdown
# Build decisions
Mode: faithful clone | clone + fixes
Demo recording: copied | synthetic

| Gap | Decision (fix | keep as built) | Notes |
|---|---|---|
| G1 | ... | ... |
... one row for every G1..G21 ...
```

Default for "faithful clone": every gap is `keep as built`. Default for "clone + fixes": fix every gap whose priority in [gap-register.md](references/gap-register.md) is P1 or P2, and keep P3 as built.

### Step 2. Follow the build order

| Phase | Read guide | Exit gate (all must pass) | Verify against SPEC |
|---|---|---|---|
| 1 | [`foundation`](guides/foundation.md) | `cd backend && npm run typecheck`; `cd frontend && npm run typecheck`; backend refuses to start with a missing secret | SPEC 2, 10.5 |
| 2 | [`backend-core`](guides/backend-core.md) | backend `typecheck`, `test`, `build`; every route in SPEC 6.2 answers with the right status | SPEC 6, 7, 8, 9 |
| 3 | [`integrations`](guides/integrations.md) | backend `typecheck`, `test`; SSRF, symlink and licence tests pass | SPEC 4.1-4.3, 6.4, 6.6 |
| 4 | [`execution-engine`](guides/execution-engine.md) | backend `test` incl. the full connect-clone-validate-execute-report-history flow | SPEC 4.4-4.8, 5, 6.5 |
| 5 | [`mock-mode`](guides/mock-mode.md) | mock tests pass; realtime never serves demo data | SPEC 4.5, 10.1 |
| 6 | [`frontend-ui`](guides/frontend-ui.md) | frontend `typecheck`, `test`, `build` | SPEC 3.1, 3.2, 3.5, 3.6 |
| 7 | [`digital-twin`](guides/digital-twin.md) | `PipelineTwin` tests pass; page does not blank | SPEC 3.4 |
| 8 | [`feature-pages`](guides/feature-pages.md) | `pages.test.tsx` equivalents pass; each page matches SPEC 3.3 | SPEC 3.3, 4 |
| 9 | [`deployment`](guides/deployment.md) | `scripts/deploy_local.sh --check` and `scripts/deploy_psh.sh --check` exit 0; compose builds | SPEC 10, 12 |
| 10 | [`testing`](guides/testing.md) | both packages: `npm run typecheck && npm test && npm run build && npm audit --omit=dev` | SPEC 11 |
| 11 | [`spec-audit`](guides/spec-audit.md) | audit table has no FAIL | SPEC 13, 15 |

Do not start a phase until the previous exit gate passes. Never mark a gate passed without running the command.

### Step 3. Maintain the feature coverage matrix

Copy this table to `BUILD_DECISIONS.md` and fill the last two columns only after the exit gate for that row passes. Record evidence (command output summary or file path) in "Evidence".

| Feature | Backend guide | Frontend guide | Test guide | FR/NFR ids | AC ids | Done? | Evidence |
|---|---|---|---|---|---|---|---|
| Auth | backend-core | feature-pages | testing | FR-01, NFR-01 | AC-01, AC-02 | [ ] | |
| Bob connection | integrations | feature-pages | testing | FR-02, NFR-02 | AC-03, AC-15 | [ ] | |
| GitHub repository | integrations | feature-pages | testing | FR-02, NFR-03 | AC-16 | [ ] | |
| QSE CLI | integrations | feature-pages | testing | NFR-03 | AC-04 | [ ] | |
| Prompt management | execution-engine | feature-pages | testing | FR-03 | AC-04 | [ ] | |
| Execution orchestration | execution-engine | feature-pages | testing | FR-03, FR-04, FR-06, FR-09, FR-10 | AC-04, AC-05, AC-08, AC-12, AC-18 | [ ] | |
| Real-time monitoring | execution-engine | frontend-ui, feature-pages | testing | FR-05 | AC-07 | [ ] | |
| Pipeline digital twin | none (uses step data) | digital-twin | testing | FR-12 | AC-14 | [ ] | |
| Report generation | execution-engine | feature-pages | testing | FR-07 | AC-09 | [ ] | |
| History | execution-engine | feature-pages | testing | FR-06 | AC-08 | [ ] | |
| Settings | backend-core | feature-pages | testing | FR-11, NFR-01 | AC-13 | [ ] | |
| Mock mode | mock-mode | feature-pages | testing | FR-08 | AC-10, AC-11 | [ ] | |
| Observability | backend-core | none | testing | NFR-04 | probes test | [ ] | |
| Deployment | deployment | none | testing | NFR-05, NFR-07 | AC-17 | [ ] | |

### Step 4. Requirements ownership

Each owner guide lists these in its "Requirements covered" section and reports evidence in its exit gate.

| Requirement | Owner guide |
|---|---|
| FR-01 auth on every /api route | backend-core |
| FR-02 secrets encrypted, never returned | backend-core (store), integrations (Bob key, repo tokens) |
| FR-03 start preconditions | execution-engine |
| FR-04 concurrency + queue | execution-engine |
| FR-05 SSE stream + resume | execution-engine (server), feature-pages (client use) |
| FR-06 persistence of executions/steps/logs/report | execution-engine |
| FR-07 honest report source | execution-engine |
| FR-08 DEMO labelling | mock-mode |
| FR-09 cancel | execution-engine |
| FR-10 restart recovery | execution-engine |
| FR-11 secret rotation | backend-core |
| FR-12 digital twin from real events only | digital-twin |
| NFR-01 no secrets in logs/responses/URLs/storage | backend-core |
| NFR-02 SSRF-guarded outbound HTTP, no redirects | integrations |
| NFR-03 no shell, never execute repo content | integrations |
| NFR-04 graceful shutdown (25 s hard stop) | backend-core |
| NFR-05 refuse to start on invalid config | foundation |
| NFR-06 Carbon g100 + IBM Plex | frontend-ui |
| NFR-07 single-node by design | deployment |
| NFR-08 no performance claims | this file |

### Step 5. Gap ownership

| Gap | Summary | Owner guide(s) |
|---|---|---|
| G1 | Prompt-limit mismatch (zod 20000 / `MAX_PROMPT_CHARS` 8000 / textarea 20000) | backend-core, execution-engine, feature-pages |
| G2 | Twin placeholder has 8 steps; backend has 9; `SHORT` lacks `completed` | digital-twin |
| G3 | `--cds-*` variables undefined (`.cds--g100` never applied) | frontend-ui, digital-twin |
| G4 | No ErrorBoundary | frontend-ui, digital-twin |
| G5 | UI does not hide actions by role | feature-pages |
| G6 | No user-management API/UI | backend-core, feature-pages |
| G7 | No retention/cleanup, no delete-execution API | execution-engine, deployment |
| G8 | SQLite single node; in-memory queue, SSE bus, limits | execution-engine, deployment |
| G9 | Reports page only lists the newest 100 executions | feature-pages |
| G10 | Fixed report tabs; no CBOM/QSE JSON parsing | execution-engine, feature-pages |
| G11 | QSE `versionArgs` not editable in UI | integrations, feature-pages |
| G12 | Prompt templates hard-coded | execution-engine, feature-pages |
| G13 | `/settings` version hard-coded "1.0.0" | backend-core, feature-pages |
| G14 | Bob save toast understates the auto-test | feature-pages |
| G15 | No SSE/pagination/E2E/a11y tests | testing |
| G16 | `STREAM_MODE` defaults to `mock`, including compose | foundation, mock-mode, deployment |
| G17 | Docs mention Postgres that does not exist | deployment, this file |
| G18 | ACP adapter has no file API | integrations |
| G19 | Prompt stored verbatim, not redacted | execution-engine |
| G20 | Headless Bob run timeout default 5 minutes | integrations, deployment |
| G21 | No metrics/tracing/alerts, automated backup or versioned migrations | backend-core, deployment |

### Step 6. Status vocabulary

Use exactly: **Implemented**, **Partial**, **Mocked**, **Planned** (legend at the top of SPEC.md). Never describe a Partial or Planned item as Implemented. Never present `STREAM_MODE=mock` behaviour as a real integration.

## Verification (exit gate)

The build is done only when all of these hold:

1. Every row of the feature coverage matrix is ticked with evidence.
2. Every G1..G21 has a decision in `BUILD_DECISIONS.md`.
3. The go/no-go list in [production-readiness.md](references/production-readiness.md) has been reviewed with the user.
4. `spec-audit` reports no FAIL.
5. NFR-08: nothing in the new project claims a performance figure.
6. G17: the new project's docs do not mention a Postgres container or service that does not exist.

## Pitfalls

- Starting with the UI. The backend contract (SPEC 6) must exist first or the UI will be wired to guesses.
- Copying `backend/demo-data/recorded-run.json` from the original project without the user's consent.
- Reading or committing `.env` files. Use `.env.example` only.
- Treating SPEC "Planned" rows as work to do in a faithful clone.
- Letting `references/SPEC.md` drift from the source SPEC. It must stay byte-identical.

## Known gaps that apply

- G17 (docs mention Postgres that does not exist). User decision: <fix | keep as built>
- G1..G21 are all recorded in `BUILD_DECISIONS.md`; see [gap-register.md](references/gap-register.md).

## SPEC references

SPEC 1 (objectives, requirements), SPEC 12 (readiness), SPEC 13 (traceability), SPEC 14 (gaps), SPEC 15 (completeness checklist). Full copy: [SPEC.md](references/SPEC.md).
