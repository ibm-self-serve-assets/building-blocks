#!/usr/bin/env python3
"""Debug script: inspect each skill directory."""
import sys
import yaml
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

SKILLS_DIR = Path(__file__).parent.parent / "skills"
FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

for entry in sorted(SKILLS_DIR.iterdir()):
    if not entry.is_dir():
        continue
    if entry.name.startswith("_") or entry.name.startswith("."):
        continue
    skill_md = entry / "SKILL.md"
    if not skill_md.is_file():
        print(f"NO-SKILL.MD: {entry.name}")
        continue
    text = skill_md.read_text(encoding="utf-8")
    m = FM_RE.match(text)
    if m:
        try:
            meta = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError as e:
            print(f"YAML-ERROR: {entry.name} → {e}")
            meta = {}
        body = text[m.end():].strip()
    else:
        meta = {}
        body = text.strip()
    has_body = bool(body)
    md_meta = meta.get("metadata")
    print(f"DIR  = {entry.name}")
    print(f"  frontmatter={bool(m)}, has_body={has_body}")
    print(f"  name={meta.get('name')!r}, id={meta.get('id')!r}")
    print(f"  metadata field = {repr(md_meta)}")
    print()
