from __future__ import annotations

from urllib.parse import urlsplit

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse

from bobserver.config import Settings
from bobserver.oauth import external_base_url


CALLBACK_PATH = "/auth/appid/callback"


def appid_configured(settings: Settings) -> bool:
    return bool(
        settings.appid_client_id
        and settings.appid_client_secret
        and settings.appid_discovery_endpoint
    )


def callback_uri(request: Request, settings: Settings) -> str:
    return settings.appid_redirect_uri or f"{external_base_url(request)}{CALLBACK_PATH}"


async def begin_login(request: Request, settings: Settings) -> RedirectResponse:
    if not appid_configured(settings):
        raise HTTPException(status_code=503, detail="IBM Cloud App ID is not configured.")
    request.session["appid_return_to"] = _safe_return_to(request.query_params.get("next"))
    return await _client(settings).authorize_redirect(request, callback_uri(request, settings))


async def finish_login(request: Request, settings: Settings) -> RedirectResponse:
    if not appid_configured(settings):
        raise HTTPException(status_code=503, detail="IBM Cloud App ID is not configured.")
    try:
        token = await _client(settings).authorize_access_token(request)
    except OAuthError as exc:
        raise HTTPException(status_code=401, detail="App ID login failed.") from exc
    user = token.get("userinfo")
    if not isinstance(user, dict) or not user.get("sub"):
        raise HTTPException(status_code=401, detail="App ID did not return a valid identity.")
    request.session["appid_user"] = {
        key: user[key]
        for key in ("sub", "email", "name", "given_name", "family_name")
        if user.get(key)
    }
    destination = _safe_return_to(request.session.pop("appid_return_to", "/"))
    return RedirectResponse(destination, status_code=303)


def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return RedirectResponse("/auth/login", status_code=303)


def _client(settings: Settings):
    oauth = OAuth()
    return oauth.register(
        name="appid",
        client_id=settings.appid_client_id,
        client_secret=settings.appid_client_secret,
        server_metadata_url=settings.appid_discovery_endpoint,
        client_kwargs={"scope": "openid email profile"},
    )


def _safe_return_to(value: str | None) -> str:
    candidate = value or "/"
    parsed = urlsplit(candidate)
    if parsed.scheme or parsed.netloc or not candidate.startswith("/") or candidate.startswith("//"):
        return "/"
    return candidate
