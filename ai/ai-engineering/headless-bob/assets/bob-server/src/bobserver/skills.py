"""
Skills loader for Bob+.

Two discovery modes, checked in order:

1. SUBDIRECTORY skills (preferred):
   skills/<skill-name>/SKILL.md   ← entry point
   - YAML frontmatter between the first pair of --- delimiters
   - Fields: name, description, metadata.{enabled, author, version}
   - The full markdown body becomes the prompt sent to Bob.
   - Sibling files in the same directory are available for Bob to read
     on demand (listed as `context_files` on the skill object).

2. FLAT-FILE skills (legacy / simple):
   skills/<anything>.md           ← must NOT start with _
   - Header comment block:  # Key: value
   - Everything after the header block is the prompt.

The `skills/` directory is resolved relative to this module's package root:
  src/bobserver/skills.py  →  up 4 dirs  →  bobserver/skills/

Files / dirs starting with _ are ignored (_example.md, etc.).
Non-skill root files (CODE_OF_CONDUCT.md, LICENSE.txt) are skipped
if they lack the expected header format — they produce no skill entry.

If the skills/ directory yields no usable skills, the built-in fallbacks
are returned so the UI always has something to show.
"""

from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path

import yaml  # PyYAML — already a transitive dep via pydantic-settings


# ---------------------------------------------------------------------------
# Skills directory
# ---------------------------------------------------------------------------

_SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"
# src/bobserver/skills.py → up 3 → bobserver/ → skills/
# Resolves to: bobserver/skills/


# ---------------------------------------------------------------------------
# Fallback built-in skills (used when skills/ dir has no files)
# ---------------------------------------------------------------------------

_BUILTIN_SKILLS: list[dict] = [
    {
        "id": "analyze-csv",
        "name": "Analyze CSV",
        "description": "Profile order data, identify quality issues, and summarize useful business signals.",
        "workspaceMode": "isolated",
        "safetyProfile": "readonly",
        "maxCoins": 5,
        "contextFiles": [],
        "source": "builtin",
        "prompt": """Read @bob_context.md first if it exists.

Analyze orders_raw.csv and orders.csv in the current isolated workspace without modifying either file.

For each available CSV:
1. Report its columns and row count.
2. Identify missing values, duplicate keys, malformed values, and inconsistent data types.
3. Summarize numeric fields and useful categorical totals.
4. Compare the files and explain material differences.
5. Recommend specific cleanup or validation steps.

Return a concise Markdown analysis. Clearly distinguish observed evidence from recommendations.""",
    },
    {
        "id": "query-sqlite",
        "name": "Query SQLite",
        "description": "Inspect a SQLite database and answer questions with read-only SQL evidence.",
        "workspaceMode": "isolated",
        "safetyProfile": "readonly",
        "maxCoins": 5,
        "contextFiles": [],
        "source": "builtin",
        "prompt": """Read @bob_context.md first if it exists.

Inspect demo.db in the current isolated workspace using read-only SQLite queries. Do not create, update, or delete data.

1. List tables and views.
2. Show the schema for relevant tables.
3. Report row counts.
4. Show a small representative sample.
5. Calculate useful totals or grouped summaries for the available data.
6. Include the exact SELECT statements used as evidence.

If demo.db is unavailable, report that clearly and explain how to create it from orders.csv; do not create it during this run.""",
    },
]


# ---------------------------------------------------------------------------
# YAML frontmatter parser
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """
    Return (meta_dict, body_text).
    If no YAML frontmatter block is found, returns ({}, text).
    """
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        meta = {}
    body = text[m.end():]
    return meta, body


# ---------------------------------------------------------------------------
# Subdirectory skill loader  (skills/<name>/SKILL.md)
# ---------------------------------------------------------------------------

