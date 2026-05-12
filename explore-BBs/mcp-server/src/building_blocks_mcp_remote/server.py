"""
IBM Building Blocks MCP server — Streamable HTTP transport for remote deployment.

Designed for IBM Code Engine. Runs as an HTTP service on port 9247.

Entry point: `building-blocks-mcp-remote` (defined in pyproject.toml scripts).

Environment variables:
  GITHUB_TOKEN   - Optional. GitHub PAT for higher rate limits and code search.
  PORT           - Optional. Override the default port (9247).
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

PORT = int(os.environ.get("PORT", "9247"))

mcp = FastMCP(
    name="building-blocks",
    instructions=(
        "This server provides access to IBM Technology Building Blocks — "
        "pre-built, embeddable capabilities across 3 core areas:\n\n"
        "AI:\n"
        "  - Agents: Agent Builder, Multi-Agent Orchestration, Agentic SDLC\n"
        "  - AI Trust: Model Evaluation, Agent Ops, Real-Time Guardrails, AI Compliance\n\n"
        "Data:\n"
        "  - Integration: Data Pipeline (AI Generated), Data Streaming, Data Observability\n"
        "  - Intelligence: Data Quality, Data Lineage, Text2SQL\n"
        "  - Retrieval: Vector Search, No SQL Database, Zero Copy\n\n"
        "Automation:\n"
        "  - Build and Deploy: iPaaS, Infrastructure as Code, Code Modernization\n"
        "  - Secure: Non-Human Identity, Quantum-Safe Cryptography\n"
        "  - Optimize: Automated Resource Management, FinOps, Automated Resilience & Compliance\n\n"
        "Use these tools to discover building blocks, read documentation, browse code assets, "
        "and find Bob Modes for watsonx Orchestrate."
    ),
    host="0.0.0.0",
    port=PORT,
    stateless_http=True,
)


# Health check endpoint for Code Engine liveness/readiness probes
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


# Tool modules are imported AFTER mcp is created — each module imports `mcp`
# from this file and decorates its functions with @mcp.tool().
from building_blocks_mcp_remote.tools import discover   # noqa: E402, F401
from building_blocks_mcp_remote.tools import details    # noqa: E402, F401
from building_blocks_mcp_remote.tools import docs       # noqa: E402, F401
from building_blocks_mcp_remote.tools import assets     # noqa: E402, F401
from building_blocks_mcp_remote.tools import bob_modes  # noqa: E402, F401


def main() -> None:
    logger.info("Starting building-blocks MCP server (streamable-http, port=%d)", PORT)
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
