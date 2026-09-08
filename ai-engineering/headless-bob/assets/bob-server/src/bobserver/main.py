from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from starlette.middleware.sessions import SessionMiddleware

from bobserver.appid import begin_login, finish_login, logout
from bobserver.auth import request_principal, require_admin
from bobserver.config import Settings, get_settings
from bobserver.mcp import handle_mcp_message
from bobserver.oauth import (
    authorization_server_metadata,
    authorize_page,
    authorize_submit,
    protected_resource_metadata,
    register_client,
    token_endpoint,
)
from bobserver.slack import handle_slack_command, handle_slack_events, handle_slack_interactivity
from bobserver.tasks import (
    BobPromptRequest,
    BobPromptResult,
    cancel_bob_prompt,
    bob_job_artifact,
    delete_bob_prompt_job,
    get_bob_prompt_status,
    list_bob_prompt_jobs,
    run_bob_prompt,
    start_bob_prompt,
    stream_bob_prompt,
)
from bobserver.sessions import (
    advance_phase,
    create_session,
    delete_session,
    get_artifact,
    get_current_session,
    send_message,
)
from bobserver.workflows import (
    WorkflowApproval,
    WorkflowRequest,
    approve_workflow,
    cancel_workflow,
    create_workflow,
    delete_workflow,
    get_workflow,
    list_workflows,
    workflow_artifact,
)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    import json as _json
    from bobserver.skills import list_skills
    from bobserver.sessions import _get_skills_registry_block
    from bobserver.tasks import _seed_mcp_config

    # ── Eager-load skills ──────────────────────────────────────────────────
    skills = list_skills()
    _get_skills_registry_block()  # warm the registry cache
    print(f"[bob+] {len(skills)} building-block skill(s) loaded:")
    for s in skills:
        ctx = len(s.get("contextFiles", []))
        print(f"[bob+]   ✓ {s['id']:45s} ({ctx} context files)")
    print(f"[bob+] Skills registry ready — injected into every Bob prompt.")

    # ── Report MCP config ─────────────────────────────────────────────────
    settings = get_settings()
    mcp_src = Path(settings.bob_mcp_config)
    if not mcp_src.is_absolute():
        mcp_src = (Path(__file__).parent.parent.parent / settings.bob_mcp_config).resolve()
    if mcp_src.is_file():
        try:
            mcp_data = _json.loads(mcp_src.read_text(encoding="utf-8"))
            servers = list(mcp_data.get("mcpServers", {}).keys())
            print(f"[bob+] MCP config: {mcp_src}")
            for srv in servers:
                print(f"[bob+]   ✓ MCP server: {srv}")
            print(f"[bob+] .bob/mcp.json will be seeded into every Bob run workspace.")
        except Exception as exc:
            print(f"[bob+] WARNING: could not read MCP config {mcp_src}: {exc}")
    else:
        print(f"[bob+] No MCP config found at {mcp_src} — Bob runs will have no MCP servers.")

    yield


app = FastAPI(
    title="Bobserver API",
    version="0.1.0",
    description=(
        "Protected REST and MCP service for managed Bob Shell runs and "
        "Plan → Approve → Execute workflows. Automation can authenticate with "
        "Basic auth or OAuth2 bearer tokens."
    ),
    openapi_tags=[
        {"name": "Bob runs", "description": "Start, observe, cancel, delete, and download artifacts from Bob Shell runs."},
        {"name": "Workflows", "description": "Skill-aware Plan → Approve → Execute workflows, including auto-approval."},
        {"name": "Bob+", "description": "5-phase guided planning sessions (Describe → Discovery → Architecture → Spec → Continue)."},
        {"name": "MCP", "description": "MCP JSON-RPC endpoint and OAuth discovery are documented in docs/claude-desktop-mcp.md."},
    ],
    lifespan=lifespan,
)


def _custom_openapi() -> dict:
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version=app.version, description=app.description, routes=app.routes, tags=app.openapi_tags)
    security_schemes = schema.setdefault("components", {}).setdefault("securitySchemes", {})
    security_schemes.update(
        {
            "BasicAuth": {"type": "http", "scheme": "basic"},
            "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "OAuth2 access token"},
            "OAuth2PKCE": {
                "type": "oauth2",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "/oauth/authorize",
                        "tokenUrl": "/oauth/token",
                        "scopes": {"bobserver:mcp": "Invoke Bobserver REST and MCP operations"},
                    }
                },
            },
        }
    )
    for path, operations in schema.get("paths", {}).items():
        if not (path.startswith("/api/") or path == "/mcp"):
            continue
        for operation in operations.values():
            if isinstance(operation, dict):
                operation["security"] = [
                    {"BasicAuth": []},
                    {"BearerAuth": []},
                    {"OAuth2PKCE": ["bobserver:mcp"]},
                ]
    app.openapi_schema = schema
    return schema


app.openapi = _custom_openapi
_startup_settings = get_settings()

