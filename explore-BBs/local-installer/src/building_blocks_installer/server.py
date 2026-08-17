"""
Local installer MCP server (stdio) for the Building Blocks Explorer Bob mode.

The Explorer's remote MCP server is the brain (catalog, skills, modes,
download URLs); this tiny local server is the hands. It exists because Bob
builds do not reliably ship a shell tool — without it, "Bob helps you get
started" would end in "please run this script yourself."

Deliberately scoped — this is NOT a shell:
  - Four fixed operations; no command execution of any kind.
  - Downloads only from the official building-blocks repository
    (https://raw.githubusercontent.com/ibm-self-serve-assets/building-blocks/).
  - Writes only inside the current workspace (the directory Bob launches the
    server in): `.bob/` for installs, `*.png` at the root for diagrams.

Tools:
    install_skill(skill_id, download_url)   -> place skill at .bob/skills/<id>/
    install_bob_mode(mode_slug, zip_url)    -> merge a Bob mode into .bob/
    render_diagram(mermaid_code, filename)  -> fetch PNG from mermaid.ink
    verify_install()                        -> report workspace .bob/ state
"""

from __future__ import annotations

import base64
import io
import logging
import shutil
import urllib.request
import zipfile
from pathlib import Path

import yaml
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

ALLOWED_URL_PREFIX = (
    "https://raw.githubusercontent.com/ibm-self-serve-assets/building-blocks/"
)
MERMAID_INK = "https://mermaid.ink/img/"
MAX_DOWNLOAD_BYTES = 100 * 1024 * 1024  # 100 MB safety cap
HTTP_TIMEOUT = 60
USER_AGENT = "building-blocks-installer/0.1.2"

_JUNK_PARTS = {"__MACOSX", ".DS_Store"}

def _resolve_workspace(workspace_root: str | None) -> Path:
    """Resolve the workspace directory.

    Bob does not reliably launch MCP servers with cwd set to the workspace
    (observed: cwd == "/"), so tools accept an explicit workspace_root.
    Guardrails: must be absolute, not the filesystem root, and must already
    contain a .bob/ directory (proof it is a real Bob workspace).
    """
    if workspace_root:
        p = Path(workspace_root).expanduser().resolve()
        if str(p) == p.anchor:
            raise ValueError("workspace_root must not be the filesystem root")
        if not (p / ".bob").is_dir():
            raise ValueError(
                f"workspace_root {p} has no .bob/ directory — pass the Bob "
                "workspace's absolute path"
            )
        return p
    cwd = Path.cwd().resolve()
    if str(cwd) != cwd.anchor and (cwd / ".bob").is_dir():
        return cwd
    raise ValueError(
        "cannot determine the workspace: pass workspace_root=<absolute path "
        "of the current Bob workspace> (the server was launched with "
        f"cwd={cwd}, which is not a workspace)"
    )

