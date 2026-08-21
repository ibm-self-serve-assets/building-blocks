"""Discovery tools — list and search building blocks. Backed by data_loader (markdown catalog)."""

from __future__ import annotations

import logging
from typing import Optional

from building_blocks_mcp_remote.data_loader import (
    DOCS_SITE_URL,
    REPO_BASE_URL,
    load_registry,
)
from building_blocks_mcp_remote.server import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
def list_building_blocks(
    group: Optional[str] = None,
    capability: Optional[str] = None,
    tag: Optional[str] = None,
) -> dict:
    """List all available IBM Technology Building Blocks, optionally filtered.

    Building Blocks are pre-built, embeddable capabilities organized as
    3 core capabilities → 8 groups → individual blocks. The response is the
    source of truth for which blocks exist — the catalog changes over time.

    Args:
        group: Filter by group. Valid values: "agents", "ai-trust" (AI);
            "integration", "intelligence", "retrieval" (Data);
            "build", "secure", "optimize" (Automation). Omit to list all.
        capability: Filter by core capability ("ai", "data", "automation"). Omit for all.
        tag: Case-insensitive partial match against any tag (e.g., "rag", "terraform").
    """
    try:
        reg = load_registry()
        blocks = reg["BUILDING_BLOCKS"]
        groups = reg["GROUPS"]

        results = []
        for bid, block in blocks.items():
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
        if group and group in groups:
            g = groups[group]
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

    Searches names, descriptions, docs page titles, and optionally code files.

    Args:
        query: Search query string. Examples: "RAG pipeline", "Terraform", "multi-agent".
        scope: One of:
            - "all"      : names + descriptions + docs page titles (default)
            - "registry" : only block names/descriptions (no API call)
            - "docs"     : docs page titles and sections
            - "code"     : code files in the repo (requires GITHUB_TOKEN)
    """
    try:
        reg = load_registry()
        blocks = reg["BUILDING_BLOCKS"]
        docs_pages = reg["DOCS_PAGES"]

        # Token-based matching: a multi-word query matches if ANY word hits,
        # ranked by how many words hit (exact-phrase matches rank highest).
        # Literal substring-only matching made e.g. "RAG agent guardrails"
        # return zero results even though three blocks matched individually.
        query_lower = query.lower()
        tokens = query_lower.split()

        def score(searchable: str) -> int:
            s = sum(1 for t in tokens if t in searchable)
            if len(tokens) > 1 and query_lower in searchable:
                s += len(tokens)  # phrase match beats scattered words
            return s

        scored: list[tuple[int, dict]] = []

        if scope in ("all", "registry"):
            for bid, block in blocks.items():
                searchable = (
                    f"{block['name']} {block['description']} "
                    f"{' '.join(block['tags'])} {' '.join(block['products'])}"
                ).lower()
                if (s := score(searchable)):
                    scored.append((s, {
                        "type": "building_block",
                        "id": bid,
                        "title": block["name"],
                        "description": block["description"],
                        "group": block["group"],
                        "url": f"{REPO_BASE_URL}/tree/main/{block['repo_path']}",
                    }))

        if scope in ("all", "docs"):
            for page in docs_pages:
                searchable = f"{page['title']} {page['section']}".lower()
                if (s := score(searchable)):
                    scored.append((s, {
                        "type": "docs_page",
                        "title": page["title"],
                        "section": page["section"],
                        "path": page["path"],
                        "url": f"{DOCS_SITE_URL}/{page['path'].replace('.md', '/')}",
                    }))

        scored.sort(key=lambda x: -x[0])
        results = [r for _, r in scored]

        if scope == "code":
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
