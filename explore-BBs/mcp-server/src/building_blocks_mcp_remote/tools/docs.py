"""Documentation tools — browse and fetch docs site pages."""

from __future__ import annotations

import logging
from typing import Optional

from building_blocks_mcp_remote.server import mcp
from building_blocks_mcp_remote.registry import (
    DOCS_PAGES,
    DOCS_REPO_NAME,
    DOCS_SITE_URL,
)

logger = logging.getLogger(__name__)


@mcp.tool()
def list_docs_pages(
    section: Optional[str] = None,
) -> dict:
    """List all documentation pages from the IBM Building Blocks docs site.

    Returns the complete navigation structure of the documentation.
    No API calls — uses the static page catalog.

    Args:
        section: Filter by section keyword. Examples:
            - "agents"     : Agent-related pages
            - "trust"      : AI Trust pages
            - "data"       : Data pages
            - "retrieval"  : Retrieval pages (vector search, NoSQL, zero-copy)
            - "build"      : Build and Deploy pages
            - "secure"     : Secure pages (non-human identity, quantum-safe)
            - "optimize"   : Optimization pages
            - "bob"        : IBM Bob pages
            Omit to list all pages. Case-insensitive partial match on section name.
    """
    try:
        if section:
            section_lower = section.lower()
            pages = [
                {**page, "url": f"{DOCS_SITE_URL}/{page['path'].replace('.md', '/')}"}
                for page in DOCS_PAGES
                if section_lower in page["section"].lower()
                or section_lower in page["title"].lower()
            ]
        else:
            pages = [
                {**page, "url": f"{DOCS_SITE_URL}/{page['path'].replace('.md', '/')}"}
                for page in DOCS_PAGES
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

    Retrieves the raw markdown content of a specific docs page. Use list_docs_pages
    to discover available page paths.

    The docs site covers architecture, concepts, prerequisites, and getting-started
    guides for each building block — often with more detail than the repo READMEs.

    Args:
        page_path: Path to the docs page. Examples:
            - "ai-core/agents/agent-builder.md"
            - "data-core/query/vector-search/index.md"
            - "automation-core/optimize/finops.md"
            - "ibm-bob/index.md"
            Use list_docs_pages to see all valid paths.
    """
    try:
        known_paths = {p["path"] for p in DOCS_PAGES}
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
