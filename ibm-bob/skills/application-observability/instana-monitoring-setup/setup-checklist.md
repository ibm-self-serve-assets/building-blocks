# Pre-Deployment Checklist for Instana Monitoring Setup

Work through this list top-to-bottom before considering the integration production-ready.

---

## Environment & Secrets

- [ ] `VITE_INSTANA_BASE_URL` / `INSTANA_BASE_URL` is set and points to the correct unit
- [ ] `VITE_INSTANA_API_TOKEN` / `INSTANA_API_TOKEN` is set and contains a valid token
- [ ] `.env` is present in `.gitignore` — run `git check-ignore -v .env` to confirm
- [ ] No API token appears in any tracked file — run `git grep -r "apiToken"` and verify no results
- [ ] A read-only API token is used (never an admin token in automated scripts)
- [ ] For production React apps: token is NOT embedded in the Vite bundle — a backend proxy is used instead

---

## Client Implementation

- [ ] `InstanaClient` reads config from environment via `getConfig()`, not hardcoded values
- [ ] `validateConnection()` runs successfully against the target Instana unit
- [ ] `ConfigurationError` is thrown immediately at construction if the token is missing
- [ ] All HTTP errors map to typed error classes (`AuthenticationError`, `PermissionError`, `RateLimitError`, `ServerError`)
- [ ] Retry logic is in place for `ServerError` (max 3 attempts, exponential back-off)
- [ ] `Retry-After` header is respected on `429` responses
- [ ] Axios `timeout` is set (default 30 000 ms) — no indefinite hangs

---

## Pagination

- [ ] All list endpoints use the `paginate()` helper (not just the first page)
- [ ] A real endpoint has been tested and `results.length === totalHits`
- [ ] Large datasets (> 1 000 items) have been verified — no memory issues

---

## React Query (Dashboard)

- [ ] All data fetching goes through `useQuery` hooks — no direct API calls in components
- [ ] `staleTime` is set appropriately per query (60 000 ms for stable data, 0 for live data)
- [ ] `isLoading` / `isError` states show a spinner / error message, never a blank panel
- [ ] `refetchInterval` is set for live panels (≥ 30 000 ms to stay within rate limits)
- [ ] Filter changes correctly invalidate related query cache keys

---

## Testing

- [ ] Unit tests exist for every endpoint method and hook
- [ ] Tests cover: 200 success, 401, 403, 429, 500 for each method
- [ ] Pagination test verifies multi-page collection
- [ ] React hook tests cover `isLoading` → `isSuccess` and `isError` states
- [ ] All tests pass: `npm test`
- [ ] No new lint/type errors: `npm run lint` and `tsc --noEmit`

---

## Documentation

- [ ] README documents all required environment variables
- [ ] README includes a "Quick start" section (`npm install` → `.env` setup → `npm run dev`)
- [ ] `env-template.env` is committed so new users know what to set
- [ ] Known rate-limit considerations are documented
- [ ] Production security note (backend proxy for API token) is documented

---

## Final Validation

- [ ] `npx tsx scripts/verify-connection.ts` runs end-to-end without errors
- [ ] At least one real paginated fetch (applications or services) returns the correct total
- [ ] Dashboard loads in a browser and all panels show data
- [ ] Clicking a trace ID opens the detail modal with span tree
- [ ] Filters narrow results correctly and trigger a fresh fetch
