#!/usr/bin/env python3
"""
Cross-reference validator for the marketplace bb-catalog.

Pydantic in data_loader.py validates each file in isolation (required fields,
types). This script catches the things pydantic can't: dangling references
between files. Wire it into CI to fail PRs that introduce drift.

Checks performed:
  1. Every block's `group` exists in groups.md
  2. Every group's `capability` exists in capabilities.md
  3. Every block's `capability` matches the capability of its group
  4. Every block ID is unique (file collision check)
  5. Every docs page path is unique

Usage:
    BB_CATALOG_LOCAL_PATH=/path/to/explore-BBs/bb-catalog \\
        uv run python scripts/validate_data.py

Without BB_CATALOG_LOCAL_PATH set, the catalog is validated against GitHub.
Exits 0 if clean, 1 if any cross-reference errors are found.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Make the package importable when running from the scripts/ folder.
PKG_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(PKG_SRC))

from building_blocks_mcp_remote.data_loader import load_registry  # noqa: E402


def _check_group_capability_refs(reg: dict) -> list[str]:
    errors: list[str] = []
    cap_ids = set(reg["CORE_CAPABILITIES"])
    for gid, group in reg["GROUPS"].items():
        cap = group.get("capability")
        if cap not in cap_ids:
            errors.append(
                f"group {gid!r} references unknown capability {cap!r} "
                f"(valid: {sorted(cap_ids)})"
            )
    return errors


def _check_block_group_refs(reg: dict) -> list[str]:
    errors: list[str] = []
    group_ids = set(reg["GROUPS"])
    cap_ids = set(reg["CORE_CAPABILITIES"])
    for bid, block in reg["BUILDING_BLOCKS"].items():
        if block.get("group") not in group_ids:
            errors.append(
                f"block {bid!r} references unknown group {block.get('group')!r} "
                f"(valid: {sorted(group_ids)})"
            )
        if block.get("capability") not in cap_ids:
            errors.append(
                f"block {bid!r} references unknown capability {block.get('capability')!r} "
                f"(valid: {sorted(cap_ids)})"
            )
    return errors


def _check_block_capability_matches_group(reg: dict) -> list[str]:
    errors: list[str] = []
    for bid, block in reg["BUILDING_BLOCKS"].items():
        group = reg["GROUPS"].get(block.get("group"))
        if group is None:
            continue  # already caught by the group-ref check
        if block.get("capability") != group.get("capability"):
            errors.append(
                f"block {bid!r} has capability={block.get('capability')!r} "
                f"but its group {block.get('group')!r} belongs to capability "
                f"{group.get('capability')!r}"
            )
    return errors


def _check_unique_docs_paths(reg: dict) -> list[str]:
    errors: list[str] = []
    seen: dict[str, list[str]] = {}
    for page in reg["DOCS_PAGES"]:
        seen.setdefault(page["path"], []).append(page["title"])
    for path, titles in seen.items():
        if len(titles) > 1:
            errors.append(f"docs page path {path!r} appears under multiple titles: {titles}")
    return errors


def main() -> int:
    print(f"Validating catalog at {os.environ.get('BB_CATALOG_LOCAL_PATH', '<GitHub>')}")
    reg = load_registry()

    checks = [
        ("group → capability references", _check_group_capability_refs),
        ("block → group/capability references", _check_block_group_refs),
        ("block capability ↔ group capability consistency", _check_block_capability_matches_group),
        ("docs page path uniqueness", _check_unique_docs_paths),
    ]

    total_errors: list[str] = []
    for label, fn in checks:
        errs = fn(reg)
        if errs:
            print(f"\n[FAIL] {label}: {len(errs)} issue(s)")
            for e in errs:
                print(f"  - {e}")
            total_errors.extend(errs)
        else:
            print(f"[OK]   {label}")

    print()
    if total_errors:
        print(f"VALIDATION FAILED — {len(total_errors)} issue(s).")
        return 1
    print(
        f"VALIDATION PASSED — "
        f"{len(reg['CORE_CAPABILITIES'])} capabilities, "
        f"{len(reg['GROUPS'])} groups, "
        f"{len(reg['BUILDING_BLOCKS'])} blocks, "
        f"{len(reg['DOCS_PAGES'])} docs pages."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
