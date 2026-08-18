# API Client Testing Patterns (Vitest / Jest + TypeScript)

## Setup

```bash
# Vitest (recommended with Vite)
npm install -D vitest @vitest/ui

# Or Jest with ts-jest
npm install -D jest ts-jest @types/jest
```

---

## Unit Test Template (Vitest)

```typescript
// src/lib/__tests__/instanaClient.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import {
  getApplications,
  getTraceDetail,
} from '../instanaClient';
import {
  AuthenticationError,
  RateLimitError,
  ServerError,
  PermissionError,
} from '../errors';

// Mock the axios instance used inside instanaClient
vi.mock('axios');
const mockedAxios = vi.mocked(axios, true);

function mockResponse(status: number, data: unknown, headers: Record<string, string> = {}) {
  return { status, data, headers };
}

function mockAxiosError(status: number, data: unknown = {}, headers: Record<string, string> = {}) {
  const err = Object.assign(new Error('Request failed'), {
    isAxiosError: true,
    response: { status, data, headers },
    config: { method: 'get', url: '/test' },
  });
  return err;
}

describe('getApplications', () => {
  it('returns items on 200', async () => {
    mockedAxios.create.mockReturnValue({
      request: vi.fn().mockResolvedValue(mockResponse(200, {
        items: [{ id: 'app-1', label: 'My App' }],
        totalHits: 1, page: 1, pageSize: 100,
      })),
      interceptors: { response: { use: vi.fn() } },
    } as any);

    const result = await getApplications();
    expect(result).toHaveLength(1);
    expect(result[0].id).toBe('app-1');
  });

  it('throws AuthenticationError on 401', async () => {
    mockedAxios.create.mockReturnValue({
      request: vi.fn().mockRejectedValue(mockAxiosError(401)),
      interceptors: { response: { use: vi.fn() } },
    } as any);

    await expect(getApplications()).rejects.toThrow(AuthenticationError);
  });

  it('throws PermissionError on 403', async () => {
    mockedAxios.create.mockReturnValue({
      request: vi.fn().mockRejectedValue(mockAxiosError(403)),
      interceptors: { response: { use: vi.fn() } },
    } as any);

    await expect(getApplications()).rejects.toThrow(PermissionError);
  });

  it('throws RateLimitError on 429 with retryAfter', async () => {
    mockedAxios.create.mockReturnValue({
      request: vi.fn().mockRejectedValue(mockAxiosError(429, {}, { 'retry-after': '10' })),
      interceptors: { response: { use: vi.fn() } },
    } as any);

    await expect(getApplications()).rejects.toSatisfy(
      (e: RateLimitError) => e instanceof RateLimitError && e.retryAfter === 10
    );
  });

  it('throws ServerError on 500', async () => {
    mockedAxios.create.mockReturnValue({
      request: vi.fn().mockRejectedValue(mockAxiosError(500)),
      interceptors: { response: { use: vi.fn() } },
    } as any);

    await expect(getApplications()).rejects.toThrow(ServerError);
  });
});

describe('pagination', () => {
  it('collects all pages until totalHits is reached', async () => {
    const page1 = { items: [{ id: 'a' }], totalHits: 2, page: 1, pageSize: 1 };
    const page2 = { items: [{ id: 'b' }], totalHits: 2, page: 2, pageSize: 1 };
    let call = 0;
    mockedAxios.create.mockReturnValue({
      request: vi.fn().mockImplementation(() =>
        Promise.resolve(mockResponse(200, call++ === 0 ? page1 : page2))
      ),
      interceptors: { response: { use: vi.fn() } },
    } as any);

    const result = await getApplications();
    expect(result).toHaveLength(2);
  });
});
```

---

## React Hook Test (Vitest + React Testing Library)

```tsx
// src/hooks/__tests__/useInstanaData.test.tsx
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useApplications } from '../useInstanaData';
import * as client from '../../lib/instanaClient';
import { vi } from 'vitest';

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
}

it('useApplications returns data', async () => {
  vi.spyOn(client, 'getApplications').mockResolvedValue([{ id: 'a1', label: 'My App' }]);

  const { result } = renderHook(() => useApplications(), { wrapper });
  await waitFor(() => expect(result.current.isSuccess).toBe(true));
  expect(result.current.data).toHaveLength(1);
});

it('useApplications surfaces errors', async () => {
  vi.spyOn(client, 'getApplications').mockRejectedValue(new Error('API down'));

  const { result } = renderHook(() => useApplications(), { wrapper });
  await waitFor(() => expect(result.current.isError).toBe(true));
});
```

---

## Test Coverage Checklist

For every new endpoint method or hook, cover:

- [ ] Success path (200) — assert returned data shape
- [ ] Authentication failure (401) — assert `AuthenticationError` thrown
- [ ] Permission denied (403) — assert `PermissionError` thrown
- [ ] Rate limit (429) — assert `RateLimitError` with correct `retryAfter`
- [ ] Server error (500) — assert `ServerError` thrown
- [ ] Pagination — assert all pages collected, `results.length === totalHits`
- [ ] React hook `isLoading` → `isSuccess` transition
- [ ] React hook `isError` state when fetch fails
