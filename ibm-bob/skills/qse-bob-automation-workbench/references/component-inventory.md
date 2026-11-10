# Component, hook, store and service inventory

> Extracted verbatim from `SPEC.md` (section 3.5). Do not edit here; edit SPEC.md and re-extract.

## Component inventory

All paths under `frontend/src/`. "Dependencies" lists the Carbon or library parts used.

## 3.5.1 Shared components

| Name | Purpose | Path | Props | Local state | Events | Styling | Variants | Dependencies | Responsive |
|---|---|---|---|---|---|---|---|---|---|
| `PageHeader` | Page title row | `components/PageHeader.tsx` | `title: string`, `subtitle?: string`, `actions?: ReactNode` | none | none | `.row`, `.page-title`, `.page-subtitle`, `.spacer` | with/without subtitle and actions | none | actions wrap via `.row` |
| `Card` | Layer-01 panel with optional title bar | `components/PageHeader.tsx` | `title?`, `icon?`, `help?`, `children`, `actions?` | none | none | `.card`, `.card-title`, `.card-help` | titled / untitled | none | fluid |
| `Stat` | Summary tile | `components/PageHeader.tsx` | `label`, `value`, `sub?`, `tone?: 'ok'\|'bad'\|'warn'\|'info'` | none | none | `.stat` + tone class | 4 tones + none | none | in `.grid-4` |
| `KeyValues` | Definition list of label/value pairs | `components/PageHeader.tsx` | `rows: Array<[string, ReactNode]>` | none | none | `.kv` | none | none | one column under 672 px; null value renders `—` |
| `StatusTag` | Coloured status pill | `components/StatusTag.tsx` | `status: AnyStatus`, `size?: 'sm'\|'md'` | none | none | Carbon `Tag` | 21 mapped statuses (below); unknown → gray with raw text | `Tag` | n/a |
| `statusLabel` | Label lookup helper | `components/StatusTag.tsx` | `(s: string)` | none | none | n/a | n/a | none | n/a |
| `LogViewer` | Filterable, auto-scrolling log list | `components/LogViewer.tsx` | `logs: ExecutionLog[]`, `live: boolean` | `follow` (true), `source` ('all') | `Dropdown` change, `Checkbox` change | `.log-view`, `.log-line`, `.ts`, `.src-*` | source filter: all / backend / headless-bob / system; `headless-bob` is displayed as `bob` | `Dropdown#log-source`, `Checkbox#log-follow` | fixed height 26 rem, scrolls |
| `Markdown` | Safe Markdown renderer | `components/Markdown.tsx` | `children: string` | none | none | `.markdown` | GFM tables | `react-markdown`, `remark-gfm` | max-width 62 rem |
| `RequireAuth` | Route guard | `components/RequireAuth.tsx` | none | none | none | n/a | loading / redirect / outlet | `Loading`, `Navigate`, `Outlet` | n/a |
| `Toasts` | Toast stack | `components/Toasts.tsx` | none | reads `useToasts` | `onClose` dismisses | fixed, top 3.5 rem, right 1 rem, z-index 9100, grid gap 0.5 rem | kinds success/error/info/warning, `lowContrast`, `timeout={0}` (store handles expiry) | `ToastNotification` | fixed |
| `PipelineTwin` | Pipeline diagram | `components/PipelineTwin.tsx` | see 3.4 | none | none | `.twin*` | tones ok/active/error/warn/idle | inline SVG | horizontal scroll under 1000 px |
| `AppShell` | Header, side nav, outlet | `layouts/AppShell.tsx` | none | user-panel open flag | sign out, nav clicks | Carbon `Header`, `SideNav`, `.header-status` | mock vs realtime header | Carbon UI Shell, `@carbon/icons-react` | see 3.1.6 |

`StatusTag` mapping (type / label):

