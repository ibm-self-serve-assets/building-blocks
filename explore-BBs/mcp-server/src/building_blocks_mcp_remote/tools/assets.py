"""Asset tools — browse and retrieve code files from building blocks."""

from __future__ import annotations

import logging
import os
from typing import Optional

from building_blocks_mcp_remote.server import mcp
from building_blocks_mcp_remote.registry import BUILDING_BLOCKS, REPO_BASE_URL

logger = logging.getLogger(__name__)

_EXT_LANG = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".yaml": "yaml", ".yml": "yaml", ".json": "json", ".tf": "terraform",
    ".sh": "shell", ".bash": "shell", ".md": "markdown", ".html": "html",
    ".css": "css", ".sql": "sql", ".toml": "toml", ".cfg": "ini",
    ".ini": "ini", ".txt": "text", ".csv": "csv", ".ipynb": "jupyter",
    ".xml": "xml", ".dockerfile": "dockerfile",
}

MAX_INLINE_SIZE = 100_000


@mcp.tool()
def list_assets(
    block_id: str,
    path: Optional[str] = None,
) -> dict:
    """List code assets, configs, and reference implementations for a building block.

    Browse the file tree within a building block's directory. Returns file names,
    types, sizes, and paths for each item.

    Args:
        block_id: Building block identifier (e.g., "agent-builder", "multi-agent-orchestration").
        path: Optional sub-path within the building block directory.
            Omit to list the top-level directory.
            Examples:
            - "assets" to list the assets directory
            - "assets/contextual-knowledge-hub/tools" to browse tool implementations
            - "bob-modes" to list Bob Mode packages
    """
    try:
        block = BUILDING_BLOCKS.get(block_id)
        if not block:
            valid_ids = sorted(BUILDING_BLOCKS.keys())
            return {
                "status": "error",
                "error": f"Unknown block_id '{block_id}'. Valid IDs: {valid_ids}",
            }

        from building_blocks_mcp_remote.github_client import fetch_contents

        repo_path = block["repo_path"]
        full_path = f"{repo_path}/{path}" if path else repo_path

        items = fetch_contents(full_path)
        if not isinstance(items, list):
            return {
                "status": "error",
                "error": f"Path '{full_path}' is a file, not a directory. Use get_asset_file to read it.",
            }

        formatted = []
        for item in items:
            entry = {
                "name": item["name"],
                "type": item["type"],
                "path": item["path"],
            }
            if item["type"] == "file":
                entry["size"] = item.get("size", 0)
            formatted.append(entry)

        return {
            "status": "success",
            "block_id": block_id,
            "path": full_path,
            "total": len(formatted),
            "items": formatted,
        }
    except Exception as exc:
        logger.error("list_assets failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}


@mcp.tool()
def get_asset_file(
    block_id: str,
    file_path: str,
) -> dict:
    """Retrieve the content of a specific code file or config from a building block.

    Fetches the raw content of a file from the building block's repository directory.
    Use list_assets first to discover available files and their paths.

    Supports any text file: Python (.py), YAML (.yaml/.yml), JSON (.json),
    Terraform (.tf), Markdown (.md), shell scripts (.sh), Jupyter notebooks (.ipynb),
    and configuration files.

    Files larger than 100KB return a download URL instead of inline content.

    Args:
        block_id: Building block identifier (e.g., "agent-builder").
        file_path: Path to the file relative to the building block's directory.
            Examples:
            - "assets/contextual-knowledge-hub/tools/cognos_analytics/get_cognos_features.py"
            - "bob-modes/README.md"
            - "assets/AI-Travel-Planner/agents/travel_planner_agent.yaml"
    """
    try:
        block = BUILDING_BLOCKS.get(block_id)
        if not block:
            valid_ids = sorted(BUILDING_BLOCKS.keys())
            return {
                "status": "error",
                "error": f"Unknown block_id '{block_id}'. Valid IDs: {valid_ids}",
            }

        from building_blocks_mcp_remote.github_client import fetch_raw_file, fetch_contents

        repo_path = block["repo_path"]
        full_path = f"{repo_path}/{file_path}"

        try:
            meta = fetch_contents(full_path)
            if isinstance(meta, list):
                return {
                    "status": "error",
                    "error": f"Path '{file_path}' is a directory. Use list_assets to browse it.",
                }
            size = meta.get("size", 0)
        except Exception:
            size = 0

        _, ext = os.path.splitext(file_path)
        language = _EXT_LANG.get(ext.lower(), "text")

        if size > MAX_INLINE_SIZE:
            return {
                "status": "success",
                "block_id": block_id,
                "file_path": file_path,
                "language": language,
                "size": size,
                "content": None,
                "download_url": f"{REPO_BASE_URL}/blob/main/{full_path}",
                "note": f"File exceeds {MAX_INLINE_SIZE // 1000}KB. View or download via the URL.",
            }

        content = fetch_raw_file(full_path)

        return {
            "status": "success",
            "block_id": block_id,
            "file_path": file_path,
            "language": language,
            "size": len(content),
            "content": content,
        }
    except Exception as exc:
        logger.error("get_asset_file failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}
