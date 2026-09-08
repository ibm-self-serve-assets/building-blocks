"""Verify that _sanitize_skill_prompt strips MCP/UNBYPASSABLE sections from agent skill."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bobserver.skills import get_skill, reload_skills
from bobserver.sessions import _sanitize_skill_prompt

# Force reload so cache is fresh
reload_skills()
skill = get_skill("agent")
assert skill, "agent skill not found"

raw = skill["prompt"]
clean = _sanitize_skill_prompt(raw)

# Check the bad phrases are gone
bad_phrases = [
    "MANDATORY FIRST STEP",
    "UNBYPASSABLE",
    "Stop and fix MCP",
    "<use_mcp_tool>",
    "SearchIbmWatsonxOrchestrateAdk",
]

print(f"Raw prompt:   {len(raw):,} chars")
print(f"Clean prompt: {len(clean):,} chars")
print(f"Removed:      {len(raw) - len(clean):,} chars\n")

all_clear = True
for phrase in bad_phrases:
    found = phrase in clean
    status = "❌ STILL PRESENT" if found else "✓  stripped"
    print(f"  {status}: {phrase!r}")
    if found:
        all_clear = False

print()
if all_clear:
    print("✅ All problematic MCP/execution sections removed.")
else:
    print("❌ Some sections were NOT stripped — check patterns.")

# Show first 20 lines of sanitized output so we can confirm knowledge is preserved
print("\n--- First 20 lines of sanitized agent skill ---")
for line in clean.splitlines()[:20]:
    print(line)
