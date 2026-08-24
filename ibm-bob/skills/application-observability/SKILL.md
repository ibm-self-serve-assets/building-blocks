---
name: instana-observability
description: >-
  Use when the user wants to work with Instana application monitoring — building
  or modifying TypeScript API clients, creating React observability dashboards
  with trace visualizations, analyzing service errors and latency, setting up
  monitoring integrations, handling pagination and retries, or investigating
  performance bottlenecks using Instana REST APIs.
metadata:
  disable-model-invocation: false
---

# Application Observability with Instana

This skill covers four workflows. Identify which applies to the current task and follow that section. Supporting reference files are in the sub-folders alongside this skill.

---

## Workflow 1 — API Client

Use when building or extending an Instana REST API client, adding endpoints, implementing authentication, validating responses, or writing API integration tests.

<Steps>
<Step>
**Understand the scope.**
Ask or identify:
- Which Instana API endpoints are involved (Applications, Services, Traces, Events, Infrastructure, SLO).
- Whether this is a new client or an extension to an existing one.
- The target language/framework (TypeScript/Node.js for the API client, React for the UI).
- Authentication method — Instana uses an `Authorization: apiToken <token>` header.

Read any existing client files before writing new code.
</Step>

<Step>
**Locate or scaffold the client.**
- If extending: use `grep` and `read_file` to find the existing client class/module.
- If new: create a dedicated TypeScript module (`src/lib/instanaClient.ts`) with an `axios` instance pre-configured with the auth header and a single `request()` helper that centralises error handling.

Follow the patterns in `instana-api-client/api-patterns.md`.
</Step>

<Step>
**Implement each endpoint method.**
- Map HTTP method + path to a typed method.
- Accept only the parameters the caller actually needs.
- Return structured response objects, not raw HTTP responses.
- Handle the Instana pagination envelope (`{ items, page, pageSize, totalHits }`) using the pagination helper in `instana-api-client/api-patterns.md`.

> ⚠️ **Application scoping — the traces endpoint behaves differently from metrics:**
> - `POST /metrics/services` and `POST /metrics/endpoints` accept `"applicationId"` as a top-level field and correctly scope results.
> - `POST /analyze/traces` **silently ignores** the top-level `"applicationId"` field and returns traces from **all applications**.
>   To scope traces correctly, fetch the app perspective config once (`GET /api/application-monitoring/settings/application/{id}`), extract its `tagFilterExpression`, and pass that in the traces request body.
>   For erroneous-only filtering, wrap the app filter and the erroneous filter in an `EXPRESSION` node with `logicalOperator: "AND"`.
>   Cache the app config — it changes rarely and does not need to be re-fetched on every trace call.
>   See `instana-api-client/endpoint-reference.md` → "Application Perspective Scoping" for the full code pattern.

See `instana-api-client/endpoint-reference.md` for common endpoint shapes.
</Step>

<Step>
**Add authentication and connection validation.**
- Raise `ConfigurationError` at construction time if the API token is missing.
- Add a `validate_connection()` method that calls `GET /api/instana/health`.
</Step>

<Step>
**Handle errors and retries.**
- Map HTTP error codes to typed exceptions: `401` → `AuthenticationError`, `403` → `PermissionError`, `429` → `RateLimitError` (honour `Retry-After`), `5xx` → `ServerError` (retry with exponential back-off, max 3 attempts).
- Never swallow errors silently — always surface status code and response body.

Refer to `instana-api-client/error-handling.md` for the full error class hierarchy and retry patterns.
</Step>

<Step>
**Validate responses and write tests.**
- Use TypeScript interfaces to type response objects; assert required fields are present at runtime.
- Log unexpected shapes at `console.warn` level rather than throwing, to tolerate minor API changes.
- Write a Vitest/Jest unit test per endpoint covering: success, 401, 403, 429, 500, and pagination.

Use templates in `instana-api-client/testing-patterns.md`.
</Step>

<Step>
**Optimise API call patterns for performance.**
- Reuse a single `axios` instance across all requests — never create a new instance per call.
- Use `Promise.all` for independent parallel requests; avoid sequential `await` chains.
- Cache stable data (application list, service list) with a simple TTL map in a React context or custom hook — do not re-fetch on every render.
- Set an explicit `timeout` (default 30 000 ms) on the axios instance.
- Log `X-RateLimit-Remaining` at `console.debug` level and back off proactively when it drops below 10.

