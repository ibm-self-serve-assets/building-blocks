from typing import Any

from bobserver.config import Settings
from bobserver.tasks import (
    BobPromptRequest,
    bob_job_artifact,
    cancel_bob_prompt,
    delete_bob_prompt_job,
    get_bob_prompt_status,
    start_bob_prompt,
)
from bobserver.workflows import (
    WorkflowApproval,
    WorkflowRequest,
    approve_workflow,
    cancel_workflow,
    create_workflow,
    get_workflow,
    list_workflows,
)

MCP_PROTOCOL_VERSION = "2025-06-18"
SERVER_INFO = {"name": "bobserver", "version": "0.1.0"}

BOB_PROMPT_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "prompt": {
            "type": "string",
            "description": "Prompt to send to Bob Shell.",
        },
        "timeoutSeconds": {
            "type": "integer",
            "minimum": 1,
            "maximum": 900,
            "default": 120,
            "description": "Maximum time to wait for Bob Shell.",
        },
        "yolo": {
            "type": "boolean",
            "default": False,
            "description": "Allow Bob Shell to create and update files under /workspace.",
        },
        "safetyProfile": {
            "type": "string",
            "enum": ["readonly", "edit", "trusted"],
            "default": "readonly",
            "description": "Bob tool policy. yolo=true overrides this with trusted.",
        },
        "maxCoins": {
            "type": "integer",
            "minimum": 1,
            "maximum": 100,
            "default": 30,
            "description": "Per-run Bob coin budget, capped by the server configuration.",
        },
        "workspaceMode": {
            "type": "string",
            "enum": ["isolated", "shared"],
            "default": "isolated",
            "description": "Use a per-run isolated workspace or the shared compatibility workspace.",
        },
    },
    "required": ["prompt"],
    "additionalProperties": False,
}

BOB_PROMPT_START_TOOL = {
    "name": "bob_prompt_start",
    "title": "Start Bob Shell Prompt",
    "description": "Start a Bob Shell prompt asynchronously and return a job id immediately.",
    "inputSchema": BOB_PROMPT_INPUT_SCHEMA,
}

BOB_PROMPT_STATUS_TOOL = {
    "name": "bob_prompt_status",
    "title": "Read Bob Prompt Status",
    "description": "Read current status and new output for an asynchronous Bob Shell prompt job.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "jobId": {
                "type": "string",
                "description": "Job id returned by bob_prompt_start.",
            },
            "offset": {
                "type": "integer",
                "minimum": 0,
                "default": 0,
                "description": "Output offset returned by the previous bob_prompt_status call.",
            },
        },
        "required": ["jobId"],
        "additionalProperties": False,
    },
}

BOB_PROMPT_CANCEL_TOOL = {
    "name": "bob_prompt_cancel",
    "title": "Cancel Bob Prompt",
    "description": "Cancel a running asynchronous Bob Shell prompt job.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "jobId": {
                "type": "string",
                "description": "Job id returned by bob_prompt_start.",
            },
        },
        "required": ["jobId"],
        "additionalProperties": False,
    },
}

BOB_PROMPT_DELETE_TOOL = {
    "name": "bob_prompt_delete",
    "title": "Delete Bob Prompt Run",
    "description": "Delete a terminal Bob run and its local artifacts.",
    "inputSchema": BOB_PROMPT_CANCEL_TOOL["inputSchema"],
}

BOB_PROMPT_ARTIFACT_TOOL = {
    "name": "bob_prompt_artifact",
    "title": "Read Bob Prompt Artifact",
    "description": "Read a text artifact from a Bob run. ZIP files remain available through the HTTP API.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "jobId": {"type": "string"},
            "artifact": {"type": "string", "enum": ["result.md", "bob-run.json", "prompt.md"]},
        },
        "required": ["jobId", "artifact"],
        "additionalProperties": False,
    },
}

WORKFLOW_START_TOOL = {
    "name": "bob_workflow_start",
    "title": "Plan and Execute Bob Workflow",
    "description": "Create a skill-aware plan. Set autoApprove=true to execute immediately after validation, or false to require approval.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "objective": {"type": "string", "minLength": 3},
            "autoApprove": {"type": "boolean", "default": False},
            "executionSafetyProfile": {"type": "string", "enum": ["readonly", "edit", "trusted"], "default": "edit"},
            "maxCoinsPerRun": {"type": "integer", "minimum": 1, "maximum": 30, "default": 10},
            "timeoutSeconds": {"type": "integer", "minimum": 10, "maximum": 900, "default": 300},
        },
        "required": ["objective"],
        "additionalProperties": False,
    },
}

WORKFLOW_ID_SCHEMA = {
    "type": "object",
    "properties": {"workflowId": {"type": "string"}},
    "required": ["workflowId"],
    "additionalProperties": False,
}

