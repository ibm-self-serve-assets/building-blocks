"""
Lazy singleton HTTP client for GitHub API access with TTL caching.

Authentication modes (auto-detected from env vars, first match wins):

1. GitHub App (preferred for prod)
   - GH_APP_ID                  GitHub App ID (a number)
   - GH_APP_INSTALLATION_ID     Installation ID on the target org
   - GH_APP_PRIVATE_KEY         PEM private key (raw multiline OR base64-encoded)
   - Mints short-lived (1-hour) installation tokens via JWT; auto-refreshes.
   - Rate limit: 5,000/hr per installation; up to ~12,500/hr on GHEC orgs.

2. Personal access token (fallback / local dev)
   - GITHUB_TOKEN               Classic or fine-grained PAT
   - Rate limit: 5,000/hr.

3. Unauthenticated (warning logged)
   - No env vars set
   - Rate limit: 60/hr; code search disabled.

Observability
-------------
Every response from api.github.com logs the rate-limit headers
(X-RateLimit-Resource, X-RateLimit-Remaining, X-RateLimit-Limit) at INFO level
so you can wire a dashboard or alert on remaining budget.

Server-wide budget for code search
----------------------------------
GitHub's search API enforces a hard 30/min cap, separate from the 5K/hr core
budget. To prevent any one client from starving everyone else, search_code()
takes from a server-wide token bucket sized at 25/min — if depleted, the call
returns an explicit error instead of letting GitHub return 403.
"""

from __future__ import annotations

import base64
import logging
import os
import threading
import time
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_OWNER = "ibm-self-serve-assets"
REPO_NAME = "building-blocks"
DOCS_REPO_NAME = "building-blocks-docs"
DEFAULT_BRANCH = "main"

API_BASE = "https://api.github.com"
RAW_BASE = "https://raw.githubusercontent.com"

USER_AGENT = "building-blocks-mcp-remote-marketplace/0.3.0"

# Cache settings
CACHE_TTL_DEFAULT = 300   # 5 minutes
CACHE_TTL_TREE = 600      # 10 minutes
CACHE_TTL_SEARCH = 120    # 2 minutes
CACHE_MAX_ENTRIES = 500

# Server-wide search budget (GitHub hard cap is 30/min; we stay at 25 to leave headroom)
SEARCH_BUDGET_MAX = 25
SEARCH_BUDGET_REFILL_PER_SEC = 25 / 60.0

# Installation token refresh: refresh when within this many seconds of expiry
TOKEN_REFRESH_BUFFER = 60

_cache: dict[str, tuple[float, Any]] = {}
_cache_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Authentication state — picks an auth mode at first use, refreshes if needed
# ---------------------------------------------------------------------------


