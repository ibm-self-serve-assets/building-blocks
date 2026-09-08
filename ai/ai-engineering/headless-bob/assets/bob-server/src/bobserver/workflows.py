from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
import json
from pathlib import Path
import shutil
from threading import Lock, Thread
import time
from uuid import uuid4
import zipfile

from pydantic import BaseModel, Field

from bobserver.config import Settings
from bobserver.skills import list_skills
from bobserver.tasks import (
    BobPromptRequest,
    bob_job_artifact,
    bob_job_workspace,
    cancel_bob_prompt,
    get_bob_prompt_status,
    start_bob_prompt,
)


class WorkflowRequest(BaseModel):
    objective: str = Field(min_length=3, max_length=12000)
    execution_safety_profile: str = Field(
        default="edit", alias="executionSafetyProfile", pattern="^(readonly|edit|trusted)$"
    )
    max_coins_per_run: int = Field(default=10, alias="maxCoinsPerRun", ge=1, le=30)
    timeout_seconds: int = Field(default=300, alias="timeoutSeconds", ge=10, le=900)
    auto_approve: bool = Field(default=False, alias="autoApprove")


class WorkflowApproval(BaseModel):
    project_context: str | None = Field(default=None, alias="projectContext", max_length=100000)
    tasks: list[dict] | None = None


@dataclass
class Workflow:
    id: str
    objective: str
    owner: dict
    state: str
    created_at: str
    updated_at: str
    execution_safety_profile: str
    max_coins_per_run: int
    timeout_seconds: int
    auto_approve: bool = False
    planning_job_id: str = ""
    active_job_id: str = ""
    project_context: str = ""
    tasks: list[dict] = field(default_factory=list)
    error: str = ""
    cancelled: bool = False
    run_dir: Path | None = None


_workflows: dict[str, Workflow] = {}
_workflow_lock = Lock()


def create_workflow(request: WorkflowRequest, owner: dict, settings: Settings) -> dict:
    now = _now()
    workflow_id = f"workflow-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"
    run_dir = _workflow_dir(workflow_id, settings)
    run_dir.mkdir(parents=True, exist_ok=False)
    workflow = Workflow(
        id=workflow_id,
        objective=request.objective,
        owner=dict(owner),
        state="planning",
        created_at=now,
        updated_at=now,
        execution_safety_profile=request.execution_safety_profile,
        max_coins_per_run=request.max_coins_per_run,
        timeout_seconds=request.timeout_seconds,
        auto_approve=request.auto_approve,
        run_dir=run_dir,
    )
    (run_dir / "objective.md").write_text(request.objective.rstrip() + "\n", encoding="utf-8")
    with _workflow_lock:
        _workflows[workflow_id] = workflow
    planning = start_bob_prompt(
        BobPromptRequest(
            prompt=_planning_prompt(request.objective, settings),
            timeoutSeconds=request.timeout_seconds,
            safetyProfile="readonly",
            maxCoins=request.max_coins_per_run,
            workspaceMode="isolated",
        ),
        settings,
        owner=owner,
        parent_id=workflow_id,
        role="planner",
    )
    with _workflow_lock:
        workflow.planning_job_id = planning["id"]
        _write_summary(workflow)
    Thread(target=_observe_planning, args=(workflow_id, settings), daemon=True).start()
    return _payload(workflow)


def list_workflows() -> list[dict]:
    with _workflow_lock:
        return [_payload(item) for item in sorted(_workflows.values(), key=lambda value: value.created_at, reverse=True)]


def get_workflow(workflow_id: str) -> dict:
    with _workflow_lock:
        workflow = _required(workflow_id)
        return _payload(workflow)


def approve_workflow(workflow_id: str, approval: WorkflowApproval, settings: Settings) -> dict:
    with _workflow_lock:
        workflow = _required(workflow_id)
        if workflow.state != "awaiting_approval":
            raise RuntimeError("Workflow is not awaiting approval.")
        if approval.project_context is not None:
            workflow.project_context = approval.project_context.strip()
        if approval.tasks is not None:
            workflow.tasks = _validate_tasks(approval.tasks)
        if not workflow.project_context or not workflow.tasks:
            raise ValueError("An approved workflow requires project context and at least one task.")
        workflow.state = "executing"
        workflow.updated_at = _now()
        _write_plan_artifacts(workflow)
        _write_summary(workflow)
    Thread(target=_execute_workflow, args=(workflow_id, settings), daemon=True).start()
    return get_workflow(workflow_id)


