"""
IBM Building Blocks MCP server (marketplace edition) — Streamable HTTP for remote deployment.

Catalog data is loaded from markdown files in explore-BBs/bb-catalog/ in the
main building-blocks repo (live-fetched from GitHub, or read from local disk
in dev mode). Catalog updates ship by PR — no server redeploy required.

Same 11 tools as the v1 production server, but backed by markdown instead of
a hardcoded registry.py. Designed to back the Bob mode submitted to the IBM
Bob modes marketplace.

Entry point: `building-blocks-mcp-remote-marketplace` (defined in pyproject.toml).

Environment variables:
  GH_APP_ID                Optional. GitHub App ID for App-based auth (preferred).
  GH_APP_INSTALLATION_ID   Optional. Installation ID on the target org.
  GH_APP_PRIVATE_KEY       Optional. PEM private key (raw or base64-encoded).
  GITHUB_TOKEN             Optional. Personal access token (fallback if GH_APP_* unset).
  PORT                     Optional. Override the default port (9248).
  BB_CATALOG_LOCAL_PATH    Optional. Path to a local bb-catalog/ for testing
                           without GitHub. Bypasses cache.
  BB_ADMIN_TOKEN           Optional. Shared secret to protect /admin/reload-data.
  BB_RATE_LIMIT_PER_MIN    Optional. Per-IP rate limit (default 60).
"""

import logging
import os
import sys

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

# All logging goes to stderr — stdout is reserved for MCP protocol messages.
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)

# Default port differs from v1 (9247) so both can run side-by-side on the same host.
PORT = int(os.environ.get("PORT", "9248"))

mcp = FastMCP(
    name="building-blocks-marketplace",
    instructions=(
        "IBM Technology Building Blocks discovery server (marketplace edition). "
        "Catalog is loaded live from markdown files at explore-BBs/bb-catalog/ "
        "in the building-blocks repo — content updates ship by PR.\n\n"
        "Building Blocks are pre-built, embeddable capabilities organized as "
        "3 core capabilities → 8 groups → individual blocks:\n"
        "  AI: agents, ai-trust\n"
        "  Data: integration, intelligence, retrieval\n"
        "  Automation: build, secure, optimize\n\n"
        "The set of blocks changes over time — always call list_building_blocks "
        "for the current catalog; never assume block names from memory.\n\n"
        "Tools: discover and search blocks, fetch READMEs and docs pages, browse "
        "code assets, and find/download two kinds of installable packages: Bob "
        "Modes (workspace configurations you switch into) and Bob skills "
        "(expertise packages that install side by side)."
    ),
    host="0.0.0.0",
    port=PORT,
    stateless_http=True,
)


# Health check for Code Engine liveness/readiness probes.
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "version": "explorer"})


# Admin endpoint to force a catalog reload (escape hatch for the 5-min cache).
# Protected by a shared secret if BB_ADMIN_TOKEN is set.
@mcp.custom_route("/admin/reload-data", methods=["POST"])
async def reload_data(request: Request) -> JSONResponse:
    expected = os.environ.get("BB_ADMIN_TOKEN")
    if expected:
        provided = request.headers.get("X-Admin-Token", "")
        if provided != expected:
            return JSONResponse({"status": "error", "error": "unauthorized"}, status_code=401)
    from building_blocks_mcp_remote.data_loader import invalidate, load_registry

    invalidate()
    reg = load_registry()
    return JSONResponse(
        {
            "status": "ok",
            "reloaded": True,
            "counts": {
                "capabilities": len(reg["CORE_CAPABILITIES"]),
                "groups": len(reg["GROUPS"]),
                "blocks": len(reg["BUILDING_BLOCKS"]),
                "docs_pages": len(reg["DOCS_PAGES"]),
            },
        }
    )


# Tool modules import `mcp` from this file and decorate their functions.
# Imports must happen AFTER mcp is created.
from building_blocks_mcp_remote.tools import discover    # noqa: E402, F401
from building_blocks_mcp_remote.tools import details     # noqa: E402, F401
from building_blocks_mcp_remote.tools import docs        # noqa: E402, F401
from building_blocks_mcp_remote.tools import assets      # noqa: E402, F401
from building_blocks_mcp_remote.tools import bob_modes   # noqa: E402, F401
from building_blocks_mcp_remote.tools import skills      # noqa: E402, F401


def main() -> None:
    import uvicorn

    from building_blocks_mcp_remote.rate_limit import RateLimitMiddleware

    logger.info("Starting building-blocks-marketplace MCP server (streamable-http, port=%d)", PORT)
    if os.environ.get("BB_CATALOG_LOCAL_PATH"):
        logger.info("Catalog source: LOCAL DISK (BB_CATALOG_LOCAL_PATH is set)")
    else:
        logger.info("Catalog source: GitHub (live fetch with 5-min cache)")

    # Build the ASGI app and wrap with per-IP rate limiting before serving.
    # Health is exempt so Code Engine liveness probes don't burn the budget.
    rate_limit = int(os.environ.get("BB_RATE_LIMIT_PER_MIN", "60"))
    logger.info("Per-IP rate limit: %d req/min (exempt: /health)", rate_limit)

    app = mcp.streamable_http_app()
    app.add_middleware(RateLimitMiddleware, max_per_minute=rate_limit, exempt_paths={"/health"})

    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")


if __name__ == "__main__":
    main()
