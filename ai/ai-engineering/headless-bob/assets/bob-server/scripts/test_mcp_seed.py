"""Verify that _seed_mcp_config correctly plants .bob/mcp.json into a run workspace."""
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bobserver.tasks import _seed_mcp_config
from bobserver.config import Settings

settings = Settings()

with tempfile.TemporaryDirectory() as tmp:
    work_dir = Path(tmp) / "work"
    work_dir.mkdir()

    _seed_mcp_config(work_dir, settings)

    mcp_file = work_dir / ".bob" / "mcp.json"
    assert mcp_file.exists(), f".bob/mcp.json was NOT created at {mcp_file}"

    data = json.loads(mcp_file.read_text())
    servers = list(data.get("mcpServers", {}).keys())
    print(f"✓ .bob/mcp.json seeded into run workspace")
    print(f"  Servers: {servers}")
    print(f"  Contents preview:")
    print(f"  {json.dumps(data, indent=2)[:300]}")
