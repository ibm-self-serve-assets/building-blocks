# Frontend UI guide

## When to use

After the backend phases. Use to create the frontend foundation that pages and the digital twin sit on. The pages themselves belong to `feature-pages.md`; the Pipeline twin belongs to `digital-twin.md`. Do not duplicate their content here.

## Inputs you need

- [design-tokens.md](../references/design-tokens.md): tokens, typography, spacing, responsive rules (SPEC 3.1.2-3.1.6).
- [component-inventory.md](../references/component-inventory.md): shared components, `StatusTag` mapping, hooks, stores, services (SPEC 3.5).
- `BUILD_DECISIONS.md` (G3, G4).
- The backend API contract (SPEC 6.2) and DTOs.

## Requirements covered

| ID | Requirement | Acceptance test |
|---|---|---|
| NFR-06 | UI uses IBM Carbon g100 dark and IBM Plex | `index.html` has `data-carbon-theme="g100"`; `main.tsx` wraps in `GlobalTheme theme="g100"`; body renders `#161616` background and IBM Plex Sans; no font is loaded from a CDN. |

## Steps

### 1. Theme setup (SPEC 3.1.1) in `frontend/src/styles/index.scss`

- `@use '@carbon/react/scss/config'` with `$font-path: '@ibm/plex'` and `$css--font-face: false`.
- `@use '@carbon/styles/scss/themes'`, then `theme with ($theme: themes.$g100)`, then `@use '@carbon/react'`, `spacing as *`, `type`.
- `@import '@ibm/plex-sans/css/ibm-plex-sans-default.min.css'` for font faces.
- `index.html`: `<html data-carbon-theme="g100">`, `<meta name="color-scheme" content="dark">`; CSS `:root { color-scheme: dark }`; `body` hard-codes `#161616` / `#f4f4f4`.
- `main.tsx` provider order: `React.StrictMode` -> `GlobalTheme g100` -> `QueryClientProvider` -> `BrowserRouter` -> `App`. QueryClient defaults: retry only on network errors and fewer than 2 attempts, `refetchOnWindowFocus: true`, `staleTime: 5000`.

### 2. G3 caveat (must read)

`GlobalTheme` supplies React context only; it does **not** add `.cds--g100` to the DOM, so `--cds-*` custom properties are **undefined** in the page. HTML survives through hard-coded body colours and Carbon's own fallbacks, but custom rules like `.card { background: var(--cds-layer-01) }` and SVG fills can resolve to initial values (SVG falls to black fill / no stroke; this blanked the first digital twin). Choose one:

- **Keep as built (faithful):** use the literal g100 values in [design-tokens.md](../references/design-tokens.md) for anything custom, and give SVG components their own variables (see `digital-twin.md`).
- **Fix:** add the `cds--g100` class to `<html>` or `<body>` and then `var(--cds-*)` works.

Also note: the value of `border-subtle-01` was not extracted from the bundle; the table says `#393939` (Carbon g100). Verify when theming.

### 3. App shell (SPEC 3.2) `frontend/src/layouts/AppShell.tsx`

- Carbon `Header` (48 px) with `SkipToContent`, `HeaderName` prefix "IBM" text "QSE Automation Workbench" linking to `/`.
- `.header-status` (label-01, `#c6c6c6`), left to right: Bob (dot: connected `#42be65`, connecting `#78a9ff`, not_configured `#8d8d8d`, else `#fa4d56`; text `Bob: [Demo - ]<label>`); magenta `Tag` `STREAM_MODE=mock` only in mock; repository `owner/name@branch` (max-width 16 rem, hidden under 1056 px); `QSE: <status>` (hidden under 1056 px); `Execution: <status or Idle>` dot (running `#78a9ff`, failed `#fa4d56`, completed `#42be65`, else `#8d8d8d`). Whole group hidden under 672 px.
- `HeaderGlobalAction` with `UserAvatar` (20) toggles a `HeaderPanel` -> `Switcher`: "`username (role)`", divider, **Settings**, **Sign out** (`Logout` icon).
- `SideNav expanded isFixedNav isRail={false}`, 16 rem wide, 8 items: Overview `/` (Dashboard, exact), Bob Connection `/bob` (Connect), Repository Configuration `/repository` (LogoGithub), QSE Configuration `/qse` (Chip), Execution Workspace `/workspace` (Code), Execution History `/history` (Activity), Reports `/reports` (DocumentMultiple_01), Settings `/settings` (Settings); others use `startsWith`.
- `Content` has `margin-left: 16rem; margin-top: 3rem`; `.app-main` padding `$spacing-07`, `max-width: 1584px`, centred; `<Suspense fallback=Loading><Outlet/></Suspense>`; `<Toasts/>` fixed top 3.5 rem right 1 rem.
- `RequireAuth`: not ready -> `<Loading description="Checking session" />`; no user -> `Navigate` to `/login` (`replace`, `state.from`); else `Outlet`.
- `App.tsx`: on mount `GET /api/auth/me`; success -> `setSession(user, csrf)`; always `markReady()`; global 401 handler (`setUnauthorizedHandler`) clears session and query cache and navigates to `/login`. All pages except `LoginPage` are `React.lazy`. Unknown routes redirect to `/`.

