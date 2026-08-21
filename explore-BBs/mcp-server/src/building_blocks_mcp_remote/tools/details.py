"""Detail tools — get comprehensive info about a specific building block."""

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
def get_building_block(
    block_id: str,
    include_readme: bool = True,
) -> dict:
    """Get comprehensive details about a specific IBM Building Block.

    Returns metadata, README content, available assets, and links. Use
    list_building_blocks first to discover available block IDs.

    Args:
        block_id: Building block identifier (e.g., "agent-builder").
        include_readme: If True, fetch and include the full README from the repo.
            Set False for a faster metadata-only response.
    """
    try:
        reg = load_registry()
        blocks = reg["BUILDING_BLOCKS"]

        block = blocks.get(block_id)
        if not block:
            valid_ids = sorted(blocks.keys())
            return {
                "status": "error",
                "error": f"Unknown block_id '{block_id}'. Valid IDs: {valid_ids}",
            }

        repo_path = block["repo_path"]

        result: dict = {
            "id": block_id,
            "name": block["name"],
            "group": block["group"],
            "capability": block["capability"],
            "description": block["description"],
            "products": block["products"],
            "tags": block["tags"],
            "repo_url": f"{REPO_BASE_URL}/tree/main/{repo_path}",
            "docs_url": f"{DOCS_SITE_URL}/{block['docs_path'].replace('.md', '/')}"
            if block.get("docs_path")
            else None,
        }

        if include_readme:
            from building_blocks_mcp_remote.github_client import fetch_raw_file
            try:
                readme = fetch_raw_file(f"{repo_path}/README.md")
                result["readme"] = readme
            except Exception:
                try:
                    readme = fetch_raw_file(f"{repo_path}/Readme.md")
                    result["readme"] = readme
                except Exception:
                    result["readme"] = None
                    result["readme_note"] = "README not found at expected path"
        else:
            result["readme"] = None

        from building_blocks_mcp_remote.github_client import fetch_contents
        try:
            items = fetch_contents(repo_path)
            if isinstance(items, list):
                result["contents"] = [
                    {"name": i["name"], "type": i["type"]} for i in items
                ]
        except Exception:
            result["contents"] = []

        return {"status": "success", "block": result}
    except Exception as exc:
        logger.error("get_building_block failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}


@mcp.tool()
def get_building_block_readme(
    block_id: str,
    sub_path: Optional[str] = None,
) -> dict:
    """Get the README content for a building block or one of its sub-components.

    Args:
        block_id: Building block identifier (e.g., "agent-builder").
        sub_path: Optional sub-path within the building block directory to fetch
            a nested README. Examples:
            - "assets/contextual-knowledge-hub" for an asset's README
            - "bob-modes" for the Bob Modes README
            - "assets/AI-Travel-Planner" for a reference implementation
            If omitted, fetches the top-level README.
    """
    try:
        reg = load_registry()
        blocks = reg["BUILDING_BLOCKS"]

        block = blocks.get(block_id)
        if not block:
            valid_ids = sorted(blocks.keys())
            return {
                "status": "error",
                "error": f"Unknown block_id '{block_id}'. Valid IDs: {valid_ids}",
            }

        from building_blocks_mcp_remote.github_client import fetch_raw_file

        repo_path = block["repo_path"]
        if sub_path:
            full_path = f"{repo_path}/{sub_path}/README.md"
        else:
            full_path = f"{repo_path}/README.md"

        try:
            content = fetch_raw_file(full_path)
        except Exception:
            alt_path = full_path.replace("README.md", "Readme.md")
            try:
                content = fetch_raw_file(alt_path)
                full_path = alt_path
            except Exception:
                return {
                    "status": "error",
                    "error": f"README not found at '{full_path}' or '{alt_path}'",
                }

        return {
            "status": "success",
            "block_id": block_id,
            "path": full_path,
            "content": content,
        }
    except Exception as exc:
        logger.error("get_building_block_readme failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}