See `instana-api-client/performance-patterns.md` for caching helpers and parallel-fetch examples.
</Step>

<Step>
**Document API usage patterns.**
After implementing, write or update the project README section covering:
- Required environment variables and where to obtain the API token.
- Which endpoints are used and what data each returns.
- Request/response examples for the most important methods.
- Known error codes and how the client handles them.
- Rate limit behaviour and retry policy.

Use `instana-api-client/api-doc-template.md` as the documentation template.
</Step>

<Step>
**Review and verify.**
Run `npm test` and confirm lint passes (`eslint`, `tsc --noEmit`). Summarise files created/modified, endpoints added, and tests added.
</Step>
</Steps>

---

## Workflow 2 — Monitoring Dashboard

Use when building or enhancing an Instana-backed React observability dashboard with interactive visualizations, clickable trace IDs, error modals, or service health panels.

<Steps>
<Step>
**Clarify requirements.**
Ask or identify:
- What data to display (services, traces, error rates, latency, call patterns, events, SLOs, infrastructure).
- React + TypeScript is the target stack; use Vite as the build tool unless the project already has a different setup.
- Whether clickable trace IDs opening a detail modal/drawer are needed.
- Time range controls required (fixed window, rolling, or date picker via `react-datepicker`).
- New app or enhancement to an existing file.

Read existing source files before making any changes.
</Step>

<Step>
**Scaffold the React app (if new).**
```bash
npm create vite@latest instana-dashboard -- --template react-ts
cd instana-dashboard
npm install axios recharts @tanstack/react-query date-fns
```
Structure:
```
src/
  lib/instanaClient.ts     ← API client (Workflow 1)
  hooks/useInstanaData.ts  ← React Query data-fetch hooks
  components/
    Header.tsx
    KpiCard.tsx
    TraceTable.tsx
    TraceDetailModal.tsx
    charts/ErrorRateChart.tsx
    charts/LatencyChart.tsx
    charts/CallVolumeChart.tsx
  App.tsx
```

Refer to `instana-dashboard/dashboard-patterns.md` for component and hook skeletons.

> **CRA (react-scripts) users — critical setup notes:**
>
> **1. Environment variables (`REACT_APP_*` prefix required)**
> CRA only exposes variables prefixed `REACT_APP_` to the browser bundle. Use `.env.local` (not `.env.example`). Values are baked in at `npm start` time — **restart the dev server after every `.env.local` change**.
> ```
> REACT_APP_INSTANA_URL=https://unit0-techzone.150-240-162-27.nip.io
> REACT_APP_INSTANA_TOKEN=<real-token>
> REACT_APP_APPLICATION_ID=<real-app-id>
> ```
> ⚠️ **Placeholder trap:** If `.env.local` still contains `your-api-token-here`, Instana returns **401 Unauthorized** — the literal string is sent as the token. Always verify: `grep "your-" .env.local` should return nothing.
>
> **2. CORS — use the CRA proxy**
> Browsers block cross-origin requests. Add a `"proxy"` field to `package.json` (not `.env`) pointing to the Instana host. The dev server then forwards all `/api/*` requests to Instana server-side:
> ```json
> "proxy": "https://unit0-techzone.150-240-162-27.nip.io"
> ```
> In `src/api/instana.js`, use relative paths (no hostname) so the proxy intercepts them:
> ```js
> fetch('/api/application-monitoring/metrics/applications', ...)
> ```
> Restart the dev server after adding or changing the proxy.
>
> **3. Authentication header**
> Instana does **not** use Basic auth or Bearer tokens. The only valid format is:
> ```
> Authorization: apiToken <token>
> ```
>
> **4. Source map warnings**
> Add `GENERATE_SOURCEMAP=false` to the `start` and `build` scripts to suppress `source-map-loader` warnings from prebuilt CSS in `@carbon/charts-react` and similar packages:
> ```json
> "start": "GENERATE_SOURCEMAP=false react-scripts start",
> "build": "GENERATE_SOURCEMAP=false react-scripts build"
> ```
</Step>

<Step>
**Implement data fetching with React Query.**
- Wrap every Instana API call in a `useQuery` hook from `@tanstack/react-query`.
- Set `staleTime` to 60 000 ms for stable data (application list); use 0 for traces and events.
- Use `isLoading` / `isError` states to show a spinner or inline error message automatically.
- Never call the API directly inside a component render function.

See `instana-dashboard/dashboard-patterns.md` for `useQuery` hook templates.
</Step>

