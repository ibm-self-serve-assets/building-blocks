# Error Handling Patterns (TypeScript)

## Error Class Hierarchy

All Instana client errors extend a common `InstanaError` base so callers can catch broadly or narrowly.

```typescript
// src/lib/errors.ts

export class InstanaError extends Error {
  constructor(message: string) {
    super(message);
    this.name = this.constructor.name;
  }
}

export class ConfigurationError extends InstanaError {
  /** Missing or invalid client configuration (e.g. no API token). */
}

export class AuthenticationError extends InstanaError {
  /** HTTP 401 — token is missing, invalid, or expired. */
}

export class PermissionError extends InstanaError {
  /** HTTP 403 — token valid but lacks required scope. */
}

export class RateLimitError extends InstanaError {
  /** HTTP 429 — too many requests. */
  constructor(message: string, public readonly retryAfter: number = 5) {
    super(message);
  }
}

export class ServerError extends InstanaError {
  /** HTTP 5xx — transient Instana server error. */
  constructor(message: string, public readonly statusCode: number) {
    super(message);
  }
}

export class NotFoundError extends InstanaError {
  /** HTTP 404 — requested resource does not exist. */
}
```

---

## Axios Error Mapper

Called in the axios response interceptor to convert HTTP errors into typed classes.

```typescript
// src/lib/errors.ts (continued)
import type { AxiosError } from 'axios';

export function mapAxiosError(err: AxiosError): InstanaError {
  const status = err.response?.status;
  const data   = err.response?.data as Record<string, unknown> | undefined;
  const body   = JSON.stringify(data ?? {});
  const method = err.config?.method?.toUpperCase() ?? 'REQUEST';
  const path   = err.config?.url ?? '';

  // Always log the full response body for 4xx — Instana error messages are in the body,
  // not surfaced by axios by default. This is critical for debugging schema rejections.
  if (status && status >= 400 && status < 500) {
    console.error(`[instana] HTTP ${status} ${method} ${path} — response body:`, data);
  }

  // 400 Bad Request — malformed JSON or wrong field types
  if (status === 400) return new InstanaError(`${method} ${path} → 400 Bad Request: ${body}`);

  // 422 Unprocessable Entity — valid JSON but invalid field values/combinations.
  // Common Instana 422 causes (see endpoint-reference.md for the full correction table):
  //   "group must not be null"      → add group: { groupbyTag: 'service.name' }
  //   "Metric type unknown"          → use metric: 'calls' not 'calls.count'
  if (status === 422) return new InstanaError(`${method} ${path} → 422 Unprocessable: ${body}`);

  if (status === 401) return new AuthenticationError(`${method} ${path} → 401 Unauthorized. Check INSTANA_API_TOKEN.`);
  if (status === 403) return new PermissionError(`${method} ${path} → 403 Forbidden. Token lacks required scope.`);
  if (status === 404) return new NotFoundError(`${method} ${path} → 404 Not Found.`);
  if (status === 429) {
    const retryAfter = Number(err.response?.headers?.['retry-after'] ?? 5);
    return new RateLimitError(`${method} ${path} → 429 Rate Limited. Retry after ${retryAfter}s.`, retryAfter);
  }
  if (status && status >= 500) return new ServerError(`${method} ${path} → ${status}: ${body}`, status);

  // Network error / timeout
  return new InstanaError(err.message ?? 'Unknown network error');
}
```

---

## Retry Logic (Exponential Back-Off)

Apply retries **only** to transient errors (`ServerError`, network timeouts). Never retry `401`, `403`, `404`, or `429` (use `retryAfter` delay instead).

```typescript
// src/lib/retry.ts
import { ServerError, RateLimitError, InstanaError } from './errors';

const RETRY_DELAYS_MS = [1_000, 2_000, 4_000]; // exponential back-off

function sleep(ms: number) { return new Promise(resolve => setTimeout(resolve, ms)); }

export async function withRetry<T>(fn: () => Promise<T>): Promise<T> {
  for (let attempt = 0; attempt <= RETRY_DELAYS_MS.length; attempt++) {
    try {
      return await fn();
    } catch (err) {
      if (err instanceof RateLimitError) {
        console.warn(`[instana] Rate limited — waiting ${err.retryAfter}s`);
        await sleep(err.retryAfter * 1_000);
        return fn(); // single retry after rate-limit delay
      }
      if (err instanceof ServerError && attempt < RETRY_DELAYS_MS.length) {
        const delay = RETRY_DELAYS_MS[attempt];
        console.warn(`[instana] Server error (attempt ${attempt + 1}/${RETRY_DELAYS_MS.length + 1}) — retrying in ${delay}ms`);
        await sleep(delay);
        continue;
      }
      throw err; // AuthenticationError, PermissionError, NotFoundError, final attempt
    }
  }
  throw new InstanaError('All retry attempts exhausted');
}
```

---

## Rules

1. **Never swallow errors silently.** Always `console.error` with the original status and full response body before re-throwing.
2. **Include context.** Error messages must include HTTP method, path, and status code.
3. **Honour Retry-After.** When a `429` is received, read the `retry-after` header and wait before the next attempt.
4. **Fail fast on configuration.** Throw `ConfigurationError` at client construction time, not at first request.
5. **Type your catches.** Use `err instanceof AuthenticationError` — never rely on `err.message` string matching.
6. **Log 4xx bodies.** Instana returns detailed validation messages in the response body for 400 and 422 errors. Always log `err.response?.data` before mapping — this is the only way to see messages like `"group must not be null"` or `"Metric type unknown"`.

---

## HTTP Status Quick Reference

| Status | Class | Meaning | Action |
|--------|-------|---------|--------|
| 400 | `InstanaError` | Malformed request body | Log full body; fix field types |
| 401 | `AuthenticationError` | Invalid/missing API token | Check `INSTANA_API_TOKEN` |
| 403 | `PermissionError` | Token lacks scope | Check token permissions in Instana UI |
| 404 | `NotFoundError` | Resource not found | Verify IDs |
| 422 | `InstanaError` | Invalid field values | Log body — see `endpoint-reference.md` for common causes |
| 429 | `RateLimitError` | Rate limited | Wait `retry-after` seconds |
| 5xx | `ServerError` | Instana server error | Retry with exponential back-off (max 3 attempts) |
