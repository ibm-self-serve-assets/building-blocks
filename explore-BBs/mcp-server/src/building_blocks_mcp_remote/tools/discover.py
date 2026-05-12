"""Discovery tools — list and search building blocks."""

from __future__ import annotations

import logging
from typing import Optional

from building_blocks_mcp_remote.server import mcp
from building_blocks_mcp_remote.registry import (
    BUILDING_BLOCKS,
    GROUPS,
    DOCS_PAGES,
    REPO_BASE_URL,
    DOCS_SITE_URL,
)

logger = logging.getLogger(__name__)


@mcp.tool()
def list_building_blocks(
    group: Optional[str] = None,
    capability: Optional[str] = None,
    tag: Optional[str] = None,
) -> dict:
    """List all available IBM Technology Building Blocks, optionally filtered.

    Building Blocks are pre-built, embeddable capabilities organized as:

      AI:
        - "agents"       : Agent Builder, Multi-Agent Orchestration, Agentic SDLC
        - "ai-trust"     : Model Evaluation, Agent Ops, Real-Time Guardrails, AI Compliance

      Data:
        - "integration"  : Data Pipeline (AI Generated), Data Streaming, Data Observability
        - "intelligence" : Data Quality, Data Lineage, Text2SQL
        - "retrieval"    : Vector Search, No SQL Database, Zero Copy

      Automation:
        - "build"        : iPaaS, Infrastructure as Code, Code Modernization
        - "secure"       : Non-Human Identity, Quantum-Safe Cryptography
        - "optimize"     : Automated Resource Management, FinOps, Automated Resilience & Compliance

    Returns a list of building block summaries with id, name, group, description,
    and links to docs and repo.

    Args:
        group: Filter by group. Allowed: "agents", "ai-trust", "integration",
            "intelligence", "retrieval", "build", "secure", "optimize". Omit to list all.
        capability: Filter by core capability. Allowed: "ai", "data", "automation". Omit for all.
        tag: Filter by tag keyword (e.g., "rag", "agents", "terraform"). Case-insensitive partial match.
    """
    try:
        results = []
        for bid, block in BUILDING_BLOCKS.items():
            if group and block["group"] != group:
                continue
            if capability and block["capability"] != capability:
                continue
            if tag:
                tag_lower = tag.lower()
                if not any(tag_lower in t for t in block["tags"]):
                    continue
            results.append({
                "id": bid,
                "name": block["name"],
                "group": block["group"],
                "capability": block["capability"],
                "description": block["description"],
                "products": block["products"],
                "repo_url": f"{REPO_BASE_URL}/tree/main/{block['repo_path']}",
                "docs_url": f"{DOCS_SITE_URL}/{block['docs_path'].replace('.md', '/')}"
                if block.get("docs_path")
                else None,
            })

        group_info = None
        if group and group in GROUPS:
            g = GROUPS[group]
            group_info = {"id": group, "name": g["name"], "description": g["description"]}

        return {
            "status": "success",
            "total": len(results),
            "group_filter": group_info,
            "building_blocks": results,
        }
    except Exception as exc:
        logger.error("list_building_blocks failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}


@mcp.tool()
def search_building_blocks(
    query: str,
    scope: str = "all",
) -> dict:
    """Search across IBM Building Blocks documentation and code.

    Searches through building block names, descriptions, documentation content,
    and README files to find relevant building blocks and content.

    Args:
        query: Search query string. Examples: "RAG pipeline", "Terraform",
            "guardrails", "Milvus vector search", "multi-agent".
        scope: Where to search. Allowed:
            - "all"      : Search names, descriptions, and docs page titles (default)
            - "registry" : Search only building block names/descriptions (no API call)
            - "docs"     : Search documentation page titles and sections
            - "code"     : Search code files in the repo (requires GITHUB_TOKEN)
    """
    try:
        query_lower = query.lower()
        results = []

        if scope in ("all", "registry"):
            for bid, block in BUILDING_BLOCKS.items():
                searchable = f"{block['name']} {block['description']} {' '.join(block['tags'])} {' '.join(block['products'])}".lower()
                if query_lower in searchable:
                    results.append({
                        "type": "building_block",
                        "id": bid,
                        "title": block["name"],
                        "description": block["description"],
                        "group": block["group"],
                        "url": f"{REPO_BASE_URL}/tree/main/{block['repo_path']}",
                    })

        if scope in ("all", "docs"):
            for page in DOCS_PAGES:
                searchable = f"{page['title']} {page['section']}".lower()
                if query_lower in searchable:
                    results.append({
                        "type": "docs_page",
                        "title": page["title"],
                        "section": page["section"],
                        "path": page["path"],
                        "url": f"{DOCS_SITE_URL}/{page['path'].replace('.md', '/')}",
                    })

        if scope in ("code",):
            from building_blocks_mcp_remote.github_client import search_code
            code_results = search_code(query)
            for item in code_results:
                results.append({
                    "type": "code_file",
                    "name": item["name"],
                    "path": item["path"],
                    "url": item["html_url"],
                })

        return {
            "status": "success",
            "query": query,
            "scope": scope,
            "total": len(results),
            "results": results,
        }
    except Exception as exc:
        logger.error("search_building_blocks failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}