def _load_subdir_skill(skill_dir: Path) -> dict | None:
    """Load a skill from a subdirectory that contains SKILL.md."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return None

    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError:
        return None

    meta, body = _parse_frontmatter(text)
    prompt = body.strip()
    if not prompt:
        return None

    # Skip disabled skills (only when metadata is a dict and enabled is explicitly False)
    metadata_block = meta.get("metadata")
    if isinstance(metadata_block, dict) and metadata_block.get("enabled") is False:
        return None

    skill_id = meta.get("id") or skill_dir.name
    name     = meta.get("name") or skill_id.replace("-", " ").title()
    description = meta.get("description", "").strip()
    if isinstance(description, str) and len(description) > 300:
        # YAML block scalars can be very long — truncate for UI display
        description = description[:297] + "…"

    # Collect sibling context files (non-SKILL.md .md files, recursively)
    context_files: list[str] = []
    for f in sorted(skill_dir.rglob("*.md")):
        if f.name == "SKILL.md":
            continue
        # Relative path from skill dir root
        rel = str(f.relative_to(skill_dir))
        context_files.append(rel)

    return {
        "id": skill_id,
        "name": name,
        "description": description,
        "workspaceMode": "isolated",
        "safetyProfile": "readonly",
        "maxCoins": 20,
        "contextFiles": context_files,
        "source": f"{skill_dir.name}/SKILL.md",
        "prompt": prompt,
    }


# ---------------------------------------------------------------------------
# Flat-file skill loader  (skills/*.md)
# ---------------------------------------------------------------------------

_FLAT_HEADER_RE = re.compile(r"^#\s+([\w]+(?:[\w\s-]*)?):\s*(.+)$")


def _load_flat_skill(md_file: Path) -> dict | None:
    """Parse a legacy flat-file skill (header comment block style)."""
    try:
        text = md_file.read_text(encoding="utf-8")
    except OSError:
        return None

    lines = text.splitlines()
    meta: dict[str, str] = {}
    prompt_lines: list[str] = []
    in_header = True

    for line in lines:
        if in_header and line.startswith("#"):
            m = _FLAT_HEADER_RE.match(line)
            if m:
                key = m.group(1).strip().lower().replace(" ", "_")
                value = m.group(2).strip()
                if key == "skill":
                    key = "name"
                meta[key] = value
        else:
            in_header = False
            prompt_lines.append(line)

    prompt = "\n".join(prompt_lines).strip()
    if not prompt:
        return None

    skill_id = meta.get("id") or md_file.stem
    name = meta.get("name") or skill_id.replace("-", " ").title()
    description = meta.get("description", "")
    safety = meta.get("safetyprofile", meta.get("safety_profile", "readonly"))
    workspace = meta.get("workspacemode", meta.get("workspace_mode", "isolated"))
    try:
        max_coins = int(meta.get("maxcoins", meta.get("max_coins", "10")))
    except ValueError:
        max_coins = 10

    return {
        "id": skill_id,
        "name": name,
        "description": description,
        "workspaceMode": workspace,
        "safetyProfile": safety,
        "maxCoins": max_coins,
        "contextFiles": [],
        "source": md_file.name,
        "prompt": prompt,
    }


# ---------------------------------------------------------------------------
# Main loader — called once at startup, then cached
# ---------------------------------------------------------------------------

_loaded_skills: list[dict] | None = None


def _load_skills() -> list[dict]:
    global _loaded_skills
    if _loaded_skills is not None:
        return _loaded_skills

    skills: list[dict] = []

    if _SKILLS_DIR.is_dir():
        # 1. Subdirectory skills (each subdir with a SKILL.md)
        for entry in sorted(_SKILLS_DIR.iterdir()):
            if not entry.is_dir() or entry.name.startswith("_") or entry.name.startswith("."):
                continue
            skill = _load_subdir_skill(entry)
            if skill:
                skills.append(skill)
                print(f"[skills] loaded subdir: {entry.name} → {skill['name']}")

        # 2. Flat-file skills in the root skills/ dir
        for md_file in sorted(_SKILLS_DIR.glob("*.md")):
            if md_file.name.startswith("_") or md_file.name.startswith("."):
                continue
            # Skip well-known non-skill files
            if md_file.stem.upper() in ("README", "LICENSE", "CHANGELOG", "CODE_OF_CONDUCT"):
                continue
            skill = _load_flat_skill(md_file)
            if skill:
                skills.append(skill)
                print(f"[skills] loaded flat:   {md_file.name} → {skill['name']}")

    if not skills:
        print(f"[skills] no skills found in {_SKILLS_DIR}, using built-ins")
        skills = deepcopy(_BUILTIN_SKILLS)

    _loaded_skills = skills
    return skills


def reload_skills() -> list[dict]:
    """Force a reload from disk (useful for hot-reload in dev)."""
    global _loaded_skills
    _loaded_skills = None
    return _load_skills()


def list_skills() -> list[dict]:
    """Return all loaded skills (copies — safe to mutate)."""
    return deepcopy(_load_skills())


def get_skill(skill_id: str) -> dict | None:
    """Return a single skill by id, or None if not found."""
    return next((s for s in _load_skills() if s["id"] == skill_id), None)
