from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import queue
import shutil
import shlex
import signal
import subprocess
from threading import Lock, Thread
from uuid import uuid4
import zipfile

from pydantic import BaseModel, Field

from bobserver.bob_runtime import BobStreamState, build_bob_args, parse_bob_output
from bobserver.config import Settings


class BobPromptRequest(BaseModel):
    prompt: str
    timeout_seconds: int = Field(default=120, alias="timeoutSeconds")
    yolo: bool = False
    safety_profile: str = Field(default="readonly", alias="safetyProfile", pattern="^(readonly|edit|trusted)$")
    max_coins: int = Field(default=30, alias="maxCoins", ge=1, le=100)
    workspace_mode: str = Field(default="isolated", alias="workspaceMode", pattern="^(isolated|shared)$")


class BobPromptResult(BaseModel):
    id: str
    state: str
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")
    exit_code: int | None = Field(default=None, alias="exitCode")
    log: str = ""
    error: str = ""
    metadata: dict = Field(default_factory=dict)


_bob_jobs: dict[str, "BobAsyncJob"] = {}
_bob_jobs_lock = Lock()


@dataclass
class BobAsyncJob:
    id: str
    state: str
    created_at: str
    updated_at: str
    exit_code: int | None = None
    log: str = ""
    error: str = ""
    metadata: dict = field(default_factory=dict)
    workspace_mode: str = "isolated"
    run_dir: Path | None = None
    owner: dict = field(default_factory=dict)
    parent_id: str = ""
    role: str = "standalone"
    activity: list[dict] = field(default_factory=list)
    process: subprocess.Popen | None = field(default=None, repr=False)


