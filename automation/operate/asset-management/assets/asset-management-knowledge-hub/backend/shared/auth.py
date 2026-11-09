"""Shared-secret API-key authentication for the backend services.

A pure ASGI middleware (so it never buffers Server-Sent-Event streams) that
rejects every request lacking the configured ``API_KEY``. It fails closed: if no
key is configured, every non-exempt request is refused.

The key is accepted as ``X-API-Key: <key>`` or ``Authorization: Bearer <key>``.
``/health`` and CORS pre-flight ``OPTIONS`` requests are exempt.
"""

from __future__ import annotations

import hmac
import json
import os

from shared.logging import get_logger

logger = get_logger(__name__)

_EXEMPT_PATHS = {"/health"}


class ApiKeyMiddleware:
    def __init__(self, app, api_key: str | None = None) -> None:
        self.app = app
        self._key = (api_key if api_key is not None else os.environ.get("API_KEY", "")).encode()
        if not self._key:
            logger.error("API_KEY is not set — all non-health requests will be rejected")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] == "OPTIONS" or scope["path"] in _EXEMPT_PATHS:
            await self.app(scope, receive, send)
            return

        if self._authorised(scope):
            await self.app(scope, receive, send)
            return

        body = json.dumps({"detail": "Unauthorized"}).encode()
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode()),
                (b"www-authenticate", b"Bearer"),
            ],
        })
        await send({"type": "http.response.body", "body": body})

    def _authorised(self, scope) -> bool:
        if not self._key:
            return False
        presented = b""
        for name, value in scope["headers"]:
            if name == b"x-api-key":
                presented = value
                break
            if name == b"authorization" and value[:7].lower() == b"bearer ":
                presented = value[7:].strip()
                break
        return hmac.compare_digest(presented, self._key)
