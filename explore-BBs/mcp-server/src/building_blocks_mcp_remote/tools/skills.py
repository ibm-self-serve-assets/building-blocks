"""Bob skills tools — list, inspect, and download Bob skills.

Backed by the generated skills catalog (bb-catalog/skills/ in the
building-blocks repo, produced by sync_skills.py). Skills are the most
current per-block technical capability; recommend them alongside Bob Modes.
"""

from __future__ import annotations

import logging
from typing import Optional

from building_blocks_mcp_remote.data_loader import load_registry
from building_blocks_mcp_remote.server import mcp

logger = logging.getLogger(__name__)


def _first_sentence(text: str, limit: int = 220) -> str:
    head = text.split(". ", 1)[0].strip()
    if len(head) > limit:
        head = head[: limit - 1].rstrip() + "…"
    return head + ("." if head and not head.endswith((".", "…")) else "")


def _install_instructions(skill: dict) -> str:
    """Layout-aware install recipe for the skill's download zip."""
    layout = "bare"  # generated skill-archives/ zips use the bare layout
    dl = skill.get("download") or ""
    for src in skill.get("sources", []):
        if src["path"].endswith(".zip") and dl.endswith(src["path"]):
            layout = src["layout"]
            break
    if layout == "bob":
        return (
            "Unzip at the project root — the archive already contains "
            ".bob/skills/<skill-name>/. Reload Bob to pick up the skill."
        )
    if layout == "skills":
        return (
            "Unzip; the archive has a top-level skills/ folder. Move the "
            "folder(s) INSIDE skills/ into the project's .bob/skills/ "
            "directory (create it if missing) — not the skills/ wrapper "
            "itself. Reload Bob to pick up the skill."
        )
    if layout == "nested":
        return (
            "Unzip; inside the archive's top-level folder there is a "
            "skills/ directory. Move the folder(s) INSIDE that skills/ "
            "directory into the project's .bob/skills/ (not the outer "
            "wrapper and not the skills/ folder itself). Reload Bob to "
            "pick up the skill."
        )
    return (
        "Unzip, then move the archive's top-level folder into the project's "
        ".bob/skills/ directory (create it if missing). Reload Bob to pick up the skill."
    )


@mcp.tool()
def list_skills(
    block_id: Optional[str] = None,
    query: Optional[str] = None,
) -> dict:
    """List available Bob skills (installable expertise packages for Bob).

    Skills are folders of instructions and reference material that extend
    Bob's capabilities for a specific technology (e.g., "agent-ops",
    "rag-pipeline-builder", "infrastructure-as-code-terraform"). Unlike Bob
    Modes (which reconfigure Bob wholesale), several skills can be installed
    side by side. Returns summaries — use get_skill for full descriptions.

    Args:
        block_id: Filter to skills belonging to one building block
            (e.g., "agent-ops", "rag", "text2sql"). Omit to list all.
        query: Case-insensitive substring match against skill id, name,
            description, and block ids (e.g., "terraform", "maximo", "vault").
    """
    try:
        reg = load_registry()
        skills = reg.get("SKILLS", {})
        blocks_reg = reg.get("BUILDING_BLOCKS", {})

        results = []
        for sid, s in sorted(skills.items()):
            if block_id and block_id not in s["blocks"]:
                continue
            if query:
                haystack = " ".join(
                    [sid, s["name"], s["description"], " ".join(s["blocks"])]
                ).lower()
                if query.lower() not in haystack:
                    continue
            # Authoritative capability from the owning block(s) — so clients
            # never have to guess which domain a skill belongs to.
            caps = sorted({
                blocks_reg[b]["capability"] for b in s["blocks"] if b in blocks_reg
            })
            results.append({
                "id": sid,
                "name": s["name"],
                "blocks": s["blocks"],
                "capability": (caps[0] if len(caps) == 1 else (caps or ["cross-cutting"])[0] if caps else "cross-cutting"),
                "summary": _first_sentence(s["description"]),
                "downloadable": bool(s.get("download")),
            })

        return {
            "status": "success",
            "count": len(results),
            "skills": results,
            "hint": "Use get_skill(skill_id) for the full description and install info.",
        }
    except Exception as exc:
        logger.error("list_skills failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}


@mcp.tool()
def get_skill(skill_id: str) -> dict:
    """Get full details for one Bob skill: complete description (written as
    'use when...' guidance — good for matching skills to a user's problem),
    owning building blocks, sub-skills, and download availability.

    Args:
        skill_id: Skill identifier from list_skills (e.g., "agent-ops",
            "rag-pipeline-builder", "qse").
    """
    try:
        reg = load_registry()
        skills = reg.get("SKILLS", {})

        skill = skills.get(skill_id)
        if not skill:
            return {
                "status": "error",
                "error": f"Unknown skill_id {skill_id!r}. Valid ids: {sorted(skills)}",
            }

        return {
            "status": "success",
            "skill": {
                "id": skill_id,
                "name": skill["name"],
                "description": skill["description"],
                "blocks": skill["blocks"],
                "subskills": skill["subskills"],
                "status": skill["status"],
                "downloadable": bool(skill.get("download")),
            },
        }
    except Exception as exc:
        logger.error("get_skill failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}


@mcp.tool()
def download_skill(skill_id: str) -> dict:
    """Get the direct download URL and install instructions for a Bob skill.

    Args:
        skill_id: Skill identifier (e.g., "agent-ops"). Use list_skills to
            discover available skills.
    """
    try:
        reg = load_registry()
        skills = reg.get("SKILLS", {})

        skill = skills.get(skill_id)
        if not skill:
            return {
                "status": "error",
                "error": f"Unknown skill_id {skill_id!r}. Valid ids: {sorted(skills)}",
            }
        if not skill.get("download"):
            return {
                "status": "error",
                "error": f"Skill {skill_id!r} has no downloadable archive yet.",
            }

        return {
            "status": "success",
            "skill_id": skill_id,
            "download_url": skill["download"],
            "instructions": _install_instructions(skill),
        }
    except Exception as exc:
        logger.error("download_skill failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}