def cancel_workflow(workflow_id: str) -> dict:
    with _workflow_lock:
        workflow = _required(workflow_id)
        workflow.cancelled = True
        active_job_id = workflow.active_job_id or workflow.planning_job_id
        if workflow.state not in {"completed", "failed", "cancelled"}:
            workflow.state = "cancelled"
            workflow.error = "Cancelled by request."
            workflow.updated_at = _now()
            _write_summary(workflow)
    if active_job_id:
        try:
            cancel_bob_prompt(active_job_id)
        except KeyError:
            pass
    return get_workflow(workflow_id)


def delete_workflow(workflow_id: str, settings: Settings) -> None:
    with _workflow_lock:
        workflow = _required(workflow_id)
        if workflow.state in {"planning", "executing"}:
            raise RuntimeError("Active workflows must be cancelled before deletion.")
        del _workflows[workflow_id]
    run_dir = _workflow_dir(workflow_id, settings)
    if run_dir.exists():
        shutil.rmtree(run_dir)


def workflow_artifact(workflow_id: str, artifact_name: str, settings: Settings) -> Path:
    allowed = {"project-context.md", "tasks.json", "workflow.json", "workflow.zip", "objective.md"}
    if artifact_name not in allowed:
        raise ValueError("Workflow artifact is not available.")
    with _workflow_lock:
        workflow = _required(workflow_id)
        run_dir = workflow.run_dir or _workflow_dir(workflow_id, settings)
        task_snapshot = [dict(task) for task in workflow.tasks]
    artifact = run_dir / artifact_name
    if artifact_name == "workflow.zip":
        with zipfile.ZipFile(artifact, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name in ("objective.md", "project-context.md", "tasks.json", "workflow.json"):
                candidate = run_dir / name
                if candidate.is_file():
                    archive.write(candidate, name)
            for task in task_snapshot:
                job_id = task.get("jobId")
                if not job_id:
                    continue
                for name in ("result.md", "bob-run.json", "prompt.md"):
                    try:
                        candidate = bob_job_artifact(job_id, name, settings)
                    except (KeyError, FileNotFoundError, ValueError):
                        continue
                    archive.write(candidate, f"children/{task['id']}/{name}")
    if not artifact.is_file():
        raise FileNotFoundError(artifact_name)
    return artifact


def _observe_planning(workflow_id: str, settings: Settings) -> None:
    while True:
        should_auto_approve = False
        with _workflow_lock:
            workflow = _workflows.get(workflow_id)
            if workflow is None or workflow.cancelled:
                return
            job_id = workflow.planning_job_id
        if not job_id:
            time.sleep(0.05)
            continue
        try:
            job = get_bob_prompt_status(job_id)
        except KeyError:
            return
        if job["state"] not in {"completed", "failed", "cancelled"}:
            time.sleep(0.1)
            continue
        with _workflow_lock:
            workflow = _workflows.get(workflow_id)
            if workflow is None or workflow.cancelled:
                return
            if job["state"] != "completed":
                workflow.state = "failed"
                workflow.error = job.get("error") or "Planning job failed."
            else:
                _load_planning_result(workflow, job)
                should_auto_approve = workflow.state == "awaiting_approval" and workflow.auto_approve
            workflow.updated_at = _now()
            _write_summary(workflow)
        if should_auto_approve:
            approve_workflow(workflow_id, WorkflowApproval(), settings)
        return


def _load_planning_result(workflow: Workflow, job: dict) -> None:
    try:
        work_dir = bob_job_workspace(workflow.planning_job_id)
        context_path = work_dir / "project-context.md"
        tasks_path = work_dir / "tasks.json"
        context = context_path.read_text(encoding="utf-8") if context_path.is_file() else ""
        tasks = json.loads(tasks_path.read_text(encoding="utf-8")) if tasks_path.is_file() else []
        if isinstance(tasks, dict):
            tasks = tasks.get("tasks", [])
        if not context or not tasks:
            plan = _parse_planning_json(job.get("output", ""))
            context = str(plan.get("projectContext") or "").strip()
            tasks = plan.get("tasks")
        workflow.project_context = context.strip()
        workflow.tasks = _validate_tasks(tasks)
        if not workflow.project_context:
            raise ValueError("Planner did not return projectContext.")
        workflow.state = "awaiting_approval"
        _write_plan_artifacts(workflow)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        workflow.state = "failed"
        workflow.error = f"Unable to load planning artifacts: {exc}"


def _execute_workflow(workflow_id: str, settings: Settings) -> None:
    index = 0
    while True:
        with _workflow_lock:
            workflow = _workflows.get(workflow_id)
            if workflow is None or workflow.cancelled:
                return
            if index >= len(workflow.tasks):
                workflow.state = "completed"
                workflow.active_job_id = ""
                workflow.updated_at = _now()
                _write_summary(workflow)
                return
            task = workflow.tasks[index]
            task["state"] = "starting"
            workflow.updated_at = _now()
            context = workflow.project_context
            tasks_json = json.dumps({"tasks": workflow.tasks}, indent=2)
            owner = dict(workflow.owner)
            safety = workflow.execution_safety_profile
            max_coins = workflow.max_coins_per_run
            timeout = workflow.timeout_seconds
            _write_summary(workflow)
        child = start_bob_prompt(
            BobPromptRequest(
                prompt=_task_prompt(task),
                timeoutSeconds=timeout,
                safetyProfile=safety,
                maxCoins=max_coins,
                workspaceMode="isolated",
            ),
            settings,
            owner=owner,
            parent_id=workflow_id,
            role="worker",
            seed_files={"project-context.md": context + "\n", "tasks.json": tasks_json + "\n"},
        )
        with _workflow_lock:
            workflow = _workflows.get(workflow_id)
            if workflow is None or workflow.cancelled:
                try:
                    cancel_bob_prompt(child["id"])
                except KeyError:
                    pass
                return
            workflow.active_job_id = child["id"]
            task["jobId"] = child["id"]
            task["state"] = "running"
            _write_summary(workflow)
        while True:
            with _workflow_lock:
                workflow = _workflows.get(workflow_id)
                if workflow is None or workflow.cancelled:
                    return
            status = get_bob_prompt_status(child["id"])
            if status["state"] in {"completed", "failed", "cancelled"}:
                break
            time.sleep(0.1)
        with _workflow_lock:
            workflow = _workflows.get(workflow_id)
            if workflow is None or workflow.cancelled:
                return
            task = workflow.tasks[index]
            task["state"] = status["state"]
            task["exitCode"] = status.get("exitCode")
            workflow.active_job_id = ""
            workflow.updated_at = _now()
            if status["state"] != "completed":
                workflow.state = "failed"
                workflow.error = f"Task {task['id']} {status['state']}: {status.get('error') or 'Bob run failed.'}"
                _write_summary(workflow)
                return
            _write_summary(workflow)
        index += 1


def _planning_prompt(objective: str, settings: Settings) -> str:
    skills = [
        {"id": skill["id"], "name": skill["name"], "description": skill["description"], "inputs": skill["inputs"]}
        for skill in list_skills()
    ]
    inventory = _shallow_inventory(settings)
    return f"""You are the planning stage of a Bobserver Plan → Approve → Execute workflow.

Objective:
{objective}

Available skills (compact metadata only):
{json.dumps(skills, indent=2)}

Shallow workspace inventory (names and sizes only):
{json.dumps(inventory, indent=2)}

Plan only. Do not inspect file contents, perform analysis, use tools, or implement the objective.
Return only one valid JSON object with this exact shape, without Markdown fences or commentary:
{{
  "projectContext": "A concise reviewable summary of the objective, available inputs, assumptions, constraints, approach, validation, and risks.",
  "tasks": [
    {{
      "title": "Short task title",
      "prompt": "Self-contained worker instruction. Detailed inspection and analysis happens here, after approval.",
      "skills": ["installed-skill-id"],
      "skillReason": "Why these skills are relevant, or why no skill is needed"
    }}
  ]
}}

Create 1 to 6 focused sequential tasks. Select only installed skill IDs. Use an empty skills array when none apply. Never include secrets."""


def _task_prompt(task: dict) -> str:
    skill_map = {skill["id"]: skill for skill in list_skills()}
    skill_instructions = "\n\n".join(
        f"Approved skill: {skill_map[skill_id]['name']}\n{skill_map[skill_id]['prompt']}"
        for skill_id in task.get("skills", [])
    )
    return f"""You are a worker in an approved Bobserver workflow.
Read project-context.md and tasks.json first. Follow the approved context and stay within this task.

Task {task['id']}: {task['title']}
{task['prompt']}

{skill_instructions or 'No specialized skill was selected for this task.'}

Validate your work. Return a concise final result with evidence, changed files, and any unresolved issues."""


def _validate_tasks(tasks: list[dict]) -> list[dict]:
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= 6:
        raise ValueError("Tasks must contain between 1 and 6 items.")
    installed = {skill["id"] for skill in list_skills()}
    validated = []
    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            raise ValueError("Each task must be an object.")
        title = str(task.get("title") or "").strip()
        prompt = str(task.get("prompt") or "").strip()
        if not title or not prompt:
            raise ValueError("Each task requires a title and prompt.")
        skills = task.get("skills") or []
        if not isinstance(skills, list) or any(str(skill) not in installed for skill in skills):
            raise ValueError("Each selected skill must be installed.")
        validated.append({
            "id": f"task-{index:02d}",
            "title": title,
            "prompt": prompt,
            "skills": [str(skill) for skill in skills],
            "skillReason": str(task.get("skillReason") or "No specialized skill selected."),
            "state": "pending",
        })
    return validated


def _parse_planning_json(output: str) -> dict:
    text = str(output or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("Planner output must be a JSON object.")
    return value


def _shallow_inventory(settings: Settings) -> list[dict]:
    root = Path(settings.workspace_root)
    if not root.is_dir():
        return []
    inventory = []
    for item in sorted(root.iterdir(), key=lambda value: value.name)[:100]:
        if item.name in {"home", "runs", "workflows"} or item.is_symlink():
            continue
        inventory.append({"name": item.name, "type": "directory" if item.is_dir() else "file", "bytes": item.stat().st_size if item.is_file() else None})
    return inventory


def _write_plan_artifacts(workflow: Workflow) -> None:
    if workflow.run_dir is None:
        return
    (workflow.run_dir / "project-context.md").write_text(workflow.project_context.rstrip() + "\n", encoding="utf-8")
    (workflow.run_dir / "tasks.json").write_text(
        json.dumps({"tasks": workflow.tasks}, indent=2) + "\n", encoding="utf-8"
    )


def _write_summary(workflow: Workflow) -> None:
    if workflow.run_dir is not None:
        (workflow.run_dir / "workflow.json").write_text(json.dumps(_payload(workflow), indent=2) + "\n", encoding="utf-8")


def _payload(workflow: Workflow) -> dict:
    planning = {}
    if workflow.planning_job_id:
        try:
            job = get_bob_prompt_status(workflow.planning_job_id)
            started = datetime.fromisoformat(job["createdAt"])
            elapsed = max(0, int((datetime.now(UTC) - started).total_seconds()))
            planning = {
                "state": job["state"],
                "model": (job.get("metadata") or {}).get("model"),
                "lastActivityAt": job.get("updatedAt"),
                "elapsedSeconds": elapsed,
                "timeoutRemainingSeconds": max(0, workflow.timeout_seconds - elapsed),
                "activity": job.get("activity") or [],
            }
        except KeyError:
            pass
    return {
        "id": workflow.id,
        "objective": workflow.objective,
        "owner": workflow.owner,
        "state": workflow.state,
        "createdAt": workflow.created_at,
        "updatedAt": workflow.updated_at,
        "executionSafetyProfile": workflow.execution_safety_profile,
        "maxCoinsPerRun": workflow.max_coins_per_run,
        "timeoutSeconds": workflow.timeout_seconds,
        "autoApprove": workflow.auto_approve,
        "planning": planning,
        "planningJobId": workflow.planning_job_id,
        "activeJobId": workflow.active_job_id,
        "projectContext": workflow.project_context,
        "tasks": [dict(task) for task in workflow.tasks],
        "error": workflow.error,
        "artifacts": [
            name
            for name in ("objective.md", "project-context.md", "tasks.json", "workflow.json", "workflow.zip")
            if workflow.run_dir is not None
            and (name == "workflow.zip" or (workflow.run_dir / name).is_file())
        ],
    }


def _workflow_dir(workflow_id: str, settings: Settings) -> Path:
    root = (Path(settings.workspace_root) / "workflows").resolve()
    run_dir = (root / workflow_id).resolve()
    if run_dir.parent != root:
        raise ValueError("Invalid workflow ID.")
    return run_dir


def _required(workflow_id: str) -> Workflow:
    workflow = _workflows.get(workflow_id)
    if workflow is None:
        raise KeyError(workflow_id)
    return workflow


def _now() -> str:
    return datetime.now(UTC).isoformat()
