"""Documentation tools — browse and fetch docs site pages."""

from __future__ import annotations

import logging
from typing import Optional

from building_blocks_mcp_remote.data_loader import (
    DOCS_REPO_NAME,
    DOCS_SITE_URL,
    load_registry,
)
from building_blocks_mcp_remote.server import mcp

logger = logging.getLogger(__name__)


@mcp.tool()
def list_docs_pages(
    section: Optional[str] = None,
) -> dict:
    """List all documentation pages from the IBM Building Blocks docs site.

    No external API calls — uses the markdown-driven docs-pages catalog.

    Args:
        section: Filter by section keyword (e.g., "agents", "trust", "data",
            "retrieval", "build", "secure", "optimize", "bob"). Omit to list all.
            Case-insensitive partial match on section name or title.
    """
    try:
        reg = load_registry()
        docs_pages = reg["DOCS_PAGES"]

        if section:
            section_lower = section.lower()
            pages = [
                {**page, "url": f"{DOCS_SITE_URL}/{page['path'].replace('.md', '/')}"}
                for page in docs_pages
                if section_lower in page["section"].lower()
                or section_lower in page["title"].lower()
            ]
        else:
            pages = [
                {**page, "url": f"{DOCS_SITE_URL}/{page['path'].replace('.md', '/')}"}
                for page in docs_pages
            ]

        return {
            "status": "success",
            "total": len(pages),
            "pages": pages,
        }
    except Exception as exc:
        logger.error("list_docs_pages failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}


@mcp.tool()
def get_docs_page(
    page_path: str,
) -> dict:
    """Fetch the content of a documentation page from the Building Blocks docs site.

    Args:
        page_path: Path to the docs page (e.g., "ai-core/agents/agent-builder.md").
            Use list_docs_pages to see all valid paths.
    """
    try:
        reg = load_registry()
        docs_pages = reg["DOCS_PAGES"]

        known_paths = {p["path"] for p in docs_pages}
        if page_path not in known_paths:
            return {
                "status": "error",
                "error": f"Unknown page_path '{page_path}'. Use list_docs_pages to see valid paths.",
                "valid_paths": sorted(known_paths),
            }

        from building_blocks_mcp_remote.github_client import fetch_raw_file
        content = fetch_raw_file(f"docs-src/{page_path}", repo=DOCS_REPO_NAME)

        return {
            "status": "success",
            "path": page_path,
            "url": f"{DOCS_SITE_URL}/{page_path.replace('.md', '/')}",
            "content": content,
        }
    except Exception as exc:
        logger.error("get_docs_page failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}