mcp = FastMCP(
    name="building-blocks-installer",
    instructions=(
        "Local installer for the Building Blocks Explorer. Installs Bob "
        "skills and Bob modes into THIS workspace and renders architecture "
        "diagrams. Get download URLs from the building-blocks catalog "
        "server's download_skill / download_bob_mode tools."
    ),
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _workspace_path(ws: Path, *parts: str) -> Path:
    """Resolve a path inside the workspace; refuse anything that escapes it."""
    p = (ws / Path(*parts)).resolve()
    if p != ws and ws not in p.parents:
        raise ValueError(f"path escapes the workspace: {p}")
    return p


def _download(url: str) -> bytes:
    if not url.startswith(ALLOWED_URL_PREFIX):
        raise ValueError(
            f"URL not allowed. Downloads are restricted to {ALLOWED_URL_PREFIX}"
        )
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        data = resp.read(MAX_DOWNLOAD_BYTES + 1)
    if len(data) > MAX_DOWNLOAD_BYTES:
        raise ValueError("download exceeds the 100MB safety cap")
    return data


def _is_junk(name: str) -> bool:
    return any(part in _JUNK_PARTS for part in name.split("/"))


def _zip_entries(data: bytes) -> tuple[zipfile.ZipFile, list[str]]:
    zf = zipfile.ZipFile(io.BytesIO(data))
    names = [n for n in zf.namelist() if not _is_junk(n) and not n.endswith("/")]
    return zf, names


def _extract_tree(zf: zipfile.ZipFile, names: list[str], strip: str, dest: Path) -> int:
    """Extract entries under `strip` into dest, preserving relative layout."""
    count = 0
    for n in names:
        if not n.startswith(strip):
            continue
        rel = n[len(strip):]
        if not rel:
            continue
        target = (dest / rel).resolve()
        if dest.resolve() not in target.parents and target != dest.resolve():
            raise ValueError(f"zip entry escapes destination: {n}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(zf.read(n))
        count += 1
    return count


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def install_skill(skill_id: str, download_url: str, workspace_root: str = "") -> dict:
    """Download a Bob skill zip and install it at .bob/skills/<skill_id>/.

    Handles every known zip layout automatically (.bob/skills/-prefixed,
    skills/-wrapped, or bare top-level folder). Replaces any existing copy
    of the skill cleanly (no stale files left from older versions).

    Args:
        skill_id: The skill's catalog id (from list_skills / download_skill).
        download_url: The zip URL from the catalog server's download_skill.
            Must be under the official building-blocks repository.
        workspace_root: Absolute path of the current Bob workspace (the
            folder containing .bob/). ALWAYS pass this.
    """
    try:
        ws = _resolve_workspace(workspace_root)
        data = _download(download_url)
        zf, names = _zip_entries(data)

        skill_mds = sorted(
            (n for n in names if n.endswith("SKILL.md")), key=lambda n: (n.count("/"), n)
        )
        if not skill_mds:
            return {"status": "error", "error": "zip contains no SKILL.md — not a skill package"}

        # Layout-agnostic root (mirrors the catalog generator): the common
        # ancestor of every SKILL.md, stepped up out of structural wrapper
        # folders. Handles all observed layouts including nested wrappers
        # and composite multi-sub-skill zips.
        import posixpath
        dirs = [posixpath.dirname(n) for n in skill_mds]
        root_dir = dirs[0]
        for d in dirs[1:]:
            root_dir = posixpath.commonpath([root_dir, d])
        while root_dir and posixpath.basename(root_dir) in ("skills", ".bob"):
            root_dir = posixpath.dirname(root_dir)
        if not root_dir:
            return {"status": "error", "error": "zip carries multiple top-level skills — unsupported"}
        inner = posixpath.basename(root_dir)
        strip = root_dir + "/"

        dest = _workspace_path(ws, ".bob", "skills", skill_id)
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True)
        count = _extract_tree(zf, names, strip, dest)

        # Root SKILL.md for normal skills; composite skills carry their
        # SKILL.mds one level down — either satisfies verification.
        if not (dest / "SKILL.md").is_file() and not any(dest.rglob("SKILL.md")):
            shutil.rmtree(dest)
            return {
                "status": "error",
                "error": f"install verification failed: no SKILL.md under .bob/skills/{skill_id}/ after extraction",
            }
        return {
            "status": "success",
            "skill_id": skill_id,
            "installed_at": f".bob/skills/{skill_id}/",
            "files": count,
            "note": "Active after Bob reloads." + (
                "" if inner == skill_id
                else f" (zip's internal folder name was {inner!r}; installed under the catalog id)"
            ),
        }
    except Exception as exc:
        logger.error("install_skill failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}


@mcp.tool()
def install_bob_mode(mode_slug: str, zip_url: str, workspace_root: str = "") -> dict:
    """Download a Bob mode zip and merge it into THIS workspace's .bob/.

    Appends the mode entry to custom_modes.yaml, copies the mode's rules and
    asset folders, and merges its MCP servers into .bob/mcp.json. Mirrors the
    manual merge flow the Explorer documented for shell-capable environments.

    Args:
        mode_slug: The mode's slug (e.g., "agent-builder-base-mode").
        zip_url: The zip URL from the catalog server's download_bob_mode.
        workspace_root: Absolute path of the current Bob workspace. ALWAYS pass this.
    """
    try:
        ws = _resolve_workspace(workspace_root)
        data = _download(zip_url)
        zf, names = _zip_entries(data)

        cm_candidates = sorted(
            (n for n in names if n.endswith(".bob/custom_modes.yaml")),
            key=lambda n: n.count("/"),
        )
        if not cm_candidates:
            return {"status": "error", "error": "zip has no .bob/custom_modes.yaml — not a Bob mode package"}
        bob_root = cm_candidates[0][: -len("custom_modes.yaml")]  # ends with ".bob/"

        # 1. Append the mode entry (everything after the customModes: header).
        incoming = zf.read(cm_candidates[0]).decode("utf-8", errors="replace")
        try:
            incoming_modes = yaml.safe_load(incoming)["customModes"]
        except Exception:
            return {"status": "error", "error": "could not parse the mode's custom_modes.yaml"}
        ours_path = _workspace_path(ws, ".bob", "custom_modes.yaml")
        ours = yaml.safe_load(ours_path.read_text(encoding="utf-8")) if ours_path.is_file() else None
        ours = ours or {"customModes": []}
        existing_slugs = {m.get("slug") for m in ours["customModes"]}
        added_modes = [m for m in incoming_modes if m.get("slug") not in existing_slugs]
        ours["customModes"].extend(added_modes)
        ours_path.parent.mkdir(parents=True, exist_ok=True)
        ours_path.write_text(
            yaml.safe_dump(ours, sort_keys=False, allow_unicode=True, width=100),
            encoding="utf-8",
        )

        # 2. Copy rules/asset folders (everything except the two config files).
        copied: set[str] = set()
        for n in names:
            if not n.startswith(bob_root):
                continue
            rel = n[len(bob_root):]
            top = rel.split("/")[0]
            if rel in ("custom_modes.yaml", "mcp.json", ".mcp.json") or not rel:
                continue
            target = _workspace_path(ws, ".bob", rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zf.read(n))
            copied.add(top)

        # 3. Merge mcpServers into our mcp.json.
        import json

        merged_servers = []
        our_mcp_path = _workspace_path(ws, ".bob", "mcp.json")
        our_mcp = {"mcpServers": {}}
        if our_mcp_path.is_file():
            our_mcp = json.loads(our_mcp_path.read_text(encoding="utf-8"))
        for candidate in (f"{bob_root}mcp.json", f"{bob_root}.mcp.json"):
            if candidate in zf.namelist():
                theirs = json.loads(zf.read(candidate).decode("utf-8"))
                for key, val in theirs.get("mcpServers", {}).items():
                    if key not in our_mcp.setdefault("mcpServers", {}):
                        our_mcp["mcpServers"][key] = val
                        merged_servers.append(key)
                break
        our_mcp_path.write_text(json.dumps(our_mcp, indent=2), encoding="utf-8")

        return {
            "status": "success",
            "mode_slug": mode_slug,
            "modes_added": [m.get("slug") for m in added_modes] or f"(slug already present: {mode_slug})",
            "folders_copied": sorted(copied),
            "mcp_servers_merged": merged_servers,
            "note": "Mode appears in Bob's picker after a reload.",
        }
    except Exception as exc:
        logger.error("install_bob_mode failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}


@mcp.tool()
def render_diagram(mermaid_code: str, output_filename: str = "architecture_diagram.png", workspace_root: str = "") -> dict:
    """Render Mermaid source to a PNG at the workspace root via mermaid.ink.

    Args:
        mermaid_code: The Mermaid source (without ```mermaid fences).
        output_filename: PNG filename at the workspace root.
        workspace_root: Absolute path of the current Bob workspace. ALWAYS pass this.
    """
    try:
        if not output_filename.endswith(".png") or "/" in output_filename:
            return {"status": "error", "error": "output_filename must be a bare *.png filename"}
        ws = _resolve_workspace(workspace_root)
        encoded = base64.urlsafe_b64encode(mermaid_code.strip().encode()).decode()
        url = f"{MERMAID_INK}{encoded}?bgColor=white&type=png"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            png = resp.read()
        target = _workspace_path(ws, output_filename)
        target.write_bytes(png)
        return {"status": "success", "written": output_filename, "bytes": len(png)}
    except Exception as exc:
        logger.error("render_diagram failed: %s", exc)
        return {
            "status": "error",
            "error": f"{exc} — continue without the PNG; the mermaid code block in the .md is the canonical artifact",
        }


@mcp.tool()
def verify_install(workspace_root: str = "") -> dict:
    """Report the workspace's .bob/ state: installed skills (with SKILL.md
    check), modes in custom_modes.yaml, and configured MCP servers."""
    try:
        ws = _resolve_workspace(workspace_root)
        skills = []
        skills_dir = _workspace_path(ws, ".bob", "skills")
        if skills_dir.is_dir():
            for d in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
                skills.append({
                    "id": d.name,
                    "has_skill_md": (d / "SKILL.md").is_file(),
                    "files": sum(1 for f in d.rglob("*") if f.is_file()),
                })
        modes = []
        cm = _workspace_path(ws, ".bob", "custom_modes.yaml")
        if cm.is_file():
            data = yaml.safe_load(cm.read_text(encoding="utf-8")) or {}
            modes = [m.get("slug") for m in data.get("customModes", [])]
        servers = []
        mj = _workspace_path(ws, ".bob", "mcp.json")
        if mj.is_file():
            import json

            servers = list(json.loads(mj.read_text(encoding="utf-8")).get("mcpServers", {}))
        problems = []
        if skills_dir.is_dir():
            for sk in skills:
                d = skills_dir / sk["id"]
                if not sk["has_skill_md"] and not any(d.rglob("SKILL.md")):
                    problems.append(f"skill {sk['id']!r} has no SKILL.md anywhere")
        return {
            "status": "success",
            "skills": skills,
            "modes": modes,
            "mcp_servers": servers,
            "problems": problems or None,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    logger.info("building-blocks-installer serving stdio; cwd=%s", Path.cwd())
    mcp.run()


if __name__ == "__main__":
    main()