| Status | Carbon tag | Label |
|---|---|---|
| not_configured | gray | Not configured |
| connecting | blue | Connecting |
| connected | green | Connected |
| auth_failed | red | Authentication failed |
| connection_failed | red | Connection failed |
| pending | gray | Pending |
| validating | blue | Validating |
| validated | cyan | Validated |
| cloning | blue | Cloning |
| cloned | green | Cloned |
| failed | red | Failed |
| discovered | cyan | Discovered |
| valid | green | Valid |
| invalid | red | Invalid |
| queued | gray | Queued |
| running | blue | Running |
| cancelling | warm-gray | Cancelling |
| completed | green | Completed |
| cancelled | warm-gray | Cancelled |
| skipped | gray | Skipped |

(`pending`/`failed`/`skipped` are shared across repo, step and execution status domains.)

## 3.5.2 Page-local components (not exported)

| Name | File | Purpose |
|---|---|---|
| `StepIcon` | `pages/WorkspacePage.tsx` | Icon per step status: `CheckmarkFilled` (success), `ErrorFilled` (error), `InProgress` (info), `WarningFilled` (warning, for cancelled/skipped), `CircleDash` (pending) |
| `StepRow` | `pages/WorkspacePage.tsx` | One `li`: icon, label, source line ("Headless Bob" / "Workbench backend"), optional message, small `StatusTag` |
| `Sections` | `pages/ReportViewPage.tsx` | Renders report sections as `h3` + `Markdown`, or an empty `Tile` |

## 3.5.3 Hooks, stores and services

| Name | File | Behaviour |
|---|---|---|
| `useBob`, `useQse`, `useSettings` (stale 60 s), `usePrompts`, `useRepos`, `useExecutions`, `useExecution`, `useReport`, `useInvalidate` | `hooks/queries.ts` | TanStack Query wrappers. Poll intervals: Bob 1500 ms while `connecting`; repos 1000 ms while `cloning`/`validating`; executions list 3000 ms while any active; single execution 4000 ms while active |
| `keys` | `hooks/queries.ts` | Query-key factory: `bob`, `repos`, `repo(id)`, `qse`, `qseDiscover`, `executions(q)`, `execution(id)`, `report(id)`, `prompts`, `settings` |
| `useExecutionStream(id)` | `hooks/useExecutionStream.ts` | `EventSource` on `/api/executions/:id/stream?after=<lastId>` with credentials. Listens to `execution` and `log`. Keeps at most **5000** log lines. On error: closes, and if the cached execution is not terminal retries after **2000 ms**. Terminal events invalidate `['executions']` and `['prompts']`. |
| `useNotify` | `hooks/useNotify.ts` | `success`, `info`, `error(e, title)` → toasts; error subtitle from `ApiError.message` |
| `useNow(active, interval=1000)` | `hooks/useElapsed.ts` | Ticking clock for elapsed time |
| `useSession` (zustand) | `stores/session.ts` | `{user, ready, setSession(user, csrf), markReady}`; stores the CSRF token in module memory only |
| `useWorkspace` (zustand) | `stores/workspace.ts` | `activeRepositoryId`, `activeExecutionId`, `promptDraft`; persisted to `sessionStorage` keys `qse.activeRepo`, `qse.activeExec`, `qse.promptDraft`. No secrets. |
| `useToasts` (zustand) | `stores/notifications.ts` | Keeps the last 4 toasts; auto-dismiss after 6 s (10 s for errors) |
| `api` | `services/api.ts` | Typed fetch client; see [6](#6-api-specification). `ApiError(status, code, message, requestId?)`. `credentials: 'same-origin'`. Sends `X-CSRF-Token` on every non-GET. POST bodies default to `{}`. Network failure → `ApiError(0, 'network_error', 'Cannot reach the Workbench backend. Check your connection.')`. 401 on any path other than `/auth/login` and `/auth/me` invokes the unauthorized handler. |
| `format.ts` | `services/format.ts` | `formatDuration`, `formatDate`, `formatBytes`, `formatTime`, `ACTIVE_STATUSES` (queued, running, cancelling), `TERMINAL_STATUSES` (completed, failed, cancelled) |
| Types | `types/api.ts` | All DTO interfaces used below |
