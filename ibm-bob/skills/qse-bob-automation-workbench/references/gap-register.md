# Gap register with owner guides

> Extracted verbatim from `SPEC.md` (section 14; the last column is added by the QSE workbench pack). Do not edit here; edit SPEC.md and re-extract.

## Gaps

Classification: **Defect** (behaves wrongly), **Inconsistency**, **Missing** (not built), **Test gap**, **Operational**. Priority: P1 fix before production, P2 soon, P3 backlog.

| # | Gap | Classification | Impact | Dependencies | Priority | Files | Owner guide(s) |
|---|---|---|---|---|---|---|---|
| G1 | Prompt limit differs by layer: zod 1–20000, orchestrator `MAX_PROMPT_CHARS` (8000, max 15000), Workspace textarea falls back to 20000 before settings load | Inconsistency | User sees a late `prompt_too_long` 422 | none | P2 | `backend/src/models/schemas.ts`, `backend/src/orchestrators/execution.orchestrator.ts`, `backend/src/config/env.ts`, `frontend/src/pages/WorkspacePage.tsx` | backend-core, execution-engine, feature-pages |
| G2 | Twin placeholder `DEFAULT_STEPS` has 8 steps; backend defines 9 (`completed`); `SHORT` has no label for `completed` | Inconsistency | Cosmetic mismatch before first data | none | P3 | `frontend/src/components/PipelineTwin.tsx`, `backend/src/orchestrators/steps.ts` | digital-twin |
| G3 | `--cds-*` CSS variables are undefined because `.cds--g100` is never applied; `.card`, `.stat`, success icon fills rely on them. The twin avoids it with `--twin-*` | Defect (styling) | Some elements fall back to default colours | Carbon theme wiring | P2 | `frontend/src/styles/index.scss`, `frontend/src/main.tsx` | frontend-ui, digital-twin |
| G4 | No `ErrorBoundary` | Missing | A render error blanks the page (the earlier twin blank-render bug is an example) | none | P2 | `frontend/src/App.tsx` | frontend-ui, digital-twin |
| G5 | UI does not hide actions by role; it relies on server 403 | Missing | Viewer sees buttons that fail | session store has `role` | P3 | all `frontend/src/pages/*Page.tsx` | feature-pages |
| G6 | No user-management API or UI; only the bootstrap admin | Missing | Single shared admin | schema, routes, Settings UI | P2 | `backend/src/routes/index.ts`, `backend/src/repositories/auth.repository.ts`, `frontend/src/pages/SettingsPage.tsx` | backend-core, feature-pages |
| G7 | No retention or cleanup of executions, logs, reports, workspaces; no delete-execution API | Missing | Unbounded disk growth | G6 for authorisation policy | P1 | `backend/src/repositories/execution.repository.ts`, `backend/src/services/repository.service.ts` | execution-engine, deployment |
| G8 | SQLite single node; in-memory queue, SSE bus and rate limits; queued executions are failed after restart | Operational | No HA or scale-out | external DB, queue, shared limiter | P2 (target architecture) | `backend/src/db/database.ts`, `backend/src/orchestrators/execution.orchestrator.ts` | execution-engine, deployment |
| G9 | Reports page only considers the newest 100 executions | Defect | Older reports not listed | pagination in UI | P3 | `frontend/src/pages/ReportsPage.tsx` | feature-pages |
| G10 | Report tabs are fixed; no Cryptographic Findings or Risk Categorization view; backend does not parse CBOM or QSE JSON | Missing | Findings are shown only as Bob's text | Parser for the QSE JSON artifacts | P2 | `backend/src/services/report.service.ts`, `frontend/src/pages/ReportViewPage.tsx` | execution-engine, feature-pages |
| G11 | QSE `versionArgs` not editable in the UI | Missing | Tools using a different version flag need API calls | none | P3 | `frontend/src/pages/QsePage.tsx` | integrations, feature-pages |
| G12 | Prompt templates are hard-coded | Missing | Cannot add templates without code change | storage and CRUD | P3 | `backend/src/orchestrators/prompt-builder.ts` | execution-engine, feature-pages |
| G13 | `/settings` version is hard-coded "1.0.0" | Inconsistency | Wrong version after upgrades | build metadata | P3 | `backend/src/controllers/index.ts` | backend-core, feature-pages |
| G14 | Save toast on Bob page says "Run Test Connection to verify" although save already tests | Inconsistency | Misleading text | none | P3 | `frontend/src/pages/BobConnectionPage.tsx` | feature-pages |
| G15 | No SSE protocol, pagination/sort, E2E or accessibility tests | Test gap | Regressions undetected (see 11.6) | test environment | P1 for SSE and E2E | `backend/tests/`, `frontend/src/` | testing |
| G16 | Default `STREAM_MODE` is `mock`, including in compose | Operational | A fresh install shows the demo, which may be mistaken for a real run | none | P2 (mitigated by DEMO labels) | `backend/src/config/env.ts`, `deployment/docker-compose.yml` | foundation, mock-mode, deployment |
| G17 | `docs/ARCHITECTURE.md` mentions Postgres as a future adapter, but no Postgres exists | Inconsistency | Misleading docs | none | P3 | `docs/ARCHITECTURE.md` | deployment, recreate |
| G18 | ACP adapter has no file API, so no artifact or report-file retrieval | Missing (limitation of ACP) | Reports come only from final answer on ACP | upstream Bob capability | P3 | `backend/src/integrations/headless-bob/acp.adapter.ts` | integrations |
| G19 | Prompt text is stored verbatim and not redacted | Operational | A secret typed in a prompt is stored | decision on redaction policy | P2 | `backend/src/repositories/execution.repository.ts` | execution-engine |
| G20 | Real analysis requires an operator-run Headless Bob and QSE CLI; the live chain has been run end-to-end once; Headless Bob's own run timeout defaults to 5 minutes | Operational | Long scans may time out on the Bob side | Bob-side configuration | P2 | `README.md`, `deployment/docker-compose.yml` | integrations, deployment |
| G21 | No metrics, tracing or alerting; no automated backup; no versioned migrations | Missing | Weak operability | monitoring stack | P2 | `backend/src/utils/logger.ts`, `backend/src/db/database.ts` | backend-core, deployment |

