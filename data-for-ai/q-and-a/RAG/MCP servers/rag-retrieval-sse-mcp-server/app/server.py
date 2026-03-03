"""
Streamable HTTP MCP Server (FastMCP) - Retrieval Only
Supports querying either OpenSearch or Milvus based on environment variables.

- ENV-only configuration (load_dotenv)
- Tool: get_retrieval_configuration (secrets masked)
- Tool: retrieve (semantic / hybrid depending on backend)
- Tool: keyword_search (OpenSearch only)
- Bootstrap connection check at startup with error details
"""

from __future__ import annotations

import os
import platform
import socket
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# Vector DBs
from opensearchpy import OpenSearch

from pymilvus import connections, Collection, utility

# Embeddings (Watsonx like your ingestion server)
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Embeddings

# Load .env early
load_dotenv()

# =============================================================================
# Base server settings (same pattern as ingestion server)
# =============================================================================

SERVER_NAME = os.getenv("SERVER_NAME", "rag-retrieval-mcp")
SERVER_VERSION = os.getenv("SERVER_VERSION", "1.0.0")
SERVER_DESCRIPTION = os.getenv(
    "SERVER_DESCRIPTION",
    "Retrieval MCP Server for querying RAG indexes (OpenSearch or Milvus)",
)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

APP_BEARER_TOKEN: Optional[str] = os.getenv("APP_BEARER_TOKEN", "").strip() or None
PUBLIC_BASE_URL: Optional[str] = os.getenv("PUBLIC_BASE_URL", "").strip() or None
ALLOWED_HOSTS_ENV: str = os.getenv("ALLOWED_HOSTS", "").strip()
ALLOWED_ORIGINS_ENV: str = os.getenv("ALLOWED_ORIGINS", "").strip()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_server_info() -> Dict[str, Any]:
    return {
        "hostname": socket.gethostname(),
        "server_time": utc_now_iso(),
        "timezone": "UTC",
        "server_name": SERVER_NAME,
        "server_version": SERVER_VERSION,
        "description": SERVER_DESCRIPTION,
        "environment": ENVIRONMENT,
        "platform": platform.system(),
        "platform_release": platform.release(),
        "python_version": platform.python_version(),
    }


def _split_csv(value: str) -> List[str]:
    return [p.strip() for p in value.split(",") if p.strip()]


def _host_from_public_url(public_url: str) -> Optional[str]:
    try:
        parsed = urlparse(public_url)
        return parsed.hostname
    except Exception:
        return None


def build_transport_security() -> TransportSecuritySettings:
    allowed_hosts: List[str] = ["localhost:*", "127.0.0.1:*"]

    if PUBLIC_BASE_URL:
        host = _host_from_public_url(PUBLIC_BASE_URL)
        if host:
            allowed_hosts.append(f"{host}:*")

    if ALLOWED_HOSTS_ENV:
        allowed_hosts = _split_csv(ALLOWED_HOSTS_ENV)

    allowed_origins: List[str] = ["http://localhost:*", "http://127.0.0.1:*"]
    if PUBLIC_BASE_URL:
        parsed = urlparse(PUBLIC_BASE_URL)
        if parsed.scheme and parsed.hostname:
            allowed_origins.append(f"{parsed.scheme}://{parsed.hostname}:*")

    if ALLOWED_ORIGINS_ENV:
        allowed_origins = _split_csv(ALLOWED_ORIGINS_ENV)

    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
    )


class OptionalBearerAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, token: Optional[str]) -> None:
        super().__init__(app)
        self._token = token

    async def dispatch(self, request: Request, call_next):
        if not self._token:
            return await call_next(request)

        path = request.url.path
        protected = (path == "/") or (path == "/health") or path.startswith("/mcp")
        if protected:
            auth = request.headers.get("authorization", "")
            expected = f"Bearer {self._token}"
            if auth != expected:
                return JSONResponse(
                    status_code=401,
                    content={
                        "error": "Unauthorized",
                        "message": "Missing or invalid Authorization header",
                    },
                )

        return await call_next(request)


# =============================================================================
# ENV-only config
# =============================================================================

