from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass
from html import escape
from typing import Any
from urllib.parse import parse_qs, urlencode

from fastapi import HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from bobserver.config import Settings

OAUTH_SCOPE = "bobserver:mcp"


@dataclass
class OAuthClient:
    client_id: str
    redirect_uris: list[str]
    client_name: str = "MCP client"


@dataclass
class OAuthCode:
    client_id: str
    redirect_uri: str
    code_challenge: str
    scope: str
    resource: str | None
    expires_at: float


@dataclass
class OAuthToken:
    scope: str
    resource: str | None
    expires_at: float


_clients: dict[str, OAuthClient] = {}
_codes: dict[str, OAuthCode] = {}
_tokens: dict[str, OAuthToken] = {}


def external_base_url(request: Request) -> str:
    proto = request.headers.get("x-forwarded-proto", request.url.scheme).split(",")[0].strip()
    host = request.headers.get("x-forwarded-host", request.headers.get("host", request.url.netloc))
    return f"{proto}://{host}".rstrip("/")


def mcp_resource_url(request: Request) -> str:
    return f"{external_base_url(request)}/mcp"


def resource_metadata_url(request: Request) -> str:
    return f"{external_base_url(request)}/.well-known/oauth-protected-resource"


def bearer_challenge(request: Request, error: str | None = None) -> str:
    parts = [
        f'resource_metadata="{resource_metadata_url(request)}"',
        f'scope="{OAUTH_SCOPE}"',
    ]
    if error:
        parts.insert(0, f'error="{error}"')
    return f"Bearer {', '.join(parts)}"


def protected_resource_metadata(request: Request) -> dict[str, Any]:
    base_url = external_base_url(request)
    return {
        "resource": mcp_resource_url(request),
        "authorization_servers": [base_url],
        "scopes_supported": [OAUTH_SCOPE],
        "bearer_methods_supported": ["header"],
    }


def authorization_server_metadata(request: Request) -> dict[str, Any]:
    base_url = external_base_url(request)
    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/oauth/authorize",
        "token_endpoint": f"{base_url}/oauth/token",
        "registration_endpoint": f"{base_url}/oauth/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["none"],
        "scopes_supported": [OAUTH_SCOPE],
    }


async def register_client(request: Request) -> JSONResponse:
    payload = await request.json()
    redirect_uris = payload.get("redirect_uris")
    if not isinstance(redirect_uris, list) or not all(isinstance(uri, str) for uri in redirect_uris):
        raise HTTPException(status_code=400, detail="redirect_uris must be a list of strings.")

    client_id = secrets.token_urlsafe(24)
    client = OAuthClient(
        client_id=client_id,
        redirect_uris=redirect_uris,
        client_name=str(payload.get("client_name") or "MCP client"),
    )
    _clients[client_id] = client
    return JSONResponse(
        {
            "client_id": client_id,
            "client_id_issued_at": int(time.time()),
            "client_name": client.client_name,
            "redirect_uris": redirect_uris,
            "grant_types": ["authorization_code"],
            "response_types": ["code"],
            "scope": OAUTH_SCOPE,
            "token_endpoint_auth_method": "none",
        },
        status_code=201,
    )


def authorize_page(request: Request) -> HTMLResponse:
    params = dict(request.query_params)
    error = _validate_authorize_params(params)
    if error:
        return _oauth_error_page(error, status_code=400)

    client = _clients.get(params["client_id"])
    client_name = client.client_name if client else "MCP client"
    hidden_fields = "\n".join(
        f'<input type="hidden" name="{escape(key)}" value="{escape(value)}" />'
        for key, value in params.items()
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Authorize Bobserver</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; max-width: 34rem; }}
    label {{ display: block; margin: 1rem 0 0.35rem; }}
    input {{ box-sizing: border-box; width: 100%; padding: 0.65rem; }}
    button {{ margin-top: 1rem; padding: 0.65rem 0.9rem; }}
  </style>
</head>
<body>
  <h1>Authorize Bobserver</h1>
  <p>{escape(client_name)} is requesting access to Bobserver MCP tools.</p>
  <form method="post" action="/oauth/authorize">
    {hidden_fields}
    <label for="username">Username</label>
    <input id="username" name="username" autocomplete="username" required />
    <label for="password">Password</label>
    <input id="password" name="password" type="password" autocomplete="current-password" required />
    <button type="submit">Authorize</button>
  </form>