# Allow the standalone demo UI (bobui/index.html opened via file:// or any
# local dev server) to call the API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=_startup_settings.appid_session_secret,
    session_cookie="bobserver_appid",
    same_site="lax",
    https_only=_startup_settings.appid_session_https_only,
    max_age=3600,
)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/slack/command", include_in_schema=False)
async def slack_command(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    return await handle_slack_command(request, settings)


@app.post("/slack/events", include_in_schema=False)
async def slack_events(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> Response:
    return await handle_slack_events(request, settings)


@app.post("/slack/interactivity", include_in_schema=False)
async def slack_interactivity(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    return await handle_slack_interactivity(request, settings)


@app.get("/.well-known/oauth-protected-resource", include_in_schema=False)
def oauth_protected_resource(request: Request) -> dict:
    return protected_resource_metadata(request)


@app.get("/.well-known/oauth-protected-resource/mcp", include_in_schema=False)
def oauth_protected_resource_mcp(request: Request) -> dict:
    return protected_resource_metadata(request)


@app.get("/.well-known/oauth-authorization-server", include_in_schema=False)
def oauth_authorization_server(request: Request) -> dict:
    return authorization_server_metadata(request)


@app.get("/.well-known/oauth-authorization-server/mcp", include_in_schema=False)
def oauth_authorization_server_mcp(request: Request) -> dict:
    return authorization_server_metadata(request)


@app.get("/.well-known/openid-configuration", include_in_schema=False)
def openid_configuration(request: Request) -> dict:
    return authorization_server_metadata(request)


@app.get("/.well-known/openid-configuration/mcp", include_in_schema=False)
def openid_configuration_mcp(request: Request) -> dict:
    return authorization_server_metadata(request)


@app.post("/oauth/register", include_in_schema=False)
async def oauth_register(request: Request) -> JSONResponse:
    return await register_client(request)


@app.get("/oauth/authorize", include_in_schema=False)
def oauth_authorize(request: Request) -> Response:
    return authorize_page(request)


@app.post("/oauth/authorize", include_in_schema=False)
async def oauth_authorize_post(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> Response:
    return await authorize_submit(request, settings)


@app.post("/oauth/token", include_in_schema=False)
async def oauth_token(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    return await token_endpoint(request, settings)


@app.get("/auth/login", include_in_schema=False)
async def appid_login(request: Request, settings: Settings = Depends(get_settings)) -> Response:
    return await begin_login(request, settings)


@app.get("/auth/appid/callback", include_in_schema=False)
async def appid_callback(request: Request, settings: Settings = Depends(get_settings)) -> Response:
    return await finish_login(request, settings)


@app.get("/auth/logout", include_in_schema=False)
def appid_logout(request: Request) -> Response:
    return logout(request)


@app.post("/api/bob/prompt", response_model=BobPromptResult)
def create_bob_prompt(
    request: BobPromptRequest,
    _admin: None = Depends(require_admin),
    settings: Settings = Depends(get_settings),
) -> BobPromptResult:
    return run_bob_prompt(request, settings)


@app.post("/api/bob/jobs")
def create_bob_job(
    request: BobPromptRequest,
    http_request: Request,
    _admin: None = Depends(require_admin),
    settings: Settings = Depends(get_settings),
) -> dict:
    return start_bob_prompt(request, settings, owner=request_principal(http_request, settings))


@app.post("/api/workflows")
def create_project_workflow(
    payload: WorkflowRequest,
    request: Request,
    _admin: None = Depends(require_admin),
    settings: Settings = Depends(get_settings),
) -> dict:
    return create_workflow(payload, request_principal(request, settings), settings)


@app.get("/api/workflows")
def list_project_workflows(_admin: None = Depends(require_admin)) -> list[dict]:
    return list_workflows()


@app.get("/api/workflows/{workflow_id}")
def read_project_workflow(workflow_id: str, _admin: None = Depends(require_admin)) -> dict:
    try:
        return get_workflow(workflow_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown workflow: {workflow_id}") from exc


@app.post("/api/workflows/{workflow_id}/approve")
def approve_project_workflow(
    workflow_id: str,
    approval: WorkflowApproval,
    _admin: None = Depends(require_admin),
    settings: Settings = Depends(get_settings),
) -> dict:
    try:
        return approve_workflow(workflow_id, approval, settings)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown workflow: {workflow_id}") from exc
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/api/workflows/{workflow_id}/cancel")
def cancel_project_workflow(workflow_id: str, _admin: None = Depends(require_admin)) -> dict:
    try:
        return cancel_workflow(workflow_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown workflow: {workflow_id}") from exc


@app.delete("/api/workflows/{workflow_id}", status_code=204)
def delete_project_workflow(
    workflow_id: str,
    _admin: None = Depends(require_admin),
    settings: Settings = Depends(get_settings),
) -> Response:
    try:
        delete_workflow(workflow_id, settings)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown workflow: {workflow_id}") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return Response(status_code=204)


@app.get("/api/workflows/{workflow_id}/artifacts/{artifact_name}")
def download_workflow_artifact(
    workflow_id: str,
    artifact_name: str,
    _admin: None = Depends(require_admin),
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    try:
        artifact = workflow_artifact(workflow_id, artifact_name, settings)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown workflow: {workflow_id}") from exc
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    media_type = "application/zip" if artifact_name.endswith(".zip") else (
        "application/json" if artifact_name.endswith(".json") else "text/markdown"
    )
    return FileResponse(artifact, media_type=media_type, filename=f"{workflow_id}-{artifact_name}")


@app.get("/api/bob/jobs")
def list_bob_jobs(_admin: None = Depends(require_admin)) -> list[dict]:
    return list_bob_prompt_jobs()


@app.get("/api/bob/jobs/{job_id}")
def read_bob_job(
    job_id: str,
    offset: int = 0,
    _admin: None = Depends(require_admin),
) -> dict:
    try:
        return get_bob_prompt_status(job_id, offset=offset)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown Bob job: {job_id}") from exc


@app.post("/api/bob/jobs/{job_id}/cancel")
def cancel_bob_job(
    job_id: str,
    _admin: None = Depends(require_admin),
) -> dict:
    try:
        return cancel_bob_prompt(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown Bob job: {job_id}") from exc


@app.delete("/api/bob/jobs/{job_id}", status_code=204)
def delete_bob_job(
    job_id: str,
    _admin: None = Depends(require_admin),
    settings: Settings = Depends(get_settings),
) -> Response:
    try:
        delete_bob_prompt_job(job_id, settings)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown Bob job: {job_id}") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return Response(status_code=204)


@app.get("/api/bob/jobs/{job_id}/artifacts/{artifact_name}")
def download_bob_artifact(
    job_id: str,
    artifact_name: str,
    _admin: None = Depends(require_admin),
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    try:
        artifact = bob_job_artifact(job_id, artifact_name, settings)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown Bob job: {job_id}") from exc
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    media_type = {
        "bob-run.json": "application/json",
        "workspace.zip": "application/zip",
    }.get(artifact_name, "text/markdown")
    return FileResponse(artifact, media_type=media_type, filename=f"{job_id}-{artifact_name}")


@app.post("/api/bob/stream")
def stream_bob(
    request: BobPromptRequest,
    _admin: None = Depends(require_admin),
    settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    return StreamingResponse(
        stream_bob_prompt(request, settings),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/mcp")
async def mcp(
    request: Request,
    _admin: None = Depends(require_admin),
    settings: Settings = Depends(get_settings),
) -> Response:
    payload = await request.json()
    if isinstance(payload, list):
        responses = [handle_mcp_message(message, settings) for message in payload]
        return JSONResponse([response for response in responses if response is not None])
    response = handle_mcp_message(payload, settings)
    if response is None:
        return Response(status_code=202)
    return JSONResponse(response)


# ---------------------------------------------------------------------------
# Bob+ Session endpoints
# ---------------------------------------------------------------------------

class SessionCreateRequest(BaseModel):
    title: str = ""


class SessionMessageRequest(BaseModel):
    message: str


@app.post("/api/sessions", tags=["Bob+"])
def create_bob_session(
    payload: SessionCreateRequest,
    _admin: None = Depends(require_admin),
    settings: Settings = Depends(get_settings),
) -> dict:
    return create_session(payload.title, settings)


@app.get("/api/sessions/current", tags=["Bob+"])
def get_bob_session(_admin: None = Depends(require_admin)) -> dict:
    session = get_current_session()
    if session is None:
        raise HTTPException(status_code=404, detail="No active session.")
    return session


@app.post("/api/sessions/{session_id}/message", tags=["Bob+"])
def bob_session_message(
    session_id: str,
    payload: SessionMessageRequest,
    _admin: None = Depends(require_admin),
    settings: Settings = Depends(get_settings),
) -> dict:
    try:
        return send_message(session_id, payload.message, settings)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/sessions/{session_id}/advance", tags=["Bob+"])
def bob_session_advance(
    session_id: str,
    _admin: None = Depends(require_admin),
    settings: Settings = Depends(get_settings),
) -> dict:
    try:
        return advance_phase(session_id, settings)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/api/sessions/{session_id}/artifact/{phase_id}", tags=["Bob+"])
def bob_session_artifact(
    session_id: str,
    phase_id: str,
    _admin: None = Depends(require_admin),
) -> dict:
    try:
        content = get_artifact(session_id, phase_id)
        return {"phaseId": phase_id, "content": content}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.delete("/api/sessions/{session_id}", status_code=204, tags=["Bob+"])
def delete_bob_session(
    session_id: str,
    _admin: None = Depends(require_admin),
) -> Response:
    try:
        delete_session(session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(status_code=204)


def main() -> None:
    import uvicorn
    uvicorn.run("bobserver.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