def run_bob_prompt(request: BobPromptRequest, settings: Settings) -> BobPromptResult:
    now = datetime.now(UTC).isoformat()
    prompt_id = f"bob-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"
    run_dir, workspace_dir = _prepare_bob_workspace(prompt_id, request, settings)

    env = os.environ.copy()
    if not env.get("BOBSHELL_API_KEY"):
        return BobPromptResult(
            id=prompt_id,
            state="failed",
            createdAt=now,
            updatedAt=datetime.now(UTC).isoformat(),
            exitCode=2,
            error="BOBSHELL_API_KEY is not set. Restart the container with -e BOBSHELL_API_KEY=<your key>.",
        )

    env.update(
        {
            "HOME": str(run_dir / "home" if request.workspace_mode == "isolated" else Path(settings.workspace_root) / "home"),
            "BOBSERVER_PROMPT_ID": prompt_id,
            "BOBSERVER_RUN_DIR": str(run_dir),
        }
    )
    command = _bob_command(request, settings)

    timeout = max(1, min(request.timeout_seconds, settings.executor_timeout_seconds))
    try:
        process = subprocess.Popen(
            command,
            cwd=workspace_dir,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        timed_out = False
        try:
            stdout, stderr = process.communicate(input=request.prompt + "\n", timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            _terminate_process(process)
            stdout, stderr = process.communicate()
        exit_code = 124 if timed_out else process.returncode
        bob_state = parse_bob_output(stdout)
        _write_bob_artifacts(run_dir, bob_state, exit_code, request)
        state = "completed" if exit_code == 0 and bob_state.status in {None, "success"} else "failed"
        log = bob_state.final_text
        if stderr.strip() and state == "failed":
            log = _process_output(log, stderr)
        return BobPromptResult(
            id=prompt_id,
            state=state,
            createdAt=now,
            updatedAt=datetime.now(UTC).isoformat(),
            exitCode=exit_code,
            log=log,
            error=(f"Timed out after {timeout} seconds." if timed_out else ("" if exit_code == 0 else f"Bob exited with code {exit_code}.")),
            metadata=bob_state.metadata(),
        )
    except FileNotFoundError as exc:
        return BobPromptResult(
            id=prompt_id,
            state="failed",
            createdAt=now,
            updatedAt=datetime.now(UTC).isoformat(),
            exitCode=127,
            error=str(exc),
        )


def stream_bob_prompt(request: BobPromptRequest, settings: Settings):
    now = datetime.now(UTC).isoformat()
    prompt_id = f"bob-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"
    run_dir, workspace_dir = _prepare_bob_workspace(prompt_id, request, settings)

    env = os.environ.copy()
    if not env.get("BOBSHELL_API_KEY"):
        yield _sse(
            "done",
            {
                "id": prompt_id,
                "state": "failed",
                "createdAt": now,
                "updatedAt": datetime.now(UTC).isoformat(),
                "exitCode": 2,
                "error": "BOBSHELL_API_KEY is not set. Restart the container with -e BOBSHELL_API_KEY=<your key>.",
            },
        )
        return

    env.update(
        {
            "HOME": str(run_dir / "home" if request.workspace_mode == "isolated" else Path(settings.workspace_root) / "home"),
            "BOBSERVER_PROMPT_ID": prompt_id,
            "BOBSERVER_RUN_DIR": str(run_dir),
        }
    )
    command = _bob_command(request, settings)

    timeout = max(1, min(request.timeout_seconds, settings.executor_timeout_seconds))
    yield _sse(
        "status",
        {
            "id": prompt_id,
            "state": "running",
            "createdAt": now,
            "command": " ".join(command),
            "safetyProfile": "trusted" if request.yolo else request.safety_profile,
            "maxCoins": min(request.max_coins, settings.bob_max_coins),
        },
    )

    try:
        process = subprocess.Popen(
            command,
            cwd=workspace_dir,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            start_new_session=True,
        )
    except FileNotFoundError as exc:
        yield _sse(
            "done",
            {
                "id": prompt_id,
                "state": "failed",
                "createdAt": now,
                "updatedAt": datetime.now(UTC).isoformat(),
                "exitCode": 127,
                "error": str(exc),
            },
        )
        return

    output_queue: queue.Queue[tuple[str, str | None]] = queue.Queue()
    for stream_name, pipe in (("stdout", process.stdout), ("stderr", process.stderr)):
        if pipe is not None:
            Thread(target=_read_stream, args=(stream_name, pipe, output_queue), daemon=True).start()
    Thread(target=_write_stdin, args=(process.stdin, request.prompt), daemon=True).start()

    deadline = datetime.now(UTC).timestamp() + timeout
    timed_out = False
    bob_state = BobStreamState()
    stderr_parts: list[str] = []
    while True:
        if process.poll() is not None and output_queue.empty():
            break
        if datetime.now(UTC).timestamp() > deadline:
            timed_out = True
            _terminate_process(process)
            break
        try:
            stream_name, chunk = output_queue.get(timeout=0.25)
        except queue.Empty:
            yield _sse("heartbeat", {"id": prompt_id})
            continue
        if chunk and stream_name == "stdout":
            for event, payload in bob_state.consume(chunk):
                yield _sse(event, {"id": prompt_id, **payload})
        elif chunk:
            stderr_parts.append(chunk)
            yield _sse("diagnostic", {"id": prompt_id, "stream": stream_name, "text": chunk})

    while not output_queue.empty():
        stream_name, chunk = output_queue.get_nowait()
        if chunk and stream_name == "stdout":
            for event, payload in bob_state.consume(chunk):
                yield _sse(event, {"id": prompt_id, **payload})
        elif chunk:
            stderr_parts.append(chunk)
            yield _sse("diagnostic", {"id": prompt_id, "stream": stream_name, "text": chunk})

    exit_code = 124 if timed_out else process.wait()
    _write_bob_artifacts(run_dir, bob_state, exit_code, request)
    state = "completed" if exit_code == 0 and bob_state.status in {None, "success"} else "failed"
    error = f"Timed out after {timeout} seconds." if timed_out else ("" if state == "completed" else f"Bob exited with code {exit_code}.")
    if bob_state.final_text:
        yield _sse("output", {"id": prompt_id, "stream": "stdout", "text": bob_state.final_text + "\n"})
    yield _sse(
        "done",
        {
            "id": prompt_id,
            "state": state,
            "createdAt": now,
            "updatedAt": datetime.now(UTC).isoformat(),
            "exitCode": exit_code,
            "error": error,
            "metadata": bob_state.metadata(),
        },
    )


def start_bob_prompt(
    request: BobPromptRequest,
    settings: Settings,
    *,
    owner: dict | None = None,
    parent_id: str = "",
    role: str = "standalone",
    seed_files: dict[str, str] | None = None,
) -> dict:
    now = datetime.now(UTC).isoformat()
    prompt_id = f"bob-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"
    job = BobAsyncJob(
        id=prompt_id,
        state="starting",
        created_at=now,
        updated_at=now,
        workspace_mode=request.workspace_mode,
        owner=dict(owner or {}),
        parent_id=parent_id,
        role=role,
    )
    with _bob_jobs_lock:
        _bob_jobs[prompt_id] = job
    Thread(target=_run_bob_async_job, args=(job, request, settings, seed_files or {}), daemon=True).start()
    return _bob_job_payload(job)


def get_bob_prompt_status(job_id: str, offset: int = 0) -> dict:
    with _bob_jobs_lock:
        job = _bob_jobs.get(job_id)
        if job is None:
            raise KeyError(job_id)
        return _bob_job_payload(job, offset=offset)


def list_bob_prompt_jobs() -> list[dict]:
    with _bob_jobs_lock:
        return [
            _bob_job_payload(job)
            for job in sorted(_bob_jobs.values(), key=lambda item: item.created_at, reverse=True)
        ]


def delete_bob_prompt_job(job_id: str, settings: Settings) -> None:
    with _bob_jobs_lock:
        job = _bob_jobs.get(job_id)
        if job is None:
            raise KeyError(job_id)
        if job.state in {"starting", "running"}:
            raise RuntimeError("Running Bob jobs must be cancelled before deletion.")
        del _bob_jobs[job_id]
    run_dir = _bob_run_dir(job_id, settings)
    if run_dir.exists():
        shutil.rmtree(run_dir)


def bob_job_artifact(job_id: str, artifact_name: str, settings: Settings) -> Path:
    allowed = {"result.md", "bob-run.json", "prompt.md", "workspace.zip"}
    if artifact_name not in allowed:
        raise ValueError("Artifact is not available for download.")
    with _bob_jobs_lock:
        if job_id not in _bob_jobs:
            raise KeyError(job_id)
    run_dir = _bob_run_dir(job_id, settings)
    artifact = run_dir / artifact_name
    if artifact_name == "workspace.zip":
        work_dir = run_dir / "work"
        if not work_dir.is_dir():
            raise FileNotFoundError(artifact_name)
        with zipfile.ZipFile(artifact, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for candidate in sorted(work_dir.rglob("*")):
                if candidate.is_file() and not candidate.is_symlink():
                    archive.write(candidate, candidate.relative_to(work_dir))
    if not artifact.is_file():
        raise FileNotFoundError(artifact_name)
    return artifact


def bob_job_workspace(job_id: str) -> Path:
    with _bob_jobs_lock:
        job = _bob_jobs.get(job_id)
        if job is None or job.run_dir is None:
            raise KeyError(job_id)
        workspace = job.run_dir / "work"
    if not workspace.is_dir():
        raise FileNotFoundError(job_id)
    return workspace


def cancel_bob_prompt(job_id: str) -> dict:
    with _bob_jobs_lock:
        job = _bob_jobs.get(job_id)
        if job is None:
            raise KeyError(job_id)
        process = job.process
        if job.state == "running" and process is not None and process.poll() is None:
            _terminate_process(process)
            job.state = "cancelled"
            job.exit_code = 130
            job.error = "Cancelled by request."
            job.updated_at = datetime.now(UTC).isoformat()
            if job.run_dir is not None:
                payload = {
                    "exitCode": 130,
                    "status": "cancelled",
                    "workspaceMode": job.workspace_mode,
                    "owner": job.owner,
                    "parentId": job.parent_id,
                    "role": job.role,
                    "error": job.error,
                    **job.metadata,
                }
                (job.run_dir / "bob-run.json").write_text(
                    json.dumps(payload, indent=2) + "\n",
                    encoding="utf-8",
                )
        return _bob_job_payload(job)


def _run_bob_async_job(
    job: BobAsyncJob,
    request: BobPromptRequest,
    settings: Settings,
    seed_files: dict[str, str] | None = None,
) -> None:
    run_dir, workspace_dir = _prepare_bob_workspace(job.id, request, settings, seed_files=seed_files)
    job.run_dir = run_dir

    env = os.environ.copy()
    if not env.get("BOBSHELL_API_KEY"):
        with _bob_jobs_lock:
            job.state = "failed"
            job.exit_code = 2
            job.error = "BOBSHELL_API_KEY is not set. Restart the container with -e BOBSHELL_API_KEY=<your key>."
            job.updated_at = datetime.now(UTC).isoformat()
        return

    env.update(
        {
            "HOME": str(run_dir / "home" if request.workspace_mode == "isolated" else Path(settings.workspace_root) / "home"),
            "BOBSERVER_PROMPT_ID": job.id,
            "BOBSERVER_RUN_DIR": str(run_dir),
        }
    )
    command = _bob_command(request, settings)

    timeout = max(1, min(request.timeout_seconds, settings.executor_timeout_seconds))
    try:
        process = subprocess.Popen(
            command,
            cwd=workspace_dir,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            start_new_session=True,
        )
    except FileNotFoundError as exc:
        with _bob_jobs_lock:
            job.state = "failed"
            job.exit_code = 127
            job.error = str(exc)
            job.updated_at = datetime.now(UTC).isoformat()
        return

    with _bob_jobs_lock:
        job.process = process
        job.state = "running"
        job.updated_at = datetime.now(UTC).isoformat()

    output_queue: queue.Queue[tuple[str, str | None]] = queue.Queue()
    for stream_name, pipe in (("stdout", process.stdout), ("stderr", process.stderr)):
        if pipe is not None:
            Thread(target=_read_stream, args=(stream_name, pipe, output_queue), daemon=True).start()
    Thread(target=_write_stdin, args=(process.stdin, request.prompt), daemon=True).start()

    deadline = datetime.now(UTC).timestamp() + timeout
    timed_out = False
    bob_state = BobStreamState()
    stderr_parts: list[str] = []
    while True:
        if process.poll() is not None and output_queue.empty():
            break
        with _bob_jobs_lock:
            if job.state == "cancelled":
                return
        if datetime.now(UTC).timestamp() > deadline:
            timed_out = True
            _terminate_process(process)
            break
        try:
            _stream_name, chunk = output_queue.get(timeout=0.25)
        except queue.Empty:
            continue
        if chunk and _stream_name == "stdout":
            events = bob_state.consume(chunk)
            with _bob_jobs_lock:
                job.metadata = bob_state.metadata()
                job.updated_at = datetime.now(UTC).isoformat()
                for event, payload in events:
                    if event == "progress":
                        job.activity.append({"at": job.updated_at, **payload})
                        job.activity = job.activity[-20:]
        elif chunk:
            stderr_parts.append(chunk)
            with _bob_jobs_lock:
                job.updated_at = datetime.now(UTC).isoformat()

    while not output_queue.empty():
        _stream_name, chunk = output_queue.get_nowait()
        if chunk and _stream_name == "stdout":
            bob_state.consume(chunk)
        elif chunk:
            stderr_parts.append(chunk)

    with _bob_jobs_lock:
        if job.state == "cancelled":
            return
    exit_code = 124 if timed_out else process.wait()
    _write_bob_artifacts(run_dir, bob_state, exit_code, request, job=job)
    with _bob_jobs_lock:
        if job.state != "cancelled":
            job.exit_code = exit_code
            job.state = "completed" if exit_code == 0 and bob_state.status in {None, "success"} else "failed"
            job.log = bob_state.final_text
            if stderr_parts and job.state == "failed":
                job.log = _process_output(job.log, "".join(stderr_parts))
            job.error = f"Timed out after {timeout} seconds." if timed_out else ("" if job.state == "completed" else f"Bob exited with code {exit_code}.")
            job.metadata = bob_state.metadata()
            job.updated_at = datetime.now(UTC).isoformat()


def _bob_job_payload(job: BobAsyncJob, offset: int = 0) -> dict:
    safe_offset = max(0, min(offset, len(job.log)))
    return {
        "id": job.id,
        "state": job.state,
        "createdAt": job.created_at,
        "updatedAt": job.updated_at,
        "exitCode": job.exit_code,
        "output": job.log[safe_offset:],
        "offset": safe_offset,
        "nextOffset": len(job.log),
        "error": job.error,
        "metadata": job.metadata,
        "workspaceMode": job.workspace_mode,
        "owner": job.owner,
        "parentId": job.parent_id,
        "role": job.role,
        "activity": [dict(item) for item in job.activity],
        "artifacts": [
            name
            for name in ("result.md", "bob-run.json", "prompt.md", "workspace.zip")
            if job.run_dir is not None
            and (
                (name == "workspace.zip" and (job.run_dir / "work").is_dir())
                or (job.run_dir / name).is_file()
            )
        ],
    }


def _process_output(stdout: str | bytes | None, stderr: str | bytes | None) -> str:
    return _to_text(stdout) + _to_text(stderr)


def _to_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _bob_command(request: BobPromptRequest, settings: Settings) -> list[str]:
    max_coins = min(request.max_coins, settings.bob_max_coins)
    return shlex.split(settings.bob_command) + build_bob_args(
        max_coins=max_coins,
        safety_profile=request.safety_profile,
        yolo=request.yolo,
    )


def _bob_run_dir(job_id: str, settings: Settings) -> Path:
    runs_root = (Path(settings.workspace_root) / "runs").resolve()
    run_dir = (runs_root / job_id).resolve()
    if run_dir.parent != runs_root:
        raise ValueError("Invalid Bob job ID.")
    return run_dir


def _seed_mcp_config(work_dir: Path, settings: Settings) -> None:
    """
    Copy .bob/mcp.json into <work_dir>/.bob/mcp.json so Bob CLI picks up
    MCP servers automatically for every run.

    The source path is settings.bob_mcp_config (default: .bob/mcp.json),
    resolved relative to the current working directory (i.e. the bobserver
    package root).  If the file doesn't exist the step is silently skipped —
    runs without MCP still work, they just lack the extra tools.
    """
    src = Path(settings.bob_mcp_config)
    if not src.is_absolute():
        # Resolve relative to the bobserver repo root (two levels up from this file)
        src = (Path(__file__).parent.parent.parent / settings.bob_mcp_config).resolve()

    if not src.is_file():
        return  # no mcp config — skip silently

    dest_dir = work_dir / ".bob"
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest_dir / "mcp.json")


def _prepare_bob_workspace(
    job_id: str,
    request: BobPromptRequest,
    settings: Settings,
    seed_files: dict[str, str] | None = None,
) -> tuple[Path, Path]:
    workspace_root = Path(settings.workspace_root).resolve()
    workspace_root.mkdir(parents=True, exist_ok=True)
    run_dir = _bob_run_dir(job_id, settings)
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "prompt.md").write_text(request.prompt + "\n", encoding="utf-8")
    if request.workspace_mode == "shared":
        return run_dir, workspace_root

    work_dir = run_dir / "work"
    work_dir.mkdir()
    (run_dir / "home").mkdir()

    # ── Seed .bob/mcp.json so Bob picks up MCP servers automatically ──
    _seed_mcp_config(work_dir, settings)

    for name in ("bob_context.md", "orders.csv", "orders_raw.csv"):
        source = workspace_root / name
        if source.is_file() and not source.is_symlink():
            shutil.copy2(source, work_dir / name)
    source_db = workspace_root / "demo.db"
    if source_db.is_file() and not source_db.is_symlink():
        with _connect_sqlite_readonly(source_db) as source, sqlite3.connect(work_dir / "demo.db") as target:
            source.backup(target)
    for name in ("context", "cert-demo"):
        source = workspace_root / name
        if source.is_dir() and not source.is_symlink():
            shutil.copytree(source, work_dir / name, symlinks=False, ignore=_ignore_symlinks)
    for name, content in (seed_files or {}).items():
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts or not relative.parts:
            raise ValueError(f"Invalid seeded workspace path: {name}")
        destination = work_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
    return run_dir, work_dir


def _ignore_symlinks(directory: str, names: list[str]) -> set[str]:
    return {name for name in names if (Path(directory) / name).is_symlink()}


def _terminate_process(process: subprocess.Popen, grace_seconds: int = 2) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=grace_seconds)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=5)


