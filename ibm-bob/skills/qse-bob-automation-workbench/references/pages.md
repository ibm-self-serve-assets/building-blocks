# Pages

> Extracted verbatim from `SPEC.md` (section 3.3). Do not edit here; edit SPEC.md and re-extract. Paths are relative to the project root.

### 3.3 Pages

All pages except `LoginPage` are `React.lazy` chunks. Every authenticated page sits inside `RequireAuth` → `AppShell`.

#### 3.3.0 Route table

| Route | Component | File | Auth |
|---|---|---|---|
| `/login` | `LoginPage` | `frontend/src/pages/LoginPage.tsx` | public |
| `/` | `OverviewPage` | `frontend/src/pages/OverviewPage.tsx` | session |
| `/bob` | `BobConnectionPage` | `frontend/src/pages/BobConnectionPage.tsx` | session |
| `/repository` | `RepositoryPage` | `frontend/src/pages/RepositoryPage.tsx` | session |
| `/qse` | `QsePage` | `frontend/src/pages/QsePage.tsx` | session |
| `/workspace` | `WorkspacePage` | `frontend/src/pages/WorkspacePage.tsx` | session |
| `/workspace/:executionId` | `WorkspacePage` | same | session |
| `/history` | `HistoryPage` | `frontend/src/pages/HistoryPage.tsx` | session |
| `/reports` | `ReportsPage` | `frontend/src/pages/ReportsPage.tsx` | session |
| `/reports/:executionId` | `ReportViewPage` | `frontend/src/pages/ReportViewPage.tsx` | session |
| `/settings` | `SettingsPage` | `frontend/src/pages/SettingsPage.tsx` | session |
| `*` | redirect to `/` | `frontend/src/App.tsx` | n/a |

Note: the UI does not hide actions by role (viewer/operator). Role enforcement is server-side only; a forbidden action surfaces as a toast with the server's 403 message.

#### 3.3.1 Login (`/login`)

- Full-height `.login-shell` with the radial gradient; centred `.login-card` (form, `aria-labelledby="login-title"`).
- Content: "IBM" eyebrow (`.step-source`), `<h1>` "QSE Automation Workbench", help text "Sign in to orchestrate quantum-safe analysis through Headless Bob."
- Fields: `TextInput#login-username` (autoFocus, required, `autoComplete=username`), `PasswordInput#login-password` (required, `current-password`).
- Submit button full width; disabled while busy or either field empty; shows `InlineLoading "Signing in"` while pending.
- States: idle; busy; error (`InlineNotification` kind error, title "Sign-in failed", subtitle = server message or "Sign-in failed.").
- On success: clears the password, `setSession(user, csrfToken)`, navigates to `state.from` or `/`.
- If already signed in (`ready && user`) it redirects immediately.

#### 3.3.2 Overview (`/`)

- `PageHeader` "Overview".
- Row of 4 `Stat` tiles (`.grid-4`): **Headless Bob** (StatusTag + endpoint; tone ok if connected, none if not_configured, bad otherwise), **Repository** (`owner/name` or "None cloned", sub `Branch <b>`), **QSE CLI** (StatusTag + version), **Executions** (total, tone info, sub "Total recorded").
- `.grid-2`: **Getting started** card (4 numbered steps with done check or dashed circle and an "Open" ghost button) and **Recent executions** card (5 newest; link goes to `/reports/:id` when completed with a report, else `/workspace/:id`; skeleton while loading; `Tile` empty state; error `InlineNotification` "Could not load executions").
- Data: `useBob`, `useRepos`, `useQse`, `useExecutions({page:1,pageSize:5,sort:'createdAt',direction:'desc'})`.

#### 3.3.3 Bob Connection (`/bob`)

- Left card **Connection settings** (form `aria-label="Bob connection settings"`):
  - `TextInput#bob-endpoint` "Headless Bob address", placeholder `http://headless-bob:3000`.
  - `PasswordInput#bob-api-key` "Bob API key" (`autoComplete=new-password`); placeholder `Stored: ••••xxxx — leave blank to keep` when a key hint exists; disabled when auth mode is `none`.
  - Ghost toggle "Show/Hide protocol settings" (`aria-expanded`), revealing: `Dropdown#bob-adapter` (two options), `TextInput#bob-base` "API base path", `Dropdown#bob-auth` (Bearer, Custom header, None), and (only for `header`) `TextInput#bob-header`.
  - Buttons: **Save configuration** (`Save`, disabled unless endpoint non-empty or demo mode), **Test connection** (secondary, disabled unless configured), **Disconnect** (`danger--tertiary`, disabled unless configured).