@dataclass
class EmbeddingConfig:
    watsonx_url: str = ""
    watsonx_api_key: str = ""
    project_id: str = ""
    embedding_model_id: str = ""

    def is_configured(self) -> bool:
        return bool(self.watsonx_url and self.watsonx_api_key and self.project_id and self.embedding_model_id)


@dataclass
class VectorDbConfig:
    db_type: str = ""  # opensearch | milvus

    # OpenSearch
    opensearch_host: str = ""
    opensearch_port: int = 9200
    opensearch_username: str = ""
    opensearch_password: str = ""
    opensearch_index: str = "rag-index"
    opensearch_use_ssl: bool = True

    # Milvus
    milvus_host: str = ""
    milvus_port: int = 19530
    milvus_user: str = ""
    milvus_password: str = ""
    milvus_secure: bool = False
    milvus_collection: str = "rag_collection"
    # if your ingestion created hybrid schema, you can still do dense-only search here
    milvus_dense_field: str = "vector"  # or "dense" if hybrid mode
    milvus_text_field: str = "text"

    def is_configured(self) -> bool:
        if self.db_type == "opensearch":
            return bool(self.opensearch_host and self.opensearch_index)
        if self.db_type == "milvus":
            return bool(self.milvus_host and self.milvus_collection)
        return False


def _env_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key, "").strip().lower()
    if not val:
        return default
    return val in ("1", "true", "yes", "y", "on")


def load_embedding_config() -> EmbeddingConfig:
    return EmbeddingConfig(
        watsonx_url=os.getenv("WATSONX_URL", "").strip(),
        watsonx_api_key=os.getenv("WATSONX_API_KEY", "").strip(),
        project_id=os.getenv("WATSONX_PROJECT_ID", "").strip(),
        embedding_model_id=os.getenv("EMBEDDING_MODEL_ID", "").strip(),
    )


def load_vector_db_config() -> VectorDbConfig:
    return VectorDbConfig(
        db_type=os.getenv("VECTOR_DB_TYPE", "").strip().lower(),

        opensearch_host=os.getenv("OPENSEARCH_HOST", "").strip(),
        opensearch_port=int(os.getenv("OPENSEARCH_PORT", "9200")),
        opensearch_username=os.getenv("OPENSEARCH_USERNAME", "").strip(),
        opensearch_password=os.getenv("OPENSEARCH_PASSWORD", "").strip(),
        opensearch_index=os.getenv("OPENSEARCH_INDEX", "rag-index").strip(),
        opensearch_use_ssl=_env_bool("OPENSEARCH_USE_SSL", True),

        milvus_host=os.getenv("MILVUS_HOST", "").strip(),
        milvus_port=int(os.getenv("MILVUS_PORT", "19530")),
        milvus_user=os.getenv("MILVUS_USER", "").strip(),
        milvus_password=os.getenv("MILVUS_PASSWORD", "").strip(),
        milvus_secure=_env_bool("MILVUS_SECURE", False),
        milvus_collection=os.getenv("MILVUS_COLLECTION", "rag_collection").strip(),
        milvus_dense_field=os.getenv("MILVUS_DENSE_FIELD", "vector").strip(),
        milvus_text_field=os.getenv("MILVUS_TEXT_FIELD", "text").strip(),
    )


# =============================================================================
# Masking helpers
# =============================================================================

def _mask_secret(val: str, show_start: int = 0, show_end: int = 0) -> str:
    if not val:
        return ""
    if show_start + show_end >= len(val):
        return "*" * len(val)
    return f"{val[:show_start]}{'*' * (len(val) - show_start - show_end)}{val[-show_end:]}"


def _mask_username(val: str) -> str:
    if not val:
        return ""
    if len(val) <= 4:
        return _mask_secret(val, show_start=1, show_end=1)
    return _mask_secret(val, show_start=2, show_end=2)


# =============================================================================
# Clients
# =============================================================================

def get_embedding(embed_cfg: EmbeddingConfig) -> Embeddings:
    credentials = Credentials(api_key=embed_cfg.watsonx_api_key, url=embed_cfg.watsonx_url)
    return Embeddings(
        model_id=embed_cfg.embedding_model_id,
        credentials=credentials,
        project_id=embed_cfg.project_id,
        verify=True,
    )


