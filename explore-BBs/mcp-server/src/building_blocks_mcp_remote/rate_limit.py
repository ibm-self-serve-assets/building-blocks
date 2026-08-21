"""
Per-IP token-bucket rate limiting middleware (Starlette ASGI3).

Protects the shared GitHub API budget from a single client monopolizing the
deployed MCP. Configurable via env var BB_RATE_LIMIT_PER_MIN (default 60).

When the deployment runs behind Code Engine's ingress, the immediate
connection peer is the ingress (same for everyone). To get the actual client
IP we read X-Forwarded-For and take the first hop, which the ingress sets
to the real client.

In-memory, per-instance limiter. With Code Engine auto-scaling to N
instances, the effective per-IP ceiling is N × max_per_minute — still
sufficient protection because most traffic flows through raw.githubusercontent.com
(CDN, not API-rate-limited) and the in-memory catalog cache absorbs duplicates.
A distributed limiter (Redis) is a Tier 3 future enhancement, not needed yet.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Iterable

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """Token-bucket rate limiter, applied per client IP."""

    def __init__(
        self,
        app,
        max_per_minute: int = 60,
        exempt_paths: Iterable[str] = ("/health",),
        bucket_eviction_threshold: int = 10_000,
        idle_eviction_seconds: int = 600,
    ) -> None:
        self.app = app
        self.max_per_minute = max_per_minute
        self.refill_per_sec = max_per_minute / 60.0
        self.exempt_paths = set(exempt_paths)
        self.bucket_eviction_threshold = bucket_eviction_threshold
        self.idle_eviction_seconds = idle_eviction_seconds
        # ip -> (tokens, last_refill_monotonic)
        self._buckets: dict[str, tuple[float, float]] = {}
        self._lock = threading.Lock()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path in self.exempt_paths:
            await self.app(scope, receive, send)
            return

        ip = self._client_ip(scope)
        if not self._take_token(ip):
            logger.warning("rate_limit denied ip=%s path=%s", ip, path)
            await self._send_429(send)
            return

        await self.app(scope, receive, send)

    def _client_ip(self, scope) -> str:
        """Extract real client IP from X-Forwarded-For, fall back to scope.client."""
        for name, value in scope.get("headers", []):
            if name == b"x-forwarded-for":
                return value.decode("latin-1").split(",")[0].strip()
        client = scope.get("client")
        return client[0] if client else "unknown"

    def _take_token(self, ip: str) -> bool:
        now = time.monotonic()
        with self._lock:
            tokens, last = self._buckets.get(ip, (float(self.max_per_minute), now))
            tokens = min(
                float(self.max_per_minute),
                tokens + (now - last) * self.refill_per_sec,
            )
            if tokens < 1.0:
                self._buckets[ip] = (tokens, now)
                return False
            self._buckets[ip] = (tokens - 1.0, now)
            self._maybe_evict(now)
            return True

    def _maybe_evict(self, now: float) -> None:
        """Drop idle buckets when the map grows beyond the threshold."""
        if len(self._buckets) < self.bucket_eviction_threshold:
            return
        cutoff = now - self.idle_eviction_seconds
        self._buckets = {k: v for k, v in self._buckets.items() if v[1] > cutoff}

    async def _send_429(self, send) -> None:
        body = b'{"error":"rate_limit_exceeded","retry_after":60}'
        await send(
            {
                "type": "http.response.start",
                "status": 429,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"retry-after", b"60"),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})
