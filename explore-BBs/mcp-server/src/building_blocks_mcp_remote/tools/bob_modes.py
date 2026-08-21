"""Bob Modes tools — discover and inspect Bob Modes for watsonx Orchestrate."""

from __future__ import annotations

import logging
from typing import Optional

from building_blocks_mcp_remote.data_loader import REPO_BASE_URL, load_registry
from building_blocks_mcp_remote.server import mcp

logger = logging.getLogger(__name__)

@mcp.tool()
def list_bob_modes(
    block_id: Optional[str] = None,
) -> dict:
    """List available Bob Modes (watsonx Orchestrate custom configuration packages).

    A "Bob Mode" is any directory inside a `bob-modes/` subtree that contains
    one or more .zip files. Discovery walks every nesting level under each
    building block's repo path.

    Args:
        block_id: Filter by building block (e.g., "agent-builder"). Omit to list across all blocks.
    """
    try:
        reg = load_registry()
        blocks = reg["BUILDING_BLOCKS"]

        if block_id and block_id not in blocks:
            valid_ids = sorted(blocks.keys())
            return {
                "status": "error",
                "error": f"Unknown block_id '{block_id}'. Valid IDs: {valid_ids}",
            }

        from building_blocks_mcp_remote.github_client import fetch_tree

        # The full git tree is already in hand — every block is checked
        # against it directly, so blocks that ship modes are discovered
        # without any hardcoded list to maintain.
        target_blocks = {block_id} if block_id else set(blocks)
        tree = fetch_tree()

        # Group every .zip under any */bob-modes/* path by its containing directory.
        modes_by_dir: dict[str, list[str]] = {}
        for item in tree:
            if item.get("type") != "blob":
                continue
            p = item["path"]
            if not p.endswith(".zip"):
                continue
            if "/bob-modes/" not in p:
                continue
            mode_dir, zip_name = p.rsplit("/", 1)
            modes_by_dir.setdefault(mode_dir, []).append(zip_name)

        all_modes = []
        for bid in sorted(target_blocks):
            block = blocks.get(bid)
            if not block:
                continue
            rp = block["repo_path"]
            for mode_dir, zip_names in modes_by_dir.items():
                if not (mode_dir == rp or mode_dir.startswith(f"{rp}/")):
                    continue
                mode_name = mode_dir.rsplit("/", 1)[-1]
                mode_type = "base" if "base" in mode_dir.lower() else "custom"
                all_modes.append({
                    "name": mode_name,
                    "block_id": bid,
                    "type": mode_type,
                    "path": mode_dir,
                    "zip_files": sorted(zip_names),
                    "repo_url": f"{REPO_BASE_URL}/tree/main/{mode_dir}",
                })

        if block_id and not all_modes:
            return {
                "status": "success",
                "total": 0,
                "bob_modes": [],
                "note": f"No Bob Modes (bob-modes/.../*.zip) found for '{block_id}'",
            }

        return {
            "status": "success",
            "total": len(all_modes),
            "bob_modes": all_modes,
        }
    except Exception as exc:
        logger.error("list_bob_modes failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}


@mcp.tool()
def get_bob_mode_info(
    block_id: str,
    mode_name: str,
) -> dict:
    """Get detailed information about a specific Bob Mode, including its README.

    Args:
        block_id: Building block identifier (e.g., "agent-builder").
        mode_name: Name of the Bob Mode (e.g., "agent-builder-base-mode",
            "domain-agent-builder", "voice-agent-builder").
            Use list_bob_modes to see all available modes.
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

        from building_blocks_mcp_remote.github_client import fetch_raw_file, fetch_tree

        repo_path = block["repo_path"]
        tree = fetch_tree()
        mode_path = None
        for item in tree:
            if (
                item.get("type") == "tree"
                and item["path"].startswith(f"{repo_path}/")
                and "/bob-modes/" in item["path"]
                and item["path"].endswith(f"/{mode_name}")
            ):
                mode_path = item["path"]
                break

        if not mode_path:
            return {
                "status": "error",
                "error": f"Bob Mode '{mode_name}' not found under '{block_id}'. Use list_bob_modes to see available modes.",
            }

        readme = None
        for readme_name in ("README.md", "Readme.md"):
            try:
                readme = fetch_raw_file(f"{mode_path}/{readme_name}")
                break
            except Exception:
                pass

        files = [
            {"name": item["path"].split("/")[-1], "path": item["path"]}
            for item in tree
            if item["path"].startswith(f"{mode_path}/") and item["type"] == "blob"
        ]

        zip_url = None
        for f in files:
            if f["name"].endswith(".zip"):
                zip_url = f"https://raw.githubusercontent.com/ibm-self-serve-assets/building-blocks/main/{f['path']}"
                break

        return {
            "status": "success",
            "block_id": block_id,
            "mode_name": mode_name,
            "path": mode_path,
            "repo_url": f"{REPO_BASE_URL}/tree/main/{mode_path}",
            "readme": readme,
            "files": files,
            "zip_download_url": zip_url,
        }
    except Exception as exc:
        logger.error("get_bob_mode_info failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}


@mcp.tool()
def download_bob_mode(
    block_id: str,
    mode_name: str,
) -> dict:
    """Get the direct download URL for a Bob Mode ZIP file.

    Args:
        block_id: Building block identifier (e.g., "agent-builder").
        mode_name: Name of the Bob Mode. Use list_bob_modes to see available modes.
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

        from building_blocks_mcp_remote.github_client import fetch_tree

        repo_path = block["repo_path"]
        tree = fetch_tree()

        mode_path = None
        for item in tree:
            if (
                item.get("type") == "tree"
                and item["path"].startswith(f"{repo_path}/")
                and "/bob-modes/" in item["path"]
                and item["path"].endswith(f"/{mode_name}")
            ):
                mode_path = item["path"]
                break

        if not mode_path:
            return {
                "status": "error",
                "error": f"Bob Mode '{mode_name}' not found under '{block_id}'. Use list_bob_modes to see available modes.",
            }

        zip_files = [
            item["path"]
            for item in tree
            if item["path"].startswith(f"{mode_path}/")
            and item["type"] == "blob"
            and item["path"].endswith(".zip")
        ]

        if not zip_files:
            return {
                "status": "error",
                "error": f"No ZIP file found for Bob Mode '{mode_name}'. Browse the mode at: {REPO_BASE_URL}/tree/main/{mode_path}",
            }

        zip_path = zip_files[0]
        zip_name = zip_path.split("/")[-1]
        download_url = f"https://raw.githubusercontent.com/ibm-self-serve-assets/building-blocks/main/{zip_path}"

        return {
            "status": "success",
            "block_id": block_id,
            "mode_name": mode_name,
            "zip_file": zip_name,
            "download_url": download_url,
            "instructions": "Download the ZIP from the URL above, then extract and install the Bob Mode in watsonx Orchestrate.",
        }
    except Exception as exc:
        logger.error("download_bob_mode failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}