def _normalize_opensearch_host_port(vdb: VectorDbConfig) -> Tuple[str, int, bool]:
    """
    Allows OPENSEARCH_HOST to be either hostname or full URL.
    Returns (host, port, use_ssl)
    """
    host = vdb.opensearch_host.strip()
    port = vdb.opensearch_port
    use_ssl = vdb.opensearch_use_ssl

    if host.startswith("http://") or host.startswith("https://"):
        parsed = urlparse(host)
        if parsed.hostname:
            host = parsed.hostname
        if parsed.port:
            port = parsed.port
        if parsed.scheme == "http":
            use_ssl = False
        elif parsed.scheme == "https":
            use_ssl = True

    return host, port, use_ssl


def _opensearch_client(vdb: VectorDbConfig) -> OpenSearch:
    host, port, use_ssl = _normalize_opensearch_host_port(vdb)

    http_auth = None
    if vdb.opensearch_username or vdb.opensearch_password:
        http_auth = (vdb.opensearch_username, vdb.opensearch_password)

    return OpenSearch(
        hosts=[{"host": host, "port": port}],
        http_auth=http_auth,
        use_ssl=use_ssl,
        verify_certs=use_ssl,
    )


def _milvus_connect(vdb: VectorDbConfig) -> None:
    kwargs: Dict[str, Any] = {
        "host": vdb.milvus_host,
        "port": str(vdb.milvus_port),
        "secure": vdb.milvus_secure,
    }
    if vdb.milvus_user:
        kwargs["user"] = vdb.milvus_user
    if vdb.milvus_password:
        kwargs["password"] = vdb.milvus_password
    connections.connect(alias="default", **kwargs)


# =============================================================================
# Bootstrap connectivity checks (print actual exception)
# =============================================================================

def _print_bootstrap_status(name: str, ok: bool, detail: str = "") -> None:
    status = "OK" if ok else "FAIL"
    msg = f"[BOOTSTRAP] {name}: {status}"
    if detail:
        msg += f" - {detail}"
    print(msg, flush=True)


def bootstrap_check_connections() -> None:
    # Embedding config check (don’t call the service unless configured)
    try:
        emb_cfg = load_embedding_config()
        if not emb_cfg.is_configured():
            _print_bootstrap_status("WATSONX_EMBEDDINGS", False, "Not configured (WATSONX_* / EMBEDDING_MODEL_ID)")
        else:
            # Light sanity call to catch auth issues early
            emb = get_embedding(emb_cfg)
            _ = emb.embed_query("ping")
            _print_bootstrap_status("WATSONX_EMBEDDINGS", True, f"model={emb_cfg.embedding_model_id}")
    except Exception as e:
        _print_bootstrap_status("WATSONX_EMBEDDINGS", False, f"{type(e).__name__}: {e}")

    # Vector DB check
    try:
        vdb = load_vector_db_config()
        if not vdb.is_configured():
            _print_bootstrap_status("VECTOR_DB", False, "Not configured (VECTOR_DB_TYPE + backend vars)")
            return

        if vdb.db_type == "opensearch":
            try:
                os_client = _opensearch_client(vdb)
                ok = bool(os_client.ping())
                host, port, use_ssl = _normalize_opensearch_host_port(vdb)
                _print_bootstrap_status("OPENSEARCH", ok, f"{host}:{port} ssl={use_ssl}")
            except Exception as e:
                _print_bootstrap_status("OPENSEARCH", False, f"{type(e).__name__}: {e}")

        elif vdb.db_type == "milvus":
            try:
                _milvus_connect(vdb)
                ver = utility.get_server_version()
                _print_bootstrap_status("MILVUS", True, f"server_version={ver} collection={vdb.milvus_collection}")
            except Exception as e:
                _print_bootstrap_status("MILVUS", False, f"{type(e).__name__}: {e}")

        else:
            _print_bootstrap_status("VECTOR_DB", False, f"Unknown VECTOR_DB_TYPE={vdb.db_type}")

    except Exception as e:
        _print_bootstrap_status("VECTOR_DB", False, f"{type(e).__name__}: {e}")


bootstrap_check_connections()

# =============================================================================
# Retrieval implementations
# =============================================================================

