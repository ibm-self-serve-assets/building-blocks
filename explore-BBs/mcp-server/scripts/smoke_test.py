#!/usr/bin/env python3
"""
Smoke test: exercises all 14 MCP tools in-process plus the offline-fallback
path. Catalog comes from BB_CATALOG_LOCAL_PATH if set (recommended for dev),
else live GitHub. Content fetches (READMEs, assets, trees) always hit GitHub —
unauthenticated works, GITHUB_TOKEN raises the rate limit.

Usage:
    BB_CATALOG_LOCAL_PATH=/path/to/explore-BBs/bb-catalog \
        uv run python scripts/smoke_test.py

Exits 0 if every tool returns status=success (and error paths error cleanly).
"""

from __future__ import annotations

import sys
from pathlib import Path

PKG_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(PKG_SRC))

FAILURES: list[str] = []


def check(label: str, result: dict, expect: str = "success", detail=None) -> None:
    ok = result.get("status") == expect
    print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail(result)}" if ok and detail else ""))
    if not ok:
        FAILURES.append(f"{label}: {result}")


def main() -> int:
    from building_blocks_mcp_remote.tools.discover import list_building_blocks, search_building_blocks
    from building_blocks_mcp_remote.tools.details import get_building_block, get_building_block_readme
    from building_blocks_mcp_remote.tools.docs import list_docs_pages, get_docs_page
    from building_blocks_mcp_remote.tools.assets import list_assets, get_asset_file
    from building_blocks_mcp_remote.tools.bob_modes import list_bob_modes, get_bob_mode_info, download_bob_mode
    from building_blocks_mcp_remote.tools.skills import list_skills, get_skill, download_skill

    # --- catalog-driven tools (no GitHub content calls) ---
    check("list_building_blocks()", list_building_blocks(),
          detail=lambda r: f"{r['total']} blocks")
    check("list_building_blocks(group=retrieval)", list_building_blocks(group="retrieval"),
          detail=lambda r: f"{r['total']} blocks")
    check("search_building_blocks(rag, registry)", search_building_blocks("rag", scope="registry"),
          detail=lambda r: f"{r['total']} hits")

    # Multi-word search must tokenize (a literal-phrase match returns zero
    # hits for queries like this — regression guard for the ranked search).
    multi = search_building_blocks("RAG agent guardrails", scope="registry")
    check("search tokenizes multi-word query", multi,
          detail=lambda r: f"{r['total']} hits")
    if multi.get("total", 0) == 0:
        FAILURES.append("multi-word search returned zero hits — tokenization regressed")
        print("FAIL  multi-word search returned hits > 0")
    phrase = search_building_blocks("vector search", scope="registry")
    top = (phrase.get("results") or [{}])[0].get("id")
    if top != "vector-search":
        FAILURES.append(f"phrase ranking regressed — top hit for 'vector search' is {top!r}")
        print(f"FAIL  phrase match ranks first (got {top!r})")
    else:
        print("PASS  phrase match ranks first — 'vector search' -> vector-search")

    # Cross-cutting skills are reachable only via query (blocks: []) —
    # regression guard for the Step 4 query sweep.
    sweep = list_skills(query="ibm cloud")
    if any(s["id"] == "ibm-cloud" for s in sweep.get("skills", [])):
        print("PASS  query sweep reaches cross-cutting skill (ibm-cloud)")
    else:
        FAILURES.append("list_skills(query='ibm cloud') did not surface the cross-cutting skill")
        print("FAIL  query sweep reaches cross-cutting skill (ibm-cloud)")
    check("list_docs_pages()", list_docs_pages(),
          detail=lambda r: f"{r['total']} pages")
    check("list_skills()", list_skills(),
          detail=lambda r: f"{r['count']} skills")
    check("list_skills(block_id=rag)", list_skills(block_id="rag"),
          detail=lambda r: ", ".join(s["id"] for s in r["skills"]))
    check("get_skill(agent-ops)", get_skill("agent-ops"))
    check("download_skill(ibm-cloud)", download_skill("ibm-cloud"),
          detail=lambda r: r["download_url"].rsplit("/", 1)[-1])
    check("get_skill(bad-id) errors cleanly", get_skill("no-such-skill"), expect="error")

    # --- GitHub-content tools (network) ---
    check("get_building_block(rag)", get_building_block("rag", include_readme=True),
          detail=lambda r: f"readme {len(r['block'].get('readme') or '')} chars")
    check("get_building_block_readme(agent-builder)", get_building_block_readme("agent-builder"))
    check("get_docs_page(agent-builder)", get_docs_page("ai-core/agents/agent-builder.md"))
    check("list_assets(rag)", list_assets("rag"))
    check("get_asset_file(rag README)", get_asset_file("rag", "README.md"))
    modes = list_bob_modes(block_id="rag")
    check("list_bob_modes(rag)", modes, detail=lambda r: f"{r['total']} modes")
    if modes.get("bob_modes"):
        mode = modes["bob_modes"][0]["name"]
        check(f"get_bob_mode_info(rag, {mode})", get_bob_mode_info("rag", mode))
        check(f"download_bob_mode(rag, {mode})", download_bob_mode("rag", mode),
              detail=lambda r: r["zip_file"])

    # --- offline fallback path ---
    import building_blocks_mcp_remote.data_loader as dl
    import os
    local = os.environ.pop(dl.LOCAL_PATH_ENV, None)
    real_build = dl._build_registry
    dl._build_registry = lambda: (_ for _ in ()).throw(RuntimeError("simulated GitHub outage"))
    dl.invalidate()
    try:
        reg = dl.load_registry()
        ok = bool(reg.get("BUILDING_BLOCKS")) and bool(reg.get("SKILLS"))
        print(f"{'PASS' if ok else 'FAIL'}  cold-start fallback snapshot — "
              f"{len(reg.get('BUILDING_BLOCKS', {}))} blocks, {len(reg.get('SKILLS', {}))} skills")
        if not ok:
            FAILURES.append("fallback snapshot empty")
    except Exception as exc:
        print(f"FAIL  cold-start fallback snapshot — raised {exc}")
        FAILURES.append(f"fallback: {exc}")
    finally:
        dl._build_registry = real_build
        dl.invalidate()
        if local:
            os.environ[dl.LOCAL_PATH_ENV] = local

    print()
    if FAILURES:
        print(f"SMOKE TEST FAILED — {len(FAILURES)} failure(s)")
        for f in FAILURES:
            print(f"  - {f[:200]}")
        return 1
    print("SMOKE TEST PASSED — all tools healthy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