WORKFLOW_STATUS_TOOL = {"name": "bob_workflow_status", "title": "Read Bob Workflow Status", "description": "Read plan, selected skills, execution status, activity, and results.", "inputSchema": WORKFLOW_ID_SCHEMA}
WORKFLOW_APPROVE_TOOL = {"name": "bob_workflow_approve", "title": "Approve Bob Workflow", "description": "Approve a workflow that is awaiting approval.", "inputSchema": WORKFLOW_ID_SCHEMA}
WORKFLOW_CANCEL_TOOL = {"name": "bob_workflow_cancel", "title": "Cancel Bob Workflow", "description": "Cancel a workflow and its active child process group.", "inputSchema": WORKFLOW_ID_SCHEMA}
WORKFLOW_LIST_TOOL = {"name": "bob_workflow_list", "title": "List Bob Workflows", "description": "List in-memory workflows for this server instance.", "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}}

TOOLS = [
    BOB_PROMPT_START_TOOL,
    BOB_PROMPT_STATUS_TOOL,
    BOB_PROMPT_CANCEL_TOOL,
    BOB_PROMPT_DELETE_TOOL,
    BOB_PROMPT_ARTIFACT_TOOL,
    WORKFLOW_START_TOOL,
    WORKFLOW_STATUS_TOOL,
    WORKFLOW_APPROVE_TOOL,
    WORKFLOW_CANCEL_TOOL,
    WORKFLOW_LIST_TOOL,
]


def handle_mcp_message(message: dict[str, Any], settings: Settings) -> dict[str, Any] | None:
    request_id = message.get("id")
    method = message.get("method")

    if request_id is None:
        return None

    try:
        if method == "initialize":
            return _result(
                request_id,
                {
                    "protocolVersion": MCP_PROTOCOL_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": SERVER_INFO,
                    "instructions": (
                        "Bobserver exposes Bob Shell through MCP tools. "
                        "Use bob_prompt_start and bob_prompt_status for work "
                        "in /workspace."
                    ),
                },
            )
        if method == "ping":
            return _result(request_id, {})
        if method == "tools/list":
            return _result(request_id, {"tools": TOOLS})
        if method == "tools/call":
            return _handle_tools_call(request_id, message.get("params") or {}, settings)
        if method in {"resources/list", "prompts/list"}:
            key = "resources" if method == "resources/list" else "prompts"
            return _result(request_id, {key: []})
        return _error(request_id, -32601, f"Method not found: {method}")
    except Exception as exc:
        return _error(request_id, -32603, str(exc))


def _handle_tools_call(request_id: Any, params: dict[str, Any], settings: Settings) -> dict[str, Any]:
    name = params.get("name")
    arguments = params.get("arguments") or {}

    if name == "bob_prompt_start":
        return _call_bob_prompt_start(request_id, arguments, settings)
    if name == "bob_prompt_status":
        return _call_bob_prompt_status(request_id, arguments)
    if name == "bob_prompt_cancel":
        return _call_bob_prompt_cancel(request_id, arguments)
    if name == "bob_prompt_delete":
        return _call_bob_prompt_delete(request_id, arguments, settings)
    if name == "bob_prompt_artifact":
        return _call_bob_prompt_artifact(request_id, arguments, settings)
    if name == "bob_workflow_start":
        return _call_workflow_start(request_id, arguments, settings)
    if name == "bob_workflow_status":
        return _call_workflow_action(request_id, arguments, "status", settings)
    if name == "bob_workflow_approve":
        return _call_workflow_action(request_id, arguments, "approve", settings)
    if name == "bob_workflow_cancel":
        return _call_workflow_action(request_id, arguments, "cancel", settings)
    if name == "bob_workflow_list":
        return _workflow_result(request_id, list_workflows())
    return _error(request_id, -32602, f"Unknown tool: {name}")


def _call_workflow_start(request_id: Any, arguments: dict[str, Any], settings: Settings) -> dict[str, Any]:
    objective = arguments.get("objective")
    if not isinstance(objective, str) or len(objective.strip()) < 3:
        return _error(request_id, -32602, "bob_workflow_start requires a non-empty objective.")
    payload = create_workflow(
        WorkflowRequest.model_validate(arguments),
        {"id": "mcp-client", "name": "MCP client", "email": "", "authMethod": "bearer"},
        settings,
    )
    return _workflow_result(request_id, payload)


def _call_workflow_action(request_id: Any, arguments: dict[str, Any], action: str, settings: Settings) -> dict[str, Any]:
    workflow_id = arguments.get("workflowId")
    if not isinstance(workflow_id, str) or not workflow_id:
        return _error(request_id, -32602, f"bob_workflow_{action} requires workflowId.")
    try:
        if action == "approve":
            payload = approve_workflow(workflow_id, WorkflowApproval(), settings)
        elif action == "cancel":
            payload = cancel_workflow(workflow_id)
        else:
            payload = get_workflow(workflow_id)
    except (KeyError, RuntimeError, ValueError) as exc:
        return _error(request_id, -32602, str(exc))
    return _workflow_result(request_id, payload)


def _workflow_result(request_id: Any, payload: Any) -> dict[str, Any]:
    return _result(request_id, {"content": [{"type": "text", "text": str(payload)}], "structuredContent": payload, "isError": False})

def _call_bob_prompt_start(request_id: Any, arguments: dict[str, Any], settings: Settings) -> dict[str, Any]:
    prompt = arguments.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        return _error(request_id, -32602, "bob_prompt_start requires a non-empty prompt string.")

    payload = start_bob_prompt(
        BobPromptRequest(
            prompt=prompt,
            timeoutSeconds=int(arguments.get("timeoutSeconds") or 120),
            yolo=bool(arguments.get("yolo", False)),
            safetyProfile=str(arguments.get("safetyProfile") or "readonly"),
            maxCoins=int(arguments.get("maxCoins") or 30),
            workspaceMode=str(arguments.get("workspaceMode") or "isolated"),
        ),
        settings,
        owner={"id": "mcp-client", "name": "MCP client", "email": "", "authMethod": "bearer"},
    )
    return _result(
        request_id,
        {
            "content": [
                {
                    "type": "text",
                    "text": _format_job_payload(payload, include_output=False),
                }
            ],
            "structuredContent": payload,
            "isError": False,
        },
    )


def _call_bob_prompt_status(request_id: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    job_id = arguments.get("jobId")
    if not isinstance(job_id, str) or not job_id.strip():
        return _error(request_id, -32602, "bob_prompt_status requires jobId.")
    try:
        payload = get_bob_prompt_status(job_id, offset=int(arguments.get("offset") or 0))
    except KeyError:
        return _error(request_id, -32602, f"Unknown Bob job: {job_id}")
    return _result(
        request_id,
        {
            "content": [{"type": "text", "text": _format_job_payload(payload)}],
            "structuredContent": payload,
            "isError": payload["state"] == "failed",
        },
    )


def _call_bob_prompt_cancel(request_id: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    job_id = arguments.get("jobId")
    if not isinstance(job_id, str) or not job_id.strip():
        return _error(request_id, -32602, "bob_prompt_cancel requires jobId.")
    try:
        payload = cancel_bob_prompt(job_id)
    except KeyError:
        return _error(request_id, -32602, f"Unknown Bob job: {job_id}")
    return _result(
        request_id,
        {
            "content": [{"type": "text", "text": _format_job_payload(payload)}],
            "structuredContent": payload,
            "isError": False,
        },
    )


def _call_bob_prompt_delete(request_id: Any, arguments: dict[str, Any], settings: Settings) -> dict[str, Any]:
    job_id = arguments.get("jobId")
    if not isinstance(job_id, str) or not job_id:
        return _error(request_id, -32602, "bob_prompt_delete requires jobId.")
    try:
        delete_bob_prompt_job(job_id, settings)
    except (KeyError, RuntimeError) as exc:
        return _error(request_id, -32602, str(exc))
    return _result(request_id, {"content": [{"type": "text", "text": f"Deleted run {job_id}."}], "structuredContent": {"id": job_id, "deleted": True}, "isError": False})


def _call_bob_prompt_artifact(request_id: Any, arguments: dict[str, Any], settings: Settings) -> dict[str, Any]:
    job_id = arguments.get("jobId")
    artifact = arguments.get("artifact")
    if not isinstance(job_id, str) or artifact not in {"result.md", "bob-run.json", "prompt.md"}:
        return _error(request_id, -32602, "bob_prompt_artifact requires jobId and a supported text artifact.")
    try:
        text = bob_job_artifact(job_id, artifact, settings).read_text(encoding="utf-8")
    except (KeyError, ValueError, FileNotFoundError, OSError) as exc:
        return _error(request_id, -32602, str(exc))
    return _result(request_id, {"content": [{"type": "text", "text": text}], "structuredContent": {"jobId": job_id, "artifact": artifact, "text": text}, "isError": False})


def _format_job_payload(payload: dict[str, Any], *, include_output: bool = True) -> str:
    lines = [
        f"jobId: {payload['id']}",
        f"state: {payload['state']}",
        f"exitCode: {payload.get('exitCode')}",
        f"nextOffset: {payload.get('nextOffset', 0)}",
    ]
    if include_output and payload.get("output"):
        lines.extend(["", payload["output"]])
    if payload.get("error"):
        lines.extend(["", payload["error"]])
    return "\n".join(lines)


def _result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code,
            "message": message,
        },
    }