def _opensearch_semantic_query(vector: List[float], k: int) -> Dict[str, Any]:
    # Requires "content_vector" knn_vector mapping (same as ingestion server)
    return {
        "size": k,
        "query": {
            "knn": {
                "content_vector": {
                    "vector": vector,
                    "k": k,
                }
            }
        },
        "_source": {
            "includes": ["id", "title", "source", "page_number", "chunk_seq", "text", "document_url", "content"]
        },
    }


def _opensearch_keyword_query(query: str, k: int) -> Dict[str, Any]:
    return {
        "size": k,
        "query": {"match": {"content": {"query": query}}},
        "_source": {
            "includes": ["id", "title", "source", "page_number", "chunk_seq", "text", "document_url", "content"]
        },
    }


def _format_hits(hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for h in hits:
        src = h.get("_source", {}) or {}
        out.append(
            {
                "id": h.get("_id") or src.get("id"),
                "score": h.get("_score"),
                "title": src.get("title", ""),
                "source": src.get("source", ""),
                "page_number": src.get("page_number", ""),
                "chunk_seq": src.get("chunk_seq", ""),
                "document_url": src.get("document_url", ""),
                "text": src.get("text") or src.get("content") or "",
            }
        )
    return out


# =============================================================================
# MCP server + tools
# =============================================================================

transport_security = build_transport_security()

mcp = FastMCP(
    name=SERVER_NAME,
    stateless_http=True,
    transport_security=transport_security,
)


@mcp.tool(description="Get information about the server including hostname, time, environment, and platform")
def get_server_info() -> Dict[str, Any]:
    return build_server_info()


@mcp.tool(description="Get the current server time in UTC timezone")
def get_server_time() -> Dict[str, str]:
    return {"server_time": utc_now_iso(), "timezone": "UTC"}


@mcp.tool(description="Get the server hostname")
def get_hostname() -> Dict[str, str]:
    return {"hostname": socket.gethostname()}


@mcp.tool(description="Get current retrieval configuration from ENV only (secrets masked).")
def get_retrieval_configuration() -> Dict[str, Any]:
    emb = load_embedding_config()
    vdb = load_vector_db_config()
    host, port, use_ssl = _normalize_opensearch_host_port(vdb)

    return {
        "embedding": {
            "configured": emb.is_configured(),
            "watsonx_url": emb.watsonx_url,
            "project_id": emb.project_id,
            "embedding_model_id": emb.embedding_model_id,
            "watsonx_api_key": _mask_secret(emb.watsonx_api_key, show_start=2, show_end=2) if emb.watsonx_api_key else "",
        },
        "vector_db": {
            "configured": vdb.is_configured(),
            "db_type": vdb.db_type,
            "opensearch": {
                "host": host,
                "port": port,
                "use_ssl": use_ssl,
                "index": vdb.opensearch_index,
                "username": _mask_username(vdb.opensearch_username),
                "password_set": bool(vdb.opensearch_password),
            },
            "milvus": {
                "host": vdb.milvus_host,
                "port": vdb.milvus_port,
                "secure": vdb.milvus_secure,
                "collection": vdb.milvus_collection,
                "dense_field": vdb.milvus_dense_field,
                "text_field": vdb.milvus_text_field,
                "username": _mask_username(vdb.milvus_user),
                "password_set": bool(vdb.milvus_password),
            },
        },
    }


@mcp.tool(description="Semantic retrieval. Uses Watsonx embeddings. Works with OpenSearch (knn) or Milvus (vector search).")
async def retrieve(
    query: str,
    k: int = 5,
    destination_index: str = "",  # override env OPENSEARCH_INDEX / MILVUS_COLLECTION
) -> Dict[str, Any]:
    if not query or not query.strip():
        raise ValueError("query must be a non-empty string")

    emb_cfg = load_embedding_config()
    vdb = load_vector_db_config()

    if not emb_cfg.is_configured():
        raise ValueError("Embedding config missing. Set WATSONX_URL, WATSONX_API_KEY, WATSONX_PROJECT_ID, EMBEDDING_MODEL_ID.")
    if not vdb.is_configured():
        raise ValueError("Vector DB config missing. Set VECTOR_DB_TYPE and backend vars.")

    dest = (destination_index or "").strip()
    if vdb.db_type == "opensearch":
        index_name = dest or vdb.opensearch_index
    else:
        index_name = dest or vdb.milvus_collection

    embedding = get_embedding(emb_cfg)
    vector = embedding.embed_query(query)

    if vdb.db_type == "opensearch":
        os_client = _opensearch_client(vdb)
        body = _opensearch_semantic_query(vector=vector, k=k)
        resp = os_client.search(index=index_name, body=body)
        hits = (resp.get("hits", {}) or {}).get("hits", []) or []
        return {
            "backend": "opensearch",
            "index": index_name,
            "k": k,
            "results": _format_hits(hits),
        }

    if vdb.db_type == "milvus":
        _milvus_connect(vdb)
        coll = Collection(name=index_name)
        coll.load()

        # Milvus search
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        res = coll.search(
            data=[vector],
            anns_field=vdb.milvus_dense_field,
            param=search_params,
            limit=k,
            output_fields=["id", "title", "source", "page_number", "chunk_seq", "document_url", vdb.milvus_text_field],
        )

        # Flatten results
        out: List[Dict[str, Any]] = []
        for hits in res:
            for h in hits:
                ent = h.entity
                out.append(
                    {
                        "id": ent.get("id"),
                        "score": float(h.distance),
                        "title": ent.get("title", ""),
                        "source": ent.get("source", ""),
                        "page_number": ent.get("page_number", ""),
                        "chunk_seq": ent.get("chunk_seq", ""),
                        "document_url": ent.get("document_url", ""),
                        "text": ent.get(vdb.milvus_text_field, "") or "",
                    }
                )

        return {
            "backend": "milvus",
            "collection": index_name,
            "k": k,
            "results": out,
        }

    raise ValueError(f"Unsupported VECTOR_DB_TYPE={vdb.db_type}")


@mcp.tool(description="Keyword search (OpenSearch only).")
def keyword_search(
    query: str,
    k: int = 5,
    destination_index: str = "",
) -> Dict[str, Any]:
    if not query or not query.strip():
        raise ValueError("query must be a non-empty string")

    vdb = load_vector_db_config()
    if vdb.db_type != "opensearch":
        raise ValueError("keyword_search is only supported when VECTOR_DB_TYPE=opensearch")

    index_name = (destination_index or "").strip() or vdb.opensearch_index
    os_client = _opensearch_client(vdb)

    body = _opensearch_keyword_query(query=query, k=k)
    resp = os_client.search(index=index_name, body=body)
    hits = (resp.get("hits", {}) or {}).get("hits", []) or []
    return {
        "backend": "opensearch",
        "index": index_name,
        "k": k,
        "results": _format_hits(hits),
    }


# Streamable HTTP ASGI app (provides /mcp)
app = mcp.streamable_http_app()
app.add_middleware(OptionalBearerAuthMiddleware, token=APP_BEARER_TOKEN)


# Extra endpoints (non-MCP)
async def health(_: Request) -> Response:
    return JSONResponse(
        {
            "status": "healthy",
            "server": SERVER_NAME,
            "version": SERVER_VERSION,
            "description": SERVER_DESCRIPTION,
            "timestamp": utc_now_iso(),
        }
    )


async def index(_: Request) -> Response:
    return JSONResponse(
        {
            "server": SERVER_NAME,
            "version": SERVER_VERSION,
            "description": SERVER_DESCRIPTION,
            "environment": ENVIRONMENT,
            "public_base_url": PUBLIC_BASE_URL,
            "endpoints": {"health": "/health", "mcp": "/mcp"},
            "auth": {"enabled": bool(APP_BEARER_TOKEN)},
            "transport_security": {
                "dns_rebinding_protection": True,
                "allowed_hosts": transport_security.allowed_hosts,
                "allowed_origins": transport_security.allowed_origins,
            },
            "tools": [
                "get_server_info",
                "get_server_time",
                "get_hostname",
                "get_retrieval_configuration",
                "retrieve",
                "keyword_search",
            ],
        }
    )


app.add_route("/", index, methods=["GET"])
app.add_route("/health", health, methods=["GET"])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