def _write_bob_artifacts(
    run_dir: Path,
    state: BobStreamState,
    exit_code: int,
    request: BobPromptRequest,
    job: BobAsyncJob | None = None,
) -> None:
    payload = {
        "exitCode": exit_code,
        "workspaceMode": request.workspace_mode,
        "safetyProfile": "trusted" if request.yolo else request.safety_profile,
        "maxCoins": request.max_coins,
        **(
            {"owner": job.owner, "parentId": job.parent_id, "role": job.role}
            if job is not None
            else {}
        ),
        **state.metadata(),
    }
    (run_dir / "bob-run.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if state.final_text:
        (run_dir / "result.md").write_text(state.final_text.rstrip() + "\n", encoding="utf-8")


def _read_stream(stream_name: str, pipe, output_queue: queue.Queue[tuple[str, str | None]]) -> None:
    try:
        for line in iter(pipe.readline, ""):
            output_queue.put((stream_name, line))
    finally:
        pipe.close()


def _write_stdin(pipe, prompt: str) -> None:
    if pipe is None:
        return
    try:
        pipe.write(prompt + "\n")
        pipe.close()
    except (BrokenPipeError, OSError):
        pass


def _stream_process(command_id: str, process: subprocess.Popen, timeout: int, created_at: str):
    output_queue: queue.Queue[tuple[str, str | None]] = queue.Queue()
    for stream_name, pipe in (("stdout", process.stdout), ("stderr", process.stderr)):
        if pipe is not None:
            Thread(target=_read_stream, args=(stream_name, pipe, output_queue), daemon=True).start()

    deadline = datetime.now(UTC).timestamp() + timeout
    timed_out = False
    while True:
        if process.poll() is not None and output_queue.empty():
            break
        if datetime.now(UTC).timestamp() > deadline:
            timed_out = True
            process.kill()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            break
        try:
            stream_name, chunk = output_queue.get(timeout=0.25)
        except queue.Empty:
            yield _sse("heartbeat", {"id": command_id})
            continue
        if chunk:
            yield _sse("output", {"id": command_id, "stream": stream_name, "text": chunk})

    while not output_queue.empty():
        stream_name, chunk = output_queue.get_nowait()
        if chunk:
            yield _sse("output", {"id": command_id, "stream": stream_name, "text": chunk})

    exit_code = 124 if timed_out else process.wait()
    state = "completed" if exit_code == 0 else "failed"
    error = f"Timed out after {timeout} seconds." if timed_out else ("" if exit_code == 0 else f"Command exited with code {exit_code}.")
    yield _sse(
        "done",
        {
            "id": command_id,
            "state": state,
            "createdAt": created_at,
            "updatedAt": datetime.now(UTC).isoformat(),
            "exitCode": exit_code,
            "error": error,
        },
    )


def _sse(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload)}\n\n"


def list_pipeline_tasks() -> list[PipelineTask]:
    with _lock:
        return list(_tasks)


def get_pipeline_task(task_id: str) -> PipelineTask | None:
    with _lock:
        return next((task for task in _tasks if task.id == task_id), None)