</body>
</html>"""
    return HTMLResponse(html)


async def authorize_submit(request: Request, settings: Settings) -> Response:
    form = await _form_data(request)
    username = form.pop("username", "")
    password = form.pop("password", "")
    if not _valid_admin_credentials(username, password, settings):
        return _oauth_error_page("Invalid Bobserver credentials.", status_code=401)

    error = _validate_authorize_params(form)
    if error:
        return _oauth_error_page(error, status_code=400)

    code = secrets.token_urlsafe(32)
    scope = form.get("scope") or OAUTH_SCOPE
    _codes[code] = OAuthCode(
        client_id=form["client_id"],
        redirect_uri=form["redirect_uri"],
        code_challenge=form["code_challenge"],
        scope=scope,
        resource=form.get("resource"),
        expires_at=time.time() + 300,
    )
    redirect_params = {"code": code}
    if form.get("state"):
        redirect_params["state"] = form["state"]
    separator = "&" if "?" in form["redirect_uri"] else "?"
    return RedirectResponse(f"{form['redirect_uri']}{separator}{urlencode(redirect_params)}", status_code=302)


async def token_endpoint(request: Request, settings: Settings) -> JSONResponse:
    form = await _form_data(request)
    if form.get("grant_type") != "authorization_code":
        return _oauth_token_error("unsupported_grant_type", "Only authorization_code is supported.")

    code = _codes.pop(form.get("code", ""), None)
    if code is None or code.expires_at < time.time():
        return _oauth_token_error("invalid_grant", "Authorization code is invalid or expired.")
    if form.get("client_id") != code.client_id or form.get("redirect_uri") != code.redirect_uri:
        return _oauth_token_error("invalid_grant", "Authorization code binding does not match.")
    if not _verify_pkce(form.get("code_verifier", ""), code.code_challenge):
        return _oauth_token_error("invalid_grant", "PKCE verification failed.")

    token_value = secrets.token_urlsafe(32)
    ttl = settings.oauth_access_token_ttl_seconds
    _tokens[token_value] = OAuthToken(
        scope=code.scope,
        resource=code.resource,
        expires_at=time.time() + ttl,
    )
    return JSONResponse(
        {
            "access_token": token_value,
            "token_type": "Bearer",
            "expires_in": ttl,
            "scope": code.scope,
        }
    )


def validate_bearer_token(token: str, request: Request) -> bool:
    record = _tokens.get(token)
    if record is None:
        return False
    if record.expires_at < time.time():
        _tokens.pop(token, None)
        return False
    if record.resource and record.resource.rstrip("/") != mcp_resource_url(request).rstrip("/"):
        return False
    return OAUTH_SCOPE in record.scope.split()


def reset_oauth_state() -> None:
    _clients.clear()
    _codes.clear()
    _tokens.clear()


def _validate_authorize_params(params: dict[str, str]) -> str | None:
    if params.get("response_type") != "code":
        return "response_type must be code."
    client_id = params.get("client_id")
    if not client_id:
        return "client_id is required."
    redirect_uri = params.get("redirect_uri")
    if not redirect_uri:
        return "redirect_uri is required."
    client = _clients.get(client_id)
    if client and redirect_uri not in client.redirect_uris:
        return "redirect_uri is not registered for this client."
    if params.get("code_challenge_method") != "S256":
        return "code_challenge_method must be S256."
    if not params.get("code_challenge"):
        return "code_challenge is required."
    return None


async def _form_data(request: Request) -> dict[str, str]:
    body = (await request.body()).decode("utf-8")
    return {key: values[-1] for key, values in parse_qs(body, keep_blank_values=True).items()}


def _valid_admin_credentials(username: str, password: str, settings: Settings) -> bool:
    username_ok = hmac.compare_digest(username, settings.admin_username)
    password_ok = hmac.compare_digest(password, settings.admin_password)
    return username_ok and password_ok


def _verify_pkce(verifier: str, challenge: str) -> bool:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    expected = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return hmac.compare_digest(expected, challenge)


def _oauth_error_page(message: str, status_code: int) -> HTMLResponse:
    return HTMLResponse(
        f"<!doctype html><title>OAuth error</title><h1>OAuth error</h1><p>{escape(message)}</p>",
        status_code=status_code,
    )


def _oauth_token_error(error: str, description: str) -> JSONResponse:
    return JSONResponse(
        {"error": error, "error_description": description},
        status_code=status.HTTP_400_BAD_REQUEST,
    )