class _AuthState:
    """Resolves env vars into an auth mode + token-supply method.

    `get_api_token()` returns the right Bearer value to send on api.github.com
    calls. For App mode it transparently refreshes the installation token via
    JWT before expiry. For PAT mode it returns the static token. For
    unauthenticated mode it returns None.
    """

    def __init__(self) -> None:
        self.mode: str = "none"
        self.app_id: Optional[str] = None
        self.installation_id: Optional[str] = None
        self.private_key_pem: Optional[str] = None
        self.pat: Optional[str] = None
        self._installation_token: Optional[str] = None
        self._installation_token_expires_at: float = 0.0
        self._lock = threading.Lock()
        self._initialize()

    def _initialize(self) -> None:
        app_id = os.environ.get("GH_APP_ID")
        inst_id = os.environ.get("GH_APP_INSTALLATION_ID")
        raw_key = os.environ.get("GH_APP_PRIVATE_KEY")
        if app_id and inst_id and raw_key:
            self.mode = "app"
            self.app_id = app_id
            self.installation_id = inst_id
            # Accept either raw PEM (multiline) or base64-encoded PEM (single line).
            if "BEGIN" in raw_key:
                self.private_key_pem = raw_key
            else:
                self.private_key_pem = base64.b64decode(raw_key).decode("utf-8")
            logger.info(
                "GitHub auth: App mode (app_id=%s installation=%s)", app_id, inst_id
            )
            return

        pat = os.environ.get("GITHUB_TOKEN")
        if pat:
            self.mode = "pat"
            self.pat = pat
            logger.info("GitHub auth: PAT mode")
            return

        logger.warning(
            "GitHub auth: NONE — rate limit is 60 req/hr; code search disabled. "
            "Set GH_APP_* env vars (preferred) or GITHUB_TOKEN."
        )

    def get_api_token(self) -> Optional[str]:
        """Return current Bearer token for api.github.com, refreshing as needed."""
        if self.mode == "pat":
            return self.pat
        if self.mode == "app":
            with self._lock:
                if (
                    not self._installation_token
                    or time.time() > self._installation_token_expires_at - TOKEN_REFRESH_BUFFER
                ):
                    self._refresh_installation_token()
                return self._installation_token
        return None

    def _refresh_installation_token(self) -> None:
        """Mint a JWT, exchange for a fresh installation token, cache + log expiry."""
        import httpx
        import jwt

        now = int(time.time())
        payload = {
            "iat": now - 60,            # tolerate clock skew
            "exp": now + 9 * 60,        # JWTs valid up to 10 min; use 9
            "iss": self.app_id,         # str — pyjwt 2.x enforces RFC 7519
        }
        token_jwt = jwt.encode(payload, self.private_key_pem, algorithm="RS256")

        url = f"{API_BASE}/app/installations/{self.installation_id}/access_tokens"
        resp = httpx.post(
            url,
            headers={
                "Authorization": f"Bearer {token_jwt}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": USER_AGENT,
            },
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()
        self._installation_token = data["token"]
        # ISO8601 like "2026-01-15T10:30:00Z" → UNIX timestamp
        expires_str = data["expires_at"].replace("Z", "+00:00")
        self._installation_token_expires_at = datetime.fromisoformat(expires_str).timestamp()
        ttl = int(self._installation_token_expires_at - time.time())
        logger.info("GitHub App installation token refreshed, expires in %ds", ttl)


_auth_state: Optional[_AuthState] = None
_auth_state_lock = threading.Lock()


def _get_auth() -> _AuthState:
    global _auth_state
    if _auth_state is not None:
        return _auth_state
    with _auth_state_lock:
        if _auth_state is None:
            _auth_state = _AuthState()
    return _auth_state


# ---------------------------------------------------------------------------
# Server-wide token bucket for search calls
# ---------------------------------------------------------------------------


class _TokenBucket:
    def __init__(self, max_tokens: int, refill_per_sec: float) -> None:
        self.max_tokens = max_tokens
        self.refill_per_sec = refill_per_sec
        self.tokens = float(max_tokens)
        self.last_refill = time.monotonic()
        self.lock = threading.Lock()

    def take(self, n: int = 1) -> bool:
        with self.lock:
            now = time.monotonic()
            self.tokens = min(
                self.max_tokens, self.tokens + (now - self.last_refill) * self.refill_per_sec
            )
            self.last_refill = now
            if self.tokens >= n:
                self.tokens -= n
                return True
            return False


_search_budget = _TokenBucket(SEARCH_BUDGET_MAX, SEARCH_BUDGET_REFILL_PER_SEC)


# ---------------------------------------------------------------------------
# Lazy singleton HTTP client
# ---------------------------------------------------------------------------

_client_lock = threading.Lock()
_client: Optional[object] = None


def _get_client():
    """Return the shared httpx.Client, initializing on first call."""
    global _client
    if _client is not None:
        return _client
    with _client_lock:
        if _client is not None:
            return _client
        import httpx

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": USER_AGENT,
        }
        _client = httpx.Client(headers=headers, timeout=30.0, follow_redirects=True)
    return _client


def reset_client() -> None:
    """Force re-initialization on next call. Used in tests."""
    global _client, _auth_state
    with _client_lock:
        if _client is not None:
            _client.close()
        _client = None
    with _auth_state_lock:
        _auth_state = None
    with _cache_lock:
        _cache.clear()


# ---------------------------------------------------------------------------
# API helper: applies current auth + logs rate-limit headers
# ---------------------------------------------------------------------------


def _api_get(url: str, **kwargs):
    """GET against api.github.com with current auth + structured rate-limit logging."""
    client = _get_client()
    headers = dict(kwargs.pop("headers", {}))
    token = _get_auth().get_api_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = client.get(url, headers=headers, **kwargs)

    # Structured rate-limit observability — emit even on 4xx so dashboards see throttling.
    remaining = resp.headers.get("X-RateLimit-Remaining")
    if remaining is not None:
        logger.info(
            "github_api resource=%s remaining=%s/%s status=%d url=%s",
            resp.headers.get("X-RateLimit-Resource", "core"),
            remaining,
            resp.headers.get("X-RateLimit-Limit", "?"),
            resp.status_code,
            url,
        )
    return resp