<Step>
**Build interactive trace visualization.**
- Each row in `TraceTable` must show: Trace ID (clickable button), service, endpoint, duration (ms), status badge, timestamp.
- Clicking a trace ID opens `TraceDetailModal` as a right-side drawer showing:
  - Full span call tree with depth indentation (`SpanTree` component)
  - Error message and stack trace for erroneous spans
  - HTTP method, URL, status code, host per span
- Lazy-fetch the trace tree via `GET /api/application-monitoring/analyze/traces/{traceId}` only on modal open using a separate `useQuery` keyed on `traceId`.

See `instana-dashboard/trace-modal-template.md` for the modal and `SpanTree` component patterns.
</Step>

<Step>
**Implement filters.**
- Application `<select>` (populated from `useApplications()` hook).
- Cascading service/endpoint `<select>` (re-fetched when application changes).
- Error-only checkbox and minimum latency `<input type="number">`.
- Store filter state in a single `useReducer` at the `App` level; pass down via context or props.
- All filter changes invalidate the relevant React Query cache keys, triggering a fresh fetch.
</Step>

<Step>
**Apply observability-appropriate styling.**
Follow `instana-dashboard/dashboard-style-guide.md`:
- Dark/neutral background; CSS custom properties for all theme colours.
- Status colours: `--color-error: #ef4444`, `--color-degraded: #f59e0b`, `--color-healthy: #22c55e`.
- No 3D, gradients, or decorative chrome.
- Trace IDs in `font-family: monospace`, colour `#7dd3fc`, `cursor: pointer`.

Use Recharts chart components from `instana-dashboard/chart-templates.md`.
</Step>

<Step>
**Review and verify.**
Run `npm run dev` and confirm all panels load. Click a trace ID — confirm the detail modal opens with span tree. Confirm filters trigger fresh data. Run `npm run lint` and `tsc --noEmit`. Summarise files and interactions added.
</Step>
</Steps>

---

## Workflow 3 — Trace Analysis

Use when investigating service errors, analyzing latency patterns, filtering traces by application/service, identifying performance bottlenecks, or computing error rate and call statistics.

<Steps>
<Step>
**Define the analysis scope.**
Ask or identify:
- Which application(s) or service(s) to analyze.
- The time window (last 1 hour, last 24 hours, a specific incident window).
- The analysis goal: error investigation, latency analysis, call pattern analysis, service dependency mapping, or SLO compliance check.
</Step>

<Step>
**Fetch the raw data.**
- **Error analysis:** `POST /api/application-monitoring/analyze/call-groups` with `call.erroneous = true` tag filter.
- **Latency analysis:** same endpoint requesting `latency.p50`, `latency.p95`, `latency.p99` grouped by `endpoint.name`.
- **Call volume:** same endpoint requesting `calls.count`.
- **Individual traces:** `POST /api/application-monitoring/analyze/traces`, then `GET /api/application-monitoring/analyze/traces/{traceId}` for full trace trees.

Always page through all results. Use ready-made request bodies from `instana-trace-analysis/analysis-queries.md`.
</Step>

<Step>
**Compute derived metrics.**
Key formulas:
- Error rate % = `(error_calls / total_calls) × 100`
- Top-N slowest endpoints = sort by `latency.p99` descending
- Error spike = `current_window_errors / baseline_errors > threshold`

Refer to `instana-trace-analysis/analysis-metrics.md` for SLO thresholds and root cause heuristics.
</Step>

<Step>
**Identify root causes.**
- Group errors by `call.http.status` (4xx vs 5xx).
- Fetch the 5 most-recent erroneous trace IDs and retrieve their full trees.
- The deepest erroneous span is typically the origin of the failure.
- For latency: compare p99 vs p50 — a large gap means outliers, not systemic slowness.
</Step>

<Step>
**Produce the analysis output.**
Present in order: (1) one-paragraph summary, (2) key metrics table, (3) top issues ranked by error count or latency, (4) root cause evidence with specific trace IDs and span detail, (5) concrete recommendations.

Follow `instana-trace-analysis/analysis-report-template.md`.
</Step>

<Step>
**Optionally persist results.**
Write a timestamped JSON file with raw metrics and trace IDs, and generate a Markdown report using `instana-trace-analysis/analysis-report-template.md`.
</Step>
</Steps>

---

## Workflow 4 — Monitoring Setup

Use when setting up an Instana monitoring integration from scratch — configuring the client, dependencies, pagination, retry logic, rate limit handling, and end-to-end connection validation.

