# Feature pages guide

## When to use

Last frontend phase, after `frontend-ui.md` and `digital-twin.md`. One section per page; build them in the order listed.

## Inputs you need

- [pages.md](../references/pages.md): SPEC 3.3 (every page's layout, states, texts).
- [feature-specs.md](../references/feature-specs.md): SPEC 4.0-4.9 (Journey, Inputs, UI transitions, Failure rows).
- Shared plumbing from `frontend-ui.md`; `PipelineTwin` from `digital-twin.md`.
- `BUILD_DECISIONS.md` (G1, G5, G6, G9, G10, G11, G12, G13, G14).

## Requirements covered

| ID | Requirement | Acceptance test |
|---|---|---|
| FR-05 (client use) | Client streams execution state and logs over SSE and resumes | The Workspace page uses `useExecutionStream`; after an error it reconnects after 2 s with the last log id unless the execution is terminal (AC-07). |
| UI side of FR-01 | Unauthenticated users never see a page | Visiting any route without a session redirects to `/login` (AC-01). |
| UI side of FR-03, FR-08, FR-09, FR-11 | Pre-flight list, DEMO tags, Cancel, Re-encrypt button | Covered by the page checks below. |

## Steps

Common rules for every page: wrap in `PageHeader`; use TanStack Query hooks (no ad-hoc fetch); surface errors with `useNotify().error` or an `InlineNotification`; skeleton while loading; `Tile` for empty states; **do not hide actions by role** (G5): the server returns 403 and the UI shows its message as a toast. Forms use Carbon inputs with the ids listed.

### 1. Login `/login` (SPEC 3.3.1, 4.0)

- API: `POST /api/auth/login` -> `{user, csrfToken}`; `setSession`.
- Fields `TextInput#login-username` (autoFocus, `autoComplete=username`), `PasswordInput#login-password`. Submit disabled while busy or empty; `InlineLoading "Signing in"`. Error `InlineNotification` title "Sign-in failed". On success clear the password and navigate to `state.from` or `/`. If already signed in, redirect.

### 2. Overview `/` (SPEC 3.3.2)

- Hooks: `useBob`, `useRepos`, `useQse`, `useExecutions({page:1,pageSize:5,sort:'createdAt',direction:'desc'})`.
- Four `Stat` tiles (Headless Bob, Repository, QSE CLI, Executions) in `.grid-4`; `.grid-2` with "Getting started" (4 steps with done check and Open buttons) and "Recent executions" (5 newest; link to `/reports/:id` if completed with a report, else `/workspace/:id`; error "Could not load executions").

### 3. Bob Connection `/bob` (SPEC 3.3.3, 4.1)

- API: `GET /bob/status`, `POST /bob/connect`, `POST /bob/test-connection`, `POST /bob/disconnect`. Poll `useBob` every 1500 ms while `connecting`.
- Fields: `TextInput#bob-endpoint` (placeholder `http://headless-bob:3000`), `PasswordInput#bob-api-key` (`autoComplete=new-password`; placeholder `Stored: ••••xxxx - leave blank to keep` when a hint exists; disabled for auth mode `none`), protocol toggle revealing `Dropdown#bob-adapter`, `TextInput#bob-base`, `Dropdown#bob-auth`, and `TextInput#bob-header` (only for `header`).
- Buttons: Save configuration (needs endpoint, or demo mode), Test connection, Disconnect (`danger--tertiary`).
- Right card status (StatusTag forced to `connecting` while pending), error notifications for `auth_failed`/`connection_failed`; full-width Supported capabilities card.
- Toasts: "Configuration saved", "Connected to Headless Bob", "Connection test failed", "Disconnected".
- **G14:** the reference toast says "Run Test Connection to verify" although save already tests. Keep as built or reword to "Saved and tested".

### 4. Repository `/repository` (SPEC 3.3.4, 4.2)

- API: `GET /repositories`, `POST /repositories/validate`, `POST /repositories/clone`, `POST /repositories/:id/reclone`, `DELETE /repositories/:id`. Poll every 1000 ms while any repo is `cloning`/`validating`.
- Fields `TextInput#repo-url` (placeholder `https://github.com/owner/repository`; editing clears validation), `TextInput#repo-branch` (default `main`), `PasswordInput#repo-token` (optional). Form seeded from the active/first repository once.
- Buttons Validate, Clone, Re-clone, Remove workspace (`danger--ghost`); all disabled while a mutation is pending or repo is cloning. Right card: details, failure notification "Clone failed", `role="log"` clone progress (last 30 lines).

### 5. QSE `/qse` (SPEC 3.3.5, 4.3)

- API: `GET /qse/discover` (auto mode), `POST /qse/configure`, `POST /qse/validate`, `GET /qse/status`.
- `RadioButtonGroup` Automatic/Manual; manual `TextInput#qse-path` (placeholder `/opt/qse-cli/qse-cli`); automatic `StructuredListWrapper selection` with Usable tags and the first usable pre-selected. Buttons "Use selected and validate" / "Save and validate" and "Revalidate".
- Warning "Not reachable from Headless Bob" when valid but outside shared mounts. **G11:** `versionArgs` are not editable in the UI; keep as built or add an input matching `^[A-Za-z0-9._=-]{1,40}$`, max 4.

### 6. Workspace `/workspace`, `/workspace/:executionId` (SPEC 3.3.6, 4.4, 4.5, 4.6)

Cards in order: Execution context; prompt card; Execution controls; **Pipeline digital twin** (`<PipelineTwin execution bob repo qse streamMode/>`); Execution monitor; or the empty `Tile`.

- Prompt: `Select#prompt-template` (4 templates: Full quantum-safe assessment, Cryptographic inventory only, Remediation plan, Dependency review; G12 hard-coded), `Select#prompt-history` (25 distinct), `TextArea#prompt` (rows 10, counter, `maxCount` = `settings.limits.maxPromptChars`, falling back to 20000 before settings load: **G1**), Reset to example, Clear. Draft in `sessionStorage` `qse.promptDraft`; textarea disabled while active.
- Pre-flight list: Bob connected; repository cloned; QSE validated **and** reachable from Bob; prompt provided and within limit; each with a **Fix** link. Start execution enabled only when all pass and nothing is active; Cancel enabled only while active and not `cancelling`; Clear workspace opens a danger modal ("This clears the prompt, the current execution view and deletes the cloned repository from the isolated workspace. Execution history and reports are kept.").
- Starting navigates (replace) to `/workspace/:id` and stores `qse.activeExec`/`qse.activeRepo`.
- Monitor: `useExecutionStream(id)` merged over `useExecution` (poll 4 s while active); logs from the stream when it holds at least as many lines as the REST fallback `GET /executions/:id/logs`. `KeyValues` (ID, status, started, elapsed ticking each second, current activity, "N of M completed", live-updates state Connected / Reconnecting... / Not streaming); two step lists with `Tag` blue "backend" and purple "headless-bob"; note "Headless Bob does not report percentage progress, so none is shown."; `LogViewer`; **View report** when completed with a report.

### 7. History `/history` (SPEC 3.3.7, 4.8)

- API: `GET /executions` with `search`, `status`, `sort`, `direction`, `page`, `pageSize`. `DataTable` titled "Executions" ("N total"); `Search#history-search` (debounced 300 ms, resets page); `Dropdown#history-status`; sortable columns Repository, Date, Duration, Status; page sizes 10/25/50; magenta `DEMO` tag for mock runs; actions View execution / View report (disabled without a report). Auto-refresh 3 s while any row is active. States: skeleton, empty row "No executions match...", error "Could not load history".

### 8. Reports `/reports` and Report view `/reports/:executionId` (SPEC 3.3.8, 3.3.9, 4.7)

- Reports list: filter the newest 100 executions client-side for completed with `reportId` (**G9**: older ones never show; keep or add server-side filtering/pagination). Empty `Tile` "No reports yet. A report is available after an execution finishes."
- Report view: `GET /executions/:id/report` (no retry); 404 -> warning "No report available". Actions Copy report, Markdown, PDF, JSON results (anchor downloads to `/api/reports/:id/download?format=`), View execution logs. Source tag: green "Report file written by Headless Bob", blue "Final answer returned by Headless Bob (no report file was produced)", red "Headless Bob returned no report content".
- Tabs (contained): Executive Summary (`summary`+`conclusion`, falls back to `bobMarkdown`), Findings (`findings`+`other`), Recommendations, Execution Details, Artifacts (download or "Not retrieved" tag; export link), Logs (lazy fetch when tab 5 opens; note "Secrets are redacted before logs are stored."). **G10:** tabs are fixed; there is no Cryptographic Findings or Risk Categorization tab. Do not invent one.

### 9. Settings `/settings` (SPEC 3.3.10, 4.9)

- API: `GET /api/settings` (read-only `KeyValues`: version, execution strategy, prompt limit, execution timeout, concurrent executions, allowed Git hosts, session lifetime/idle, encryption key id, stream mode tag magenta "mock - demo, recorded data" or green "realtime - live Headless Bob"; **G13** version hard-coded "1.0.0"), shared-mount list or `Tile` "No shared mounts configured."
- Change password: `POST /api/auth/password`; three `PasswordInput`s (current; new, helper "At least 12 characters."; confirm, error "Passwords do not match."). Submit enabled only when current is set, new >= 12 and matches. Success: server revokes all sessions; clear session and query cache, navigate to `/login`, toast.
- Credential rotation: admin sees instructions and **Re-encrypt stored secrets** opening a confirmation modal that calls `POST /api/admin/rotate-secrets`; others see info "Administrator only". Failure toast "Rotation failed". **G6:** no user-management UI.

## Verification (exit gate)

```bash
cd frontend && npm run typecheck && npm test && npm run build
```

Port the 10 tests in `pages.test.tsx`: LoginPage (2), BobConnectionPage (4), WorkspacePage pre-flight (2) plus Overview/History/Settings rendering. Add manual checks:

- FR-05: open a running execution, kill the backend, confirm "Reconnecting...", restart, confirm resume without duplicate log lines.
- FR-08: in mock mode, header tag, `DEMO` tags and `-DEMO` download names are visible.
- FR-09: Cancel is disabled when idle or cancelling.
- FR-11: Re-encrypt button only actionable for admin (server enforces).
- Each page's ids, copy and states match [pages.md](../references/pages.md).

## Pitfalls

- Fetching directly instead of via hooks (loses polling and invalidation).
- Hiding buttons by role (the reference does not; server 403 is the control).
- Showing a progress bar for the Bob phase.
- Rendering report Markdown with raw HTML.
- Forgetting to clear the query cache on logout/401.

## Known gaps that apply

- G1: prompt limit fallback 20000 before settings load. User decision: <fix | keep as built>
- G5: UI does not hide actions by role. User decision: <fix | keep as built>
- G6: no user-management UI. User decision: <fix | keep as built>
- G9: Reports page only newest 100 executions. User decision: <fix | keep as built>
- G10: fixed report tabs, no CBOM/QSE JSON view. User decision: <fix | keep as built>
- G11: `versionArgs` not editable in UI. User decision: <fix | keep as built>
- G12: prompt templates hard-coded. User decision: <fix | keep as built>
- G13: Settings version hard-coded. User decision: <fix | keep as built>
- G14: Bob save toast understates auto-test. User decision: <fix | keep as built>

## SPEC references

SPEC 3.2, SPEC 3.3, SPEC 3.3.1-3.3.10, SPEC 4.0-4.9. Detail: [pages.md](../references/pages.md), [feature-specs.md](../references/feature-specs.md).