- Right card **Connection status**: `StatusTag` (forced to `connecting` while a test is pending), `InlineLoading "Contacting Headless Bob"`, error notification for `auth_failed`/`connection_failed`, message line when connected, `KeyValues` (Address, Protocol, API key hint or "Not stored", Last tested).
- Full-width card **Supported capabilities**: `Tile` "No capabilities available…" until a test succeeds, then two `KeyValues` blocks (runtime ready, streaming, cancellation, file download, threads/continuation; run timeout, max message size, max concurrent runs, max download size).
- Toasts: "Configuration saved" (subtitle differs in demo), "Connected to Headless Bob", "Connection test failed", "Disconnected".
- Polling: `useBob` refetches every 1500 ms while `state === 'connecting'`.
- Mock mode: the page is usable without an address; the key is never stored.

#### 3.3.4 Repository Configuration (`/repository`)

- Left card **GitHub repository**: `TextInput#repo-url` (placeholder `https://github.com/owner/repository`; editing clears any validation result), `TextInput#repo-branch` (default `main`), `PasswordInput#repo-token` (optional; helper text switches when a token is already stored).
- Success `InlineNotification` "Repository validated" with `owner/name · branch X · <12-char commit>`.
- Buttons: **Validate repository** (`Checkmark`), **Clone repository** (`Download`), **Re-clone repository** (`Renew`, needs an existing repo), **Remove workspace** (`danger--ghost`, `TrashCan`). All disabled while any mutation is pending or the repo is cloning/validating; validate and clone also need a non-empty URL.
- Right card **Repository details**: `Tile` empty state, or status tag, `InlineLoading "Cloning in progress"`, failure notification "Clone failed", `KeyValues` (name, URL, branch, clone status, workspace label, commit (12), last cloned, files, token stored), and a `role="log"` **Clone progress** block (last 30 sanitized lines).
- The form is seeded from the active/first repository **once** on load.
- Polling: `useRepos` refetches every 1000 ms while any repo is `cloning` or `validating`.
- The page shows one repository (active → first cloned → first). Several can exist in the database; the Workspace page lets the user choose among cloned ones.

#### 3.3.5 QSE Configuration (`/qse`)

- Left card **Locate QSE CLI**: `RadioButtonGroup` (Automatic / Manual).
  - Manual: `TextInput#qse-path`, placeholder `/opt/qse-cli/qse-cli`, helper "Must be an absolute path to an allowed executable (default names: qse-cli, cli.sh)."
  - Automatic: "Discovered candidates" with **Run discovery** (`Search`), `InlineLoading "Searching"`, empty `Tile`, or a `StructuredListWrapper selection` table (Path / Source / Usable tag: green "Executable", gray "Not executable" or "Name not allowed"). Unusable rows are disabled. The first usable candidate is pre-selected.
  - Buttons: primary **Use selected and validate** / **Save and validate**; secondary **Revalidate** / **Validate QSE CLI** (needs a stored path).
- Right card **QSE CLI status**: StatusTag (forced `validating` while pending), error notification "Validation failed", warning "Not reachable from Headless Bob" (valid but outside shared mounts), `KeyValues` (executable path, path in Bob container, detected version, version command, method, validated, execution strategy).
- Discovery query runs automatically when mode is `auto`.

#### 3.3.6 Execution Workspace (`/workspace`, `/workspace/:executionId`)

Cards, top to bottom:

