"""
Streamable HTTP MCP Server for IBM Code Engine (MCP Python SDK FastMCP)

Fixes 421 "Invalid Host header" by configuring MCP transport security allowed_hosts.

Endpoints:
- /mcp     MCP Streamable HTTP endpoint (provided by MCP SDK)
- /health  Health check
- /        Basic info

Optional auth:
- APP_BEARER_TOKEN
  - If unset: auth disabled
  - If set: require Authorization: Bearer <token> for /mcp, /health, /
"""

from __future__ import annotations

import os
import platform
import socket
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings


SERVER_NAME = os.getenv("SERVER_NAME", "base-mcp-server")
SERVER_VERSION = os.getenv("SERVER_VERSION", "1.0.0")
SERVER_DESCRIPTION = os.getenv(
    "SERVER_DESCRIPTION",
    "Base MCP Server for Data for AI Building Block",
)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

APP_BEARER_TOKEN: Optional[str] = os.getenv("APP_BEARER_TOKEN", "").strip() or None

# Public URL of this deployment (recommended to set in Code Engine)
# Example:
#   PUBLIC_BASE_URL=https://base-mcp-server-data-for-ai.<id>.us-east.codeengine.appdomain.cloud
PUBLIC_BASE_URL: Optional[str] = os.getenv("PUBLIC_BASE_URL", "").strip() or None

# Comma-separated allowlists (optional overrides)
# Example:
#   ALLOWED_HOSTS=localhost:*,127.0.0.1:*,base-mcp-server-data-for-ai.<id>.us-east.codeengine.appdomain.cloud:*
#   ALLOWED_ORIGINS=http://localhost:*,https://base-mcp-server-data-for-ai.<id>.us-east.codeengine.appdomain.cloud:*
ALLOWED_HOSTS_ENV: str = os.getenv("ALLOWED_HOSTS", "").strip()
ALLOWED_ORIGINS_ENV: str = os.getenv("ALLOWED_ORIGINS", "").strip()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_server_info() -> Dict[str, Any]:
    return {
        "hostname": socket.gethostname(),
        "server_time": utc_now_iso(),
        "timezone": "UTC",
        "server_name": SERVER_NAME,
        "server_version": SERVER_VERSION,
        "description": SERVER_DESCRIPTION,
        "environment": ENVIRONMENT,
        "platform": platform.system(),
        "platform_release": platform.release(),
        "python_version": platform.python_version(),
    }


def _split_csv(value: str) -> List[str]:
    items: List[str] = []
    for part in value.split(","):
        p = part.strip()
        if p:
            items.append(p)
    return items


def _host_from_public_url(public_url: str) -> Optional[str]:
    try:
        parsed = urlparse(public_url)
        if parsed.hostname:
            return parsed.hostname
    except Exception:
        return None
    return None


def build_transport_security() -> TransportSecuritySettings:
    """
    Configure DNS rebinding protection allowlists to avoid 421 Invalid Host header.
    See MCP Python SDK guidance. :contentReference[oaicite:1]{index=1}
    """
    # Defaults always safe for local dev
    allowed_hosts: List[str] = ["localhost:*", "127.0.0.1:*"]

    # Add Code Engine hostname if provided
    if PUBLIC_BASE_URL:
        host = _host_from_public_url(PUBLIC_BASE_URL)
        if host:
            allowed_hosts.append(f"{host}:*")

    # Allow explicit overrides
    if ALLOWED_HOSTS_ENV:
        allowed_hosts = _split_csv(ALLOWED_HOSTS_ENV)

    # Origins are mainly relevant if you use browser-based MCP clients.
    # mcp-proxy does not need origins, but setting them doesn't hurt.
    allowed_origins: List[str] = ["http://localhost:*", "http://127.0.0.1:*"]
    if PUBLIC_BASE_URL:
        parsed = urlparse(PUBLIC_BASE_URL)
        if parsed.scheme and parsed.hostname:
            allowed_origins.append(f"{parsed.scheme}://{parsed.hostname}:*")

    if ALLOWED_ORIGINS_ENV:
        allowed_origins = _split_csv(ALLOWED_ORIGINS_ENV)

    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
    )


class OptionalBearerAuthMiddleware(BaseHTTPMiddleware):
    """
    Optional auth:
      - If APP_BEARER_TOKEN is unset -> allow all
      - If set -> require Authorization: Bearer <token> for /mcp, /health, /
    """

    def __init__(self, app: ASGIApp, token: Optional[str]) -> None:
        super().__init__(app)
        self._token = token

    async def dispatch(self, request: Request, call_next):
        if not self._token:
            return await call_next(request)

        path = request.url.path
        protected = (path == "/") or (path == "/health") or path.startswith("/mcp")
        if protected:
            auth = request.headers.get("authorization", "")
            expected = f"Bearer {self._token}"
            if auth != expected:
                return JSONResponse(
                    status_code=401,
                    content={
                        "error": "Unauthorized",
                        "message": "Missing or invalid Authorization header",
                    },
                )

        return await call_next(request)


# --- MCP Server (MCP Python SDK FastMCP) ---
transport_security = build_transport_security()

mcp = FastMCP(
    name=SERVER_NAME,
    stateless_http=True,
    transport_security=transport_security,
)


@mcp.tool(description="Get information about the server including hostname, time, environment, and platform")
def get_server_info() -> Dict[str, Any]:
    return build_server_info()


@mcp.tool(description="Get the current server time in UTC timezone")
def get_server_time() -> Dict[str, str]:
    return {"server_time": utc_now_iso(), "timezone": "UTC"}


@mcp.tool(description="Get the server hostname")
def get_hostname() -> Dict[str, str]:
    return {"hostname": socket.gethostname()}


# MCP Streamable HTTP ASGI app (provides /mcp)
app = mcp.streamable_http_app()

# Optional auth middleware
app.add_middleware(OptionalBearerAuthMiddleware, token=APP_BEARER_TOKEN)


# Extra endpoints (non-MCP)
async def health(_: Request) -> Response:
    return JSONResponse(
        {
            "status": "healthy",
            "server": SERVER_NAME,
            "version": SERVER_VERSION,
            "description": SERVER_DESCRIPTION,
            "timestamp": utc_now_iso(),
        }
    )


async def index(_: Request) -> Response:
    return JSONResponse(
        {
            "server": SERVER_NAME,
            "version": SERVER_VERSION,
            "description": SERVER_DESCRIPTION,
            "environment": ENVIRONMENT,
            "public_base_url": PUBLIC_BASE_URL,
            "endpoints": {
                "health": "/health",
                "mcp": "/mcp",
            },
            "auth": {
                "enabled": bool(APP_BEARER_TOKEN),
                "header": "Authorization: Bearer <token>" if APP_BEARER_TOKEN else None,
            },
            "transport_security": {
                "dns_rebinding_protection": True,
                "allowed_hosts": transport_security.allowed_hosts,
                "allowed_origins": transport_security.allowed_origins,
            },
            "tools": ["get_server_info", "get_server_time", "get_hostname"],
        }
    )


app.add_route("/", index, methods=["GET"])
app.add_route("/health", health, methods=["GET"])


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