### 4. Shared components (SPEC 3.5.1)

Implement with the exact props listed in [component-inventory.md](../references/component-inventory.md): `PageHeader`, `Card`, `Stat`, `KeyValues` (all in `components/PageHeader.tsx`), `StatusTag` (+ `statusLabel`; 21 statuses), `LogViewer` (`role="log"`, `aria-live="off"`, `tabIndex=0`, `aria-label="Execution logs"`, source filter, follow checkbox, `headless-bob` displayed as `bob`), `Markdown` (react-markdown + remark-gfm; **raw HTML skipped**; only `http(s):`, `mailto:`, `#` links; links open in a new tab with `rel="noopener noreferrer nofollow"`), `RequireAuth`, `Toasts` (`aria-live="polite"`, kinds success/error/info/warning, `timeout={0}`).

### 5. Hooks, stores, services (SPEC 3.5.3)

- `services/api.ts`: typed fetch client; `credentials: 'same-origin'`; `X-CSRF-Token` on every non-GET; POST bodies default `{}`; network failure -> `ApiError(0,'network_error','Cannot reach the Workbench backend. Check your connection.')`; 401 on any path except `/auth/login` and `/auth/me` calls the unauthorized handler. `ApiError(status, code, message, requestId?)`.
- `hooks/queries.ts`: `useBob`, `useQse`, `useSettings` (stale 60 s), `usePrompts`, `useRepos`, `useExecutions`, `useExecution`, `useReport`, `useInvalidate`, and the `keys` factory. Poll intervals: Bob 1500 ms while `connecting`; repos 1000 ms while `cloning`/`validating`; executions list 3000 ms while any active; single execution 4000 ms while active.
- `hooks/useExecutionStream.ts`: `EventSource` on `/api/executions/:id/stream?after=<lastId>` with credentials; listens to `execution` and `log`; keeps at most **5000** log lines; on error closes and, if the cached execution is not terminal, retries after **2000 ms**; terminal events invalidate `['executions']` and `['prompts']`.
- `hooks/useNotify.ts` (success/info/error toasts; error subtitle from `ApiError.message`), `hooks/useElapsed.ts` (`useNow(active, interval=1000)`).
- Stores (zustand 5): `session` (`{user, ready, setSession, markReady}`; CSRF token only in module memory), `workspace` (`activeRepositoryId`, `activeExecutionId`, `promptDraft` persisted to `sessionStorage` keys `qse.activeRepo`, `qse.activeExec`, `qse.promptDraft`; no secrets, no `localStorage`), `notifications` (last 4 toasts; auto-dismiss 6 s, 10 s for errors).
- `services/format.ts`: `formatDuration`, `formatDate`, `formatBytes`, `formatTime`, `ACTIVE_STATUSES` (queued, running, cancelling), `TERMINAL_STATUSES` (completed, failed, cancelled). `types/api.ts` holds all DTOs.

### 6. ErrorBoundary decision (G4)

The reference has **no** `ErrorBoundary`; a render exception blanks the page. Faithful clone: keep as built but add the regression test in `digital-twin.md`. If BUILD_DECISIONS says "fix": add a route-level boundary in `App.tsx` that shows an `InlineNotification` and a link back to `/`.

### 7. Assets (SPEC 3.6)

`frontend/public/favicon.svg` (32x32, `#161616` square, `#78a9ff` hexagon glyph); page title "QSE Automation Workbench"; fonts bundled (no CDN); icons from `@carbon/icons-react` only; no images or logos (the text "IBM" is the only brand mark).

### 8. Responsive and accessibility

Breakpoints and spacing are in design-tokens.md. Side nav is fixed 16 rem at all widths (no collapse). `SkipToContent` present. No animations in app SCSS.

## Verification (exit gate)

```bash
cd frontend && npm run typecheck && npm test && npm run build && npm audit --omit=dev
```

- NFR-06 statement: grep the built `dist/` for `fonts.googleapis`/`cdn` (must be none) and confirm the Plex font files are bundled.
- Tests to port: `api.test.ts` (5), `stores.test.ts` (4), `format.test.ts` (4), `components.test.tsx` (StatusTag `it.each`, LogViewer, Markdown).
- Visual check: login background `radial-gradient(circle at 20% 10%, #1c2a44 0%, #161616 55%)`, header 48 px, side nav 16 rem.

## Pitfalls

- Relying on `var(--cds-*)` without applying the theme class (G3).
- Storing tokens or the CSRF token in `localStorage`/`sessionStorage`.
- Rendering Markdown with raw HTML enabled.
- Hiding the side nav on small screens (reference never collapses it).
- Duplicating twin or page logic here.

## Known gaps that apply

- G3: `--cds-*` variables undefined because `.cds--g100` is never applied. User decision: <fix | keep as built>
- G4: no ErrorBoundary. User decision: <fix | keep as built>

## SPEC references

SPEC 3.1, SPEC 3.2, SPEC 3.5, SPEC 3.6, SPEC 8.1 (output encoding). Detail: [design-tokens.md](../references/design-tokens.md), [component-inventory.md](../references/component-inventory.md). Next: `digital-twin.md`, `feature-pages.md`.