1. **Execution context**: four `.grid-4` cells (Bob status and protocol; repository, branch, clone status; QSE status and version; a repository `Select#ws-repo` shown only when more than one repository is cloned).
2. **What would you like Headless Bob to do?**: `Select#prompt-template` (Full quantum-safe assessment, Cryptographic inventory only, Remediation plan, Dependency review), `Select#prompt-history` (up to 25 distinct previous prompts; disabled when none), `TextArea#prompt` (rows 10, counter, `maxCount` = `settings.limits.maxPromptChars`, falling back to 20000 before settings load; invalid text "Prompt exceeds the N character limit."), **Reset to example**, **Clear**. The textarea is disabled while an execution is active. The draft is saved to `sessionStorage` key `qse.promptDraft`.
3. **Execution controls**: "Pre-flight checks" list (Bob connected; repository cloned; QSE validated **and** reachable from Bob; prompt provided and within limit, each with a **Fix** link to the owning page) and buttons **Start execution** (`Play`, enabled only when all checks pass and nothing is active), **Cancel execution** (`danger--tertiary`, `StopOutline`, enabled only while active and not already `cancelling`), **Clear workspace** (ghost, `TrashCan`, opens the confirmation modal).
4. **Pipeline digital twin**: see [3.4](#34-pipeline-digital-twin).
5. **Execution monitor** (only when an execution is selected): `KeyValues` (ID, status, started, elapsed (ticks every second while active), current activity, "N of M completed[, K failed]", live-updates state "Connected"/"Reconnecting…"/"Not streaming"); `InlineLoading`; notifications for failed, cancelled and warnings; two step lists (**Workbench preparation** `Tag` blue "backend" and **Headless Bob execution** `Tag` purple "headless-bob"); a note "Headless Bob does not report percentage progress, so none is shown." plus streamed character count; the `LogViewer`; and a **View report** button once completed with a report.
6. When nothing is selected: `Tile` "No execution selected. Start one above, or open a previous one from Execution History."

Modal **Clear workspace?** (danger): "This clears the prompt, the current execution view and deletes the cloned repository from the isolated workspace. Execution history and reports are kept." Buttons "Clear workspace" / "Keep".

Behaviour:

- Starting an execution navigates (replace) to `/workspace/:id` and stores the id in `sessionStorage` (`qse.activeExec`); the repository id is in `qse.activeRepo`.
- Live data comes from `useExecutionStream` (SSE) merged over `useExecution` (poll every 4 s while active). Logs: the stream array is used when it holds at least as many lines as the REST fallback (`GET /executions/:id/logs`).
- Because `Content` has no separate scroll container, the page scrolls as a whole.

#### 3.3.7 Execution History (`/history`)

- Carbon `DataTable` in `TableContainer` titled "Executions" (description "`N total`").
- Toolbar: `Search#history-search` (placeholder "Search prompt, repository or ID"; debounced 300 ms; resets page to 1) and `Dropdown#history-status` (All, Completed, Failed, Running, Queued, Cancelling, Cancelled).
- Columns: Execution ID (first 8 chars, tooltip full id, magenta `DEMO` tag for mock runs), Repository, Prompt (summary, tooltip full), Date, Duration, Status (`StatusTag`), Report (green "Available" or gray "None"), Actions (**View execution**, **View report** (disabled without a report)).
- Sortable by Repository, Date, Duration, Status; clicking toggles direction; a new column starts descending.
- `Pagination` page sizes 10/25/50.
- States: skeleton rows while loading, empty row "No executions match…" with a link, error notification "Could not load history".
- Auto-refresh every 3 s while any listed execution is queued/running/cancelling.

#### 3.3.8 Reports (`/reports`)

- Lists completed executions that have a `reportId`, taken from the newest 100 executions (client-side filter). Executions beyond the newest 100 are not shown (limitation).
- Each is a `Card` with status tag, optional `DEMO` tag, date, repository name, prompt summary, branch, duration, a link to the execution and an **Open report** button.
- States: skeleton, empty `Tile` "No reports yet. A report is available after an execution finishes.", error notification.

#### 3.3.9 Report view (`/reports/:executionId`)

- Loads `GET /api/executions/:id/report` (no retry). 404 renders a warning "No report available"; other errors an error notification; both with an "Open execution" link.
- Header "End-to-End Report", subtitle `repo · branch X · generated <date>`, actions: **Copy report** (clipboard), **Markdown**, **PDF**, **JSON results** (anchor downloads), **View execution logs** (jumps to the Logs tab).
- Status tag plus a source tag: green "Report file written by Headless Bob", blue "Final answer returned by Headless Bob (no report file was produced)", red "Headless Bob returned no report content".
- Warning or info notification for `unavailable` and `headless-bob-output`.
- `Tabs` (contained): **Executive Summary** (sections `summary` + `conclusion`; falls back to the raw `bobMarkdown` when the report has no structure), **Findings** (`findings` + `other`), **Recommendations**, **Execution Details** (KeyValues, warnings, step list), **Artifacts** (list with Download for retrieved files, "Not retrieved" tag otherwise, and an **Export report with logs (JSON)** link), **Logs** (fetched lazily when tab 5 opens; `LogViewer`, note "Secrets are redacted before logs are stored.").
- Section text is rendered by the `Markdown` component (raw HTML skipped, only `http(s):`, `mailto:`, `#` links kept, links open in a new tab with `noopener noreferrer nofollow`).

Note: the report tabs are fixed by the UI. There is **no** "Cryptographic Findings", "Risk Categorization" or "Remediation" tab; those names appear only if Bob's own Markdown headings match the classifier (see [4.7](#47-report-generation)).

#### 3.3.10 Settings (`/settings`)

- **Server configuration** (read-only `KeyValues`): version, execution strategy, prompt limit, execution timeout, concurrent executions, allowed Git hosts, session lifetime and idle time, encryption key id, stream mode tag (magenta "mock — demo, recorded data" or green "realtime — live Headless Bob").
- **Shared execution environment**: list of `label → bobPath` mounts, or `Tile` "No shared mounts configured."
- **Change password**: three `PasswordInput`s (current, new with helper "At least 12 characters.", confirm with mismatch error "Passwords do not match."). Submit enabled only when current is set, new has at least 12 characters and matches. On success all sessions are revoked server-side, the client clears session and cache and navigates to `/login` with a toast.
- **Credential rotation**: admin sees the instructions and a **Re-encrypt stored secrets** button opening a confirmation modal; others see an info notification "Administrator only".