# ---------------------------------------------------------------------------
# Caching helpers (unchanged)
# ---------------------------------------------------------------------------


def _cache_get(key: str) -> Any | None:
    with _cache_lock:
        entry = _cache.get(key)
        if entry is None:
            return None
        ts, val = entry
        if time.monotonic() - ts > CACHE_TTL_DEFAULT:
            del _cache[key]
            return None
        return val


def _cache_get_with_ttl(key: str, ttl: float) -> Any | None:
    with _cache_lock:
        entry = _cache.get(key)
        if entry is None:
            return None
        ts, val = entry
        if time.monotonic() - ts > ttl:
            del _cache[key]
            return None
        return val


def _cache_set(key: str, value: Any) -> None:
    with _cache_lock:
        if len(_cache) >= CACHE_MAX_ENTRIES:
            sorted_keys = sorted(_cache, key=lambda k: _cache[k][0])
            for k in sorted_keys[:100]:
                del _cache[k]
        _cache[key] = (time.monotonic(), value)


# ---------------------------------------------------------------------------
# Public fetch functions
# ---------------------------------------------------------------------------


def fetch_raw_file(path: str, repo: str = REPO_NAME) -> str:
    """Fetch raw file content from raw.githubusercontent.com.

    Public repos: no auth required, served via CDN, does NOT count against the
    GitHub API rate limit. The vast majority of MCP traffic flows through here.
    """
    cache_key = f"raw:{repo}:{path}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    url = f"{RAW_BASE}/{REPO_OWNER}/{repo}/{DEFAULT_BRANCH}/{path}"
    client = _get_client()
    resp = client.get(url)
    resp.raise_for_status()
    content = resp.text
    _cache_set(cache_key, content)
    return content


def fetch_contents(path: str, repo: str = REPO_NAME) -> list[dict] | dict:
    """Fetch directory listing or file metadata via GitHub Contents API."""
    cache_key = f"contents:{repo}:{path}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    url = f"{API_BASE}/repos/{REPO_OWNER}/{repo}/contents/{path}?ref={DEFAULT_BRANCH}"
    resp = _api_get(url)
    resp.raise_for_status()
    data = resp.json()

    if isinstance(data, list):
        result = [
            {
                "name": item["name"],
                "type": item["type"],
                "size": item.get("size", 0),
                "path": item["path"],
                "download_url": item.get("download_url"),
            }
            for item in data
        ]
    else:
        result = data

    _cache_set(cache_key, result)
    return result


def fetch_tree(repo: str = REPO_NAME) -> list[dict]:
    """Fetch the full recursive tree for a repo (single API call). Cached 10 min."""
    cache_key = f"tree:{repo}"
    cached = _cache_get_with_ttl(cache_key, CACHE_TTL_TREE)
    if cached is not None:
        return cached

    url = f"{API_BASE}/repos/{REPO_OWNER}/{repo}/git/trees/{DEFAULT_BRANCH}?recursive=1"
    resp = _api_get(url)
    resp.raise_for_status()
    tree = resp.json().get("tree", [])
    _cache_set(cache_key, tree)
    return tree


class SearchBudgetExceeded(RuntimeError):
    """Raised when the server-wide code-search budget is depleted.

    GitHub's search API enforces a hard 30/min cap; we stay under it with a
    server-wide token bucket. When depleted, callers should back off and try
    again shortly rather than have GitHub 403 us.
    """


def search_code(query: str, repo: str = REPO_NAME) -> list[dict]:
    """Search code in the repo using GitHub Code Search API.

    Requires auth (GH App or PAT). Returns at most 20 results. The result set
    is cached for 2 minutes per query. Calls beyond the server-wide budget of
    25/min raise SearchBudgetExceeded.
    """
    cache_key = f"search:{repo}:{query}"
    cached = _cache_get_with_ttl(cache_key, CACHE_TTL_SEARCH)
    if cached is not None:
        return cached

    if not _search_budget.take():
        raise SearchBudgetExceeded(
            "Server-wide code-search budget (25/min) depleted. Try again in a few seconds."
        )

    encoded_query = f"{query} repo:{REPO_OWNER}/{repo}"
    url = f"{API_BASE}/search/code"
    resp = _api_get(url, params={"q": encoded_query, "per_page": 20})
    resp.raise_for_status()
    items = resp.json().get("items", [])
    result = [
        {
            "name": item["name"],
            "path": item["path"],
            "html_url": item["html_url"],
            "repository": item["repository"]["full_name"],
        }
        for item in items
    ]
    _cache_set(cache_key, result)
    return result
