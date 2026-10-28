#!/usr/bin/env python3
"""Start Factory Pulse locally — installs dependencies then launches backend + frontend.

Usage:
    python scripts/start.py           # install deps if needed, then start both servers
    python scripts/start.py --reinstall  # force a fresh npm install even if node_modules exists

Backend  → http://localhost:4000
Frontend → http://localhost:5173

Press Ctrl+C to stop both servers.
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
SERVER_ENTRY = ROOT / "server" / "app.py"
BACKEND_PORT = 4000
BACKEND_WAIT_SECS = 30  # max seconds to wait for Flask to be ready


def _npm() -> str:
    cmd = "npm.cmd" if os.name == "nt" else "npm"
    found = shutil.which(cmd)
    if not found:
        sys.exit(
            "[start] ERROR: npm not found. Install Node.js (https://nodejs.org) and rerun."
        )
    return found


def _find_requirements() -> Path | None:
    """Search common locations for requirements.txt."""
    for candidate in (
        ROOT / "server" / "requirements.txt",
        ROOT / "requirements.txt",
        ROOT / "deploy" / "requirements.txt",
    ):
        if candidate.exists():
            return candidate
    return None


def _install_python_deps() -> None:
    req = _find_requirements()
    if req is None:
        print("[start] No requirements.txt found — skipping pip install.", flush=True)
        return
    print(f"[start] Installing Python dependencies from {req.relative_to(ROOT)} ...", flush=True)
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(req), "--quiet"],
        check=True,
    )
    print("[start] Python dependencies installed.", flush=True)


def _install_frontend(npm: str, *, force: bool) -> None:
    node_modules = FRONTEND / "node_modules"
    if not force and node_modules.exists():
        print("[start] node_modules already present — skipping npm install.", flush=True)
        return
    print("[start] Running npm install in frontend/ ...", flush=True)
    subprocess.run([npm, "install"], cwd=FRONTEND, check=True)
    print("[start] npm install completed.", flush=True)


def _wait_for_backend(timeout: int = BACKEND_WAIT_SECS) -> bool:
    """Poll localhost:BACKEND_PORT until Flask is accepting connections."""
    deadline = time.monotonic() + timeout
    attempt = 0
    while time.monotonic() < deadline:
        attempt += 1
        try:
            with socket.create_connection(("127.0.0.1", BACKEND_PORT), timeout=1):
                print(f"[start] Backend ready on port {BACKEND_PORT}.", flush=True)
                return True
        except OSError:
            if attempt == 1:
                print(
                    f"[start] Waiting for backend on port {BACKEND_PORT} ...",
                    flush=True,
                )
            time.sleep(0.5)
    return False


def main() -> None:
    force_reinstall = "--reinstall" in sys.argv

    npm = _npm()

    # 1. Install Python deps (checks server/, root, and deploy/)
    _install_python_deps()

    # 2. Install / verify frontend Node deps
    _install_frontend(npm, force=force_reinstall)

    env = os.environ.copy()
    # Suppress the urllib3/chardet version-mismatch noise
    env.setdefault("PYTHONWARNINGS", "ignore::urllib3.exceptions.RequestsDependencyWarning")

    backend_proc = None
    frontend_proc = None

    try:
        # 3. Start backend FIRST
        print("\n[start] Starting backend  → http://localhost:4000", flush=True)
        backend_proc = subprocess.Popen(
            [sys.executable, str(SERVER_ENTRY)],
            cwd=ROOT,
            env=env,
        )

        # 4. Wait until Flask is accepting connections before launching Vite
        if not _wait_for_backend():
            rc = backend_proc.poll()
            sys.exit(
                f"[start] ERROR: Backend did not start within {BACKEND_WAIT_SECS}s "
                f"(exit code: {rc}). Check the output above for Python errors."
            )

        # 5. Start frontend only after backend is confirmed ready
        print("[start] Starting frontend → http://localhost:5173", flush=True)
        print("[start] Press Ctrl+C to stop.\n", flush=True)
        frontend_proc = subprocess.Popen(
            [npm, "run", "dev"],
            cwd=FRONTEND,
            env=env,
        )

        backend_proc.wait()

    except KeyboardInterrupt:
        print("\n[start] Shutting down...", flush=True)
    finally:
        for proc in (frontend_proc, backend_proc):
            if proc and proc.poll() is None:
                proc.terminate()
        print("[start] Both servers stopped.", flush=True)


if __name__ == "__main__":
    main()
