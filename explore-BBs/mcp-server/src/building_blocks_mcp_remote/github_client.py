"""
Lazy singleton HTTP client for GitHub API access with TTL caching.

The client is constructed on first access, not at import time.

Environment variables
---------------------
GITHUB_TOKEN : GitHub personal access token (optional but recommended)
               Without a token: 60 requests/hr.  With a token: 5,000 req/hr.
               Required for code search.

Usage
-----
    from building_blocks_mcp_remote.github_client import fetch_raw_file, fetch_contents
    content = fetch_raw_file("agents/agent-builder/README.md")
    items   = fetch_contents("agents/agent-builder")
"""

from __future__ import annotations

import logging
import os
import threading
import time
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

# ---------------------------------------------------------------------------
# Cache settings
# ---------------------------------------------------------------------------

CACHE_TTL_DEFAULT = 300   # 5 minutes
CACHE_TTL_TREE = 600      # 10 minutes
CACHE_MAX_ENTRIES = 500

_cache: dict[str, tuple[float, Any]] = {}
_cache_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Lazy singleton client
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
            "User-Agent": "building-blocks-mcp-remote/0.1.0",
        }
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
            logger.info("GitHub client initialized with authentication")
        else:
            logger.warning(
                "GITHUB_TOKEN not set — rate limit is 60 req/hr. "
                "Set GITHUB_TOKEN for 5,000 req/hr and code search."
            )
        _client = httpx.Client(
            headers=headers,
            timeout=30.0,
            follow_redirects=True,
        )
    return _client


def reset_client() -> None:
    """Force re-initialization on next call. Used in tests."""
    global _client
    with _client_lock:
        if _client is not None:
            _client.close()
        _client = None
    with _cache_lock:
        _cache.clear()


# ---------------------------------------------------------------------------
# Caching helpers
# ---------------------------------------------------------------------------

def _cache_get(key: str) -> Any | None:
    """Return cached value if present and not expired, else None."""
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
    """Return cached value if present and within custom TTL."""
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
    """Store a value in cache, evicting oldest entries if at capacity."""
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
    """Fetch raw file content from raw.githubusercontent.com (CDN, no rate limit)."""
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
    client = _get_client()
    resp = client.get(url)
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
    client = _get_client()
    resp = client.get(url)
    resp.raise_for_status()
    tree = resp.json().get("tree", [])
    _cache_set(cache_key, tree)
    return tree


def search_code(query: str, repo: str = REPO_NAME) -> list[dict]:
    """Search code in the repo using GitHub Code Search API. Requires GITHUB_TOKEN."""
    cache_key = f"search:{repo}:{query}"
    cached = _cache_get_with_ttl(cache_key, 120)
    if cached is not None:
        return cached

    encoded_query = f"{query} repo:{REPO_OWNER}/{repo}"
    url = f"{API_BASE}/search/code"
    client = _get_client()
    resp = client.get(url, params={"q": encoded_query, "per_page": 20})
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