<Steps>
<Step>
**Gather configuration requirements.**
Ask or identify the Instana unit URL, API token source (existing `.env`, secrets manager, or to be created), signals needed (traces, events, SLOs, infrastructure), and deployment target (React SPA, Node.js backend, or CI pipeline).

Never hard-code API tokens. Always read from environment variables or a secrets manager.
</Step>

<Step>
**Set up configuration and environment.**
Copy the correct section from `instana-monitoring-setup/env-template.env` into the active env file for your build tool:

- **CRA:** copy to `.env.local`; use `REACT_APP_*` prefix; read via `process.env.REACT_APP_*`
- **Vite:** copy to `.env.local`; use `VITE_*` prefix; read via `import.meta.env.VITE_*`
- **Node.js:** copy to `.env`; use plain names; read via `process.env.*` (with `dotenv`)

Replace every placeholder value immediately — a literal `your-api-token-here` string causes **401 Unauthorized**. Add the env file to `.gitignore`. Restart the dev server after any edit.

For React (CRA or Vite) apps also configure the dev-server proxy to avoid CORS:
- **CRA:** add `"proxy": "<instana-url>"` to `package.json`
- **Vite:** add a `server.proxy` entry in `vite.config.ts`

Then use **relative paths** in all `fetch()` calls (e.g. `/api/application-monitoring/...`) so the proxy intercepts them.
</Step>

<Step>
**Install dependencies.**
React app: `axios`, `@tanstack/react-query`, `recharts`, `date-fns`. Node.js backend/script: `axios`, `dotenv`. Update `package.json` and run `npm install`. Confirm no peer-dependency conflicts.
</Step>

<Step>
**Implement and validate the client.**
Follow Workflow 1 to build the TypeScript client. Then create a `scripts/verify-connection.ts` script that calls `validateConnection()` and `getApplications()`, logs results, and exits non-zero on failure. Run with `npx tsx scripts/verify-connection.ts`.
</Step>

<Step>
**Configure pagination and validate rate limiting.**
Test the pagination helper against a real endpoint and confirm `results.length === totalHits`. Add a `console.debug` log for `X-RateLimit-Remaining` in the axios response interceptor, and `console.warn` when it drops below 10.
</Step>

<Step>
**Create an API inspection script.**
Create `scripts/inspect-api.ts` that accepts an endpoint path as a CLI argument and prints the raw JSON response. Run with `npx tsx scripts/inspect-api.ts /api/instana/health`. Mark it as local-development only — do not deploy it.
</Step>

<Step>
**Run end-to-end validation.**
Work through the checklist in `instana-monitoring-setup/setup-checklist.md`. Confirm `verify-connection.ts` succeeds, pagination returns the correct total, a 401 throws `AuthenticationError`, and no token appears in any tracked file.
</Step>
</Steps>

---

## Supporting Files

| File | Workflow | Purpose |
|------|----------|---------|
| `instana-api-client/api-patterns.md` | 1 | Client structure, pagination helper, request wrapper |
| `instana-api-client/endpoint-reference.md` | 1 | Common Instana endpoint signatures |
| `instana-api-client/error-handling.md` | 1 | Exception hierarchy and retry logic |
| `instana-api-client/testing-patterns.md` | 1 | Vitest / Jest unit test templates |
| `instana-api-client/performance-patterns.md` | 1 | TTL cache helper, parallel-fetch examples, timeout config |
| `instana-api-client/api-doc-template.md` | 1 | README template for documenting API usage patterns |
| `instana-dashboard/dashboard-patterns.md` | 2 | React component skeleton, hooks, React Query templates |
| `instana-dashboard/chart-templates.md` | 2 | Recharts components for error rate, latency, call volume |
| `instana-dashboard/trace-modal-template.md` | 2 | Trace detail modal and span tree renderer |
| `instana-dashboard/dashboard-style-guide.md` | 2 | Colour palette, status conventions, chart rules |
| `instana-trace-analysis/analysis-queries.md` | 3 | Ready-made Instana API request bodies |
| `instana-trace-analysis/analysis-metrics.md` | 3 | Metric formulas, SLO thresholds, root cause heuristics |
| `instana-trace-analysis/analysis-report-template.md` | 3 | Structured Markdown report template |
| `instana-monitoring-setup/setup-checklist.md` | 4 | Pre-deployment checklist |
| `instana-monitoring-setup/env-template.env` | 4 | `.env` template with all variables documented |
