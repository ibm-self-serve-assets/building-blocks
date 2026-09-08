import base64
import secrets

from fastapi import Depends, HTTPException, Request, status

from bobserver.config import Settings, get_settings
from bobserver.oauth import bearer_challenge, validate_bearer_token


def require_admin(request: Request, settings: Settings = Depends(get_settings)) -> None:
    if appid_session_user(request):
        return
    if valid_basic_or_bearer(request, settings):
        return
    raise _unauthorized(request)


def valid_basic_or_bearer(request: Request, settings: Settings) -> bool:
    authorization = request.headers.get("authorization", "")
    scheme, _, value = authorization.partition(" ")
    if scheme.lower() == "bearer" and value:
        if validate_bearer_token(value, request):
            return True
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token.",
            headers={"WWW-Authenticate": bearer_challenge(request, error="invalid_token")},
        )
    if scheme.lower() == "basic" and value:
        try:
            decoded = base64.b64decode(value).decode("utf-8")
        except Exception as exc:
            raise _unauthorized(request) from exc
        username, separator, password = decoded.partition(":")
        if separator and _valid_basic_credentials(username, password, settings):
            return True
    return False


def appid_session_user(request: Request) -> dict | None:
    user = request.session.get("appid_user")
    return user if isinstance(user, dict) and user.get("sub") else None


def request_principal(request: Request, settings: Settings) -> dict:
    user = appid_session_user(request)
    if user:
        return {
            "id": str(user["sub"]),
            "name": str(user.get("name") or user.get("email") or "App ID user"),
            "email": str(user.get("email") or ""),
            "authMethod": "appid",
        }
    authorization = request.headers.get("authorization", "")
    scheme, _, value = authorization.partition(" ")
    if scheme.lower() == "basic" and value:
        try:
            username, separator, password = base64.b64decode(value).decode("utf-8").partition(":")
        except Exception:
            username, separator, password = "", "", ""
        if separator and _valid_basic_credentials(username, password, settings):
            return {"id": username, "name": username, "email": "", "authMethod": "basic"}
    if scheme.lower() == "bearer" and value and validate_bearer_token(value, request):
        return {"id": "oauth-client", "name": "OAuth client", "email": "", "authMethod": "bearer"}
    raise _unauthorized(request)


def _valid_basic_credentials(username: str, password: str, settings: Settings) -> bool:
    username_ok = secrets.compare_digest(username, settings.admin_username)
    password_ok = secrets.compare_digest(password, settings.admin_password)
    return username_ok and password_ok


def _unauthorized(request: Request) -> HTTPException:
    authenticate = f'Basic realm="Bobserver", {bearer_challenge(request)}'
    if request.url.path == "/mcp":
        authenticate = f'{bearer_challenge(request)}, Basic realm="Bobserver"'
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials.",
        headers={"WWW-Authenticate": authenticate},
    )
