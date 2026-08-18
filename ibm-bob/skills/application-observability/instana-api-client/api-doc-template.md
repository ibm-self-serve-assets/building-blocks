# API Usage Documentation Template

Copy this template into your project README (or a dedicated `docs/instana-api.md` file) and fill in each section.

---

## Instana API Integration

### Overview

> _One-paragraph description of what this integration does, which Instana unit it connects to, and what data it retrieves._

**Instana unit:** `https://<unit>.instana.io`
**API version:** Instana REST API v1
**Authentication:** API token (`Authorization: apiToken <token>`)

---

### Requirements

| Requirement | Details |
|-------------|---------|
| API token scope | Read access to Application Monitoring (and Infrastructure / Events if used) |
| Node.js | >= 18 |
| React | >= 18 (for dashboard) |
| Key dependencies | `axios`, `@tanstack/react-query`, `recharts` (see `package.json`) |

---

### Environment Variables

**Vite / React app** — prefix with `VITE_`:

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_INSTANA_BASE_URL` | ✅ Yes | Base URL of your Instana unit, e.g. `https://myunit.instana.io` |
| `VITE_INSTANA_API_TOKEN` | ✅ Yes | API token with read access. Generate in Instana → Settings → API Tokens. |
| `VITE_INSTANA_TIMEOUT_MS` | No | HTTP timeout in ms (default: 30000) |
| `VITE_INSTANA_MAX_RETRIES` | No | Max retry attempts for 5xx errors (default: 3) |

**Node.js scripts** — no prefix:

| Variable | Required | Description |
|----------|----------|-------------|
| `INSTANA_BASE_URL` | ✅ Yes | Base URL of your Instana unit |
| `INSTANA_API_TOKEN` | ✅ Yes | API token with read access |

Copy `instana-monitoring-setup/env-template.env` to `.env` and fill in your values. **Never commit `.env`.**

> ⚠️ Vite embeds `VITE_*` variables into the browser bundle at build time. Never put secrets in `VITE_*` variables for production deployments — use a backend proxy instead.

---

### Endpoints Used

| Method | Path | Purpose | Paginated |
|--------|------|---------|-----------|
| `GET` | `/api/instana/health` | Connection validation | No |
| `GET` | `/api/application-monitoring/applications` | List all applications | Yes |
| `GET` | `/api/application-monitoring/services` | List services for an application | Yes |
| `POST` | `/api/application-monitoring/analyze/call-groups` | Aggregate error rates, latency, call volume | No |
| `POST` | `/api/application-monitoring/analyze/traces` | Fetch trace list with filters | Yes |
| `GET` | `/api/application-monitoring/analyze/traces/{traceId}` | Fetch full trace call tree | No |
| `GET` | `/api/events` | Fetch events in a time window | No |

> _Add or remove rows to match the endpoints your integration actually uses._

---

### Request / Response Examples

#### List Applications

```bash
curl -s \
  -H "Authorization: apiToken $INSTANA_API_TOKEN" \
  "$INSTANA_BASE_URL/api/application-monitoring/applications?pageSize=50&page=1"
```

```json
{
  "items": [
    { "id": "abc123", "label": "My App", "types": ["SERVICES"] }
  ],
  "page": 1,
  "pageSize": 50,
  "totalHits": 1
}
```

#### Fetch Error Call Groups

```bash
curl -s -X POST \
  -H "Authorization: apiToken $INSTANA_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "timeFrame": { "to": 0, "windowSize": 3600000 },
    "tagFilters": [
      { "name": "application.name", "operator": "EQUALS", "value": "My App" },
      { "name": "call.erroneous", "operator": "EQUALS", "value": "true" }
    ],
    "groupByTags": ["service.name"],
    "metrics": [{ "aggregation": "SUM", "metric": "calls.count" }]
  }' \
  "$INSTANA_BASE_URL/api/application-monitoring/analyze/call-groups"
```

---

### Error Codes

| HTTP Status | Error Class | Meaning | Action |
|-------------|------------|---------|--------|
| `401` | `AuthenticationError` | Invalid or missing API token | Check `INSTANA_API_TOKEN` |
| `403` | `PermissionError` | Token lacks required scope | Add read permissions in Instana Settings |
| `404` | `NotFoundError` | Resource does not exist | Verify the ID or path |
| `429` | `RateLimitError` | Too many requests | Client waits for `retryAfter` seconds automatically |
| `5xx` | `ServerError` | Transient Instana server error | Client retries up to 3 times with exponential back-off |

---

### Rate Limits

Instana enforces per-token rate limits. The client logs remaining quota automatically:

- `console.warn` when `X-RateLimit-Remaining < 5`
- `console.debug` when `X-RateLimit-Remaining < 10`
- `429` responses trigger an automatic `retryAfter`-second wait

To stay within limits: rely on React Query's `staleTime` for stable data (application/service lists), and avoid `refetchInterval` values shorter than 30 seconds for live panels.

---

### Pagination

All list endpoints return a paginated envelope:

```json
{ "items": [...], "page": 1, "pageSize": 50, "totalHits": 200 }
```

The `paginate()` helper in `instana-api-client/api-patterns.md` automatically collects all pages. Do not call list endpoints directly without pagination — you will only see the first page.
