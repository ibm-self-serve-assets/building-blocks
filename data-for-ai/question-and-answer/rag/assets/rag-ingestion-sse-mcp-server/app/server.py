"""
Streamable HTTP MCP Server (FastMCP) + RAG ingestion from IBM Cloud Object Storage (COS)
into vector databases (OpenSearch or Milvus).

ENV only configuration:
- No runtime config tools.
- Tool to view current config with secrets masked.
- ingest_from_cos supports per-call bucket and destination index/collection.

Bootstrap:
- Loads .env via load_dotenv()
- Checks connections on startup and prints status.
"""

from __future__ import annotations

import os
import platform
import socket
import json
import hashlib
import logging
import tarfile
import tempfile
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from dotenv import load_dotenv

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# --- Notebook libraries (imports aligned with modern LangChain layout) ---
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredPowerPointLoader,
    UnstructuredFileLoader,
    BSHTMLLoader,
    TextLoader,
)
from langchain_core.documents import Document
from bs4 import BeautifulSoup
from langchain_core.documents import Document

# IBM COS SDK: prefer bundled ibm_boto3 if available; otherwise import from ibm_cos_sdk namespace.
try:
    import ibm_boto3  # type: ignore
    from ibm_botocore.client import Config  # type: ignore
except Exception:
    from ibm_cos_sdk import ibm_boto3  # type: ignore
    from ibm_cos_sdk.ibm_botocore.client import Config  # type: ignore

# Vector DB clients
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk as os_bulk

from pymilvus.bulk_writer import RemoteBulkWriter, BulkFileType
from pymilvus import (
    connections,
    FieldSchema,
    DataType,
    Collection,
    CollectionSchema,
    utility,
    Function,
    FunctionType,
)

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Embeddings


# =============================================================================
# Load .env early
# =============================================================================
load_dotenv()


# =============================================================================
# Logging
# =============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").strip().upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("rag_ingestion_server")


# =============================================================================
# Base server settings (from your original server.py)
# =============================================================================

SERVER_NAME = os.getenv("SERVER_NAME", "base-mcp-server")
SERVER_VERSION = os.getenv("SERVER_VERSION", "1.0.0")
SERVER_DESCRIPTION = os.getenv(
    "SERVER_DESCRIPTION",
    "Base MCP Server for Data for AI Building Block (with RAG ingestion)",
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
# Ingestion configuration (ENV ONLY)
# =============================================================================

SUPPORTED_FILE_TYPES = ["tar", "pdf", "pptx", "docx", "md", "txt", "html"]


@dataclass
class CosConfig:
    endpoint: str = ""
    api_key: str = ""
    instance_crn: str = ""
    bucket: str = ""
    prefix: str = ""

    def is_configured(self) -> bool:
        return bool(self.endpoint and self.api_key and self.instance_crn and self.bucket)


@dataclass
class EmbeddingConfig:
    watsonx_url: str = ""
    watsonx_api_key: str = ""
    project_id: str = ""
    embedding_model_id: str = ""

    def is_configured(self) -> bool:
        return bool(self.watsonx_url and self.watsonx_api_key and self.project_id and self.embedding_model_id)


@dataclass
class ChunkingConfig:
    chunk_size: int = 1000
    chunk_overlap: int = 200
    include_all_html_tags: bool = False


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
    milvus_hybrid_search: bool = False
    milvus_use_bulk_ingestion: bool = False

    # Milvus bulk-writer remote path (COS/S3)
    bulk_remote_path: str = ""
    bulk_cos_endpoint: str = ""
    bulk_cos_access_key: str = ""
    bulk_cos_secret_key: str = ""
    bulk_cos_bucket: str = ""
    bulk_cos_region: str = ""
    bulk_cos_is_ibm: bool = True

    def is_configured(self) -> bool:
        if self.db_type == "opensearch":
            return bool(self.opensearch_host and (self.opensearch_index))
        if self.db_type == "milvus":
            return bool(self.milvus_host and (self.milvus_collection))
        return False


def _env_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key, "").strip().lower()
    if not val:
        return default
    return val in ("1", "true", "yes", "y", "on")


def load_cos_config() -> CosConfig:
    return CosConfig(
        endpoint=os.getenv("COS_ENDPOINT", "").strip(),
        api_key=os.getenv("COS_API_KEY", "").strip(),
        instance_crn=os.getenv("COS_INSTANCE_CRN", "").strip(),
        bucket=os.getenv("COS_BUCKET", "").strip(),
        prefix=os.getenv("COS_PREFIX", "").strip(),
    )


def load_embedding_config() -> EmbeddingConfig:
    return EmbeddingConfig(
        watsonx_url=os.getenv("WATSONX_URL", "").strip(),
        watsonx_api_key=os.getenv("WATSONX_API_KEY", "").strip(),
        project_id=os.getenv("WATSONX_PROJECT_ID", "").strip(),
        embedding_model_id=os.getenv("EMBEDDING_MODEL_ID", "").strip(),
    )


def load_chunking_config() -> ChunkingConfig:
    return ChunkingConfig(
        chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
        include_all_html_tags=_env_bool("INCLUDE_ALL_HTML_TAGS", False),
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
        milvus_hybrid_search=_env_bool("MILVUS_HYBRID_SEARCH", False),
        milvus_use_bulk_ingestion=_env_bool("MILVUS_USE_BULK_INGESTION", False),

        bulk_remote_path=os.getenv("MILVUS_BULK_REMOTE_PATH", "").strip(),
        bulk_cos_endpoint=os.getenv("MILVUS_BULK_COS_ENDPOINT", "").strip(),
        bulk_cos_access_key=os.getenv("MILVUS_BULK_COS_ACCESS_KEY", "").strip(),
        bulk_cos_secret_key=os.getenv("MILVUS_BULK_COS_SECRET_KEY", "").strip(),
        bulk_cos_bucket=os.getenv("MILVUS_BULK_COS_BUCKET", "").strip(),
        bulk_cos_region=os.getenv("MILVUS_BULK_COS_REGION", "").strip(),
        bulk_cos_is_ibm=_env_bool("MILVUS_BULK_COS_IS_IBM", True),
    )


# =============================================================================
# Masking configuration in tool output
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
# Notebook ingestion logic (ported)
# =============================================================================

def _cos_client_from_config(cfg: CosConfig):
    endpoint = cfg.endpoint if cfg.endpoint.startswith("https://") else ("https://" + cfg.endpoint)
    logger.info("Initializing COS client for endpoint=%s bucket=%s", endpoint, cfg.bucket)
    return ibm_boto3.client(
        "s3",
        ibm_api_key_id=cfg.api_key,
        ibm_service_instance_id=cfg.instance_crn,
        config=Config(signature_version="oauth"),
        endpoint_url=endpoint,
    )


def get_cos_objects(cos_client, bucket_name: str, prefix: str) -> List[str]:
    logger.info("Listing COS objects from bucket=%s prefix=%s", bucket_name, prefix or "<root>")
    objects: List[str] = []
    paginator = cos_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix or ""):
        if "Contents" in page:
            for obj in page["Contents"]:
                objects.append(obj["Key"])
    logger.info("Listed %d COS objects from bucket=%s prefix=%s", len(objects), bucket_name, prefix or "<root>")
    return objects


def get_split_documents(documents: List[Document], chunk_cfg: ChunkingConfig) -> List[Document]:
    content: List[str] = []
    metadata: List[Dict[str, Any]] = []

    for doc in documents:
        title = doc.metadata.get("title") or doc.metadata.get("source", "").split("/")[-1].split(".")[0]
        metadata.append(
            {
                "title": title,
                "source": doc.metadata.get("source", ""),
                "document_url": "",
                "page_number": str(doc.metadata.get("page", "")) if "page" in doc.metadata else "",
            }
        )
        content.append(doc.page_content)

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_cfg.chunk_size,
        chunk_overlap=chunk_cfg.chunk_overlap,
        disallowed_special=(),
    )

    split_documents = text_splitter.create_documents(content, metadatas=metadata)

    chunk_id = 0
    chunk_source = ""
    for chunk in split_documents:
        chunk.metadata["title"] = chunk.metadata.get("title", "Unknown Title")
        chunk.page_content = f"Document Title: {chunk.metadata['title']}\n Document Content: {chunk.page_content}"
        if chunk_source == "" or chunk_source != chunk.metadata.get("source", ""):
            chunk_id = 1
            chunk_source = chunk.metadata.get("source", "")
        chunk.metadata["chunk_seq"] = chunk_id
        chunk_id += 1

    logger.info("Created %d split documents", len(split_documents))
    return split_documents


def process_file(file: Tuple[str, bytes], chunk_cfg: ChunkingConfig) -> Tuple[str, List[Document]]:
    file_name, file_content = file
    file_type = file_name.split(".")[-1].lower()
    logger.info("Processing file name=%s type=%s size_bytes=%d", file_name, file_type, len(file_content))

    with tempfile.NamedTemporaryFile(suffix=f".{file_type}", delete=True) as temp_file:
        temp_file.write(file_content)
        temp_file.flush()

        if file_type == "pdf":
            loader = PyPDFLoader(temp_file.name)
        elif file_type == "docx":
            loader = Docx2txtLoader(temp_file.name)
        elif file_type in ["md", "txt"]:
            # Read text files directly to avoid UnstructuredFileLoader hanging issues
            try:
                text_content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                # Fallback to latin-1 if utf-8 fails
                text_content = file_content.decode('latin-1', errors='ignore')
            
            # Create a Document directly instead of using a loader
            documents = [Document(page_content=text_content, metadata={"source": file_name})]
            logger.info("Loaded 1 raw document for file=%s (direct text read)", file_name)
            split_docs = get_split_documents(documents, chunk_cfg)
            logger.info("Finished processing file=%s chunks=%d", file_name, len(split_docs))
            return file_name, split_docs
        elif file_type == "pptx":
            loader = UnstructuredPowerPointLoader(temp_file.name, mode="elements")
        elif file_type == "html":
            class StructuredHTMLLoader(BSHTMLLoader):
                def load(self) -> List[Document]:
                    encoding: Optional[str] = getattr(self, "encoding", None) or "utf-8"
                    with open(self.file_path, mode="r", encoding=encoding, errors="ignore") as f:
                        soup = BeautifulSoup(f, "html.parser")
                        texts = soup.find_all(string=True)
                        visible_texts: List[str] = []
                        for t in texts:
                            s = str(t).strip()
                            if s:
                                visible_texts.append(s)
                        full_text = "\n".join(visible_texts)
                    return [Document(page_content=full_text, metadata={"source": self.file_path})]

            loader = BSHTMLLoader(temp_file.name) if not chunk_cfg.include_all_html_tags else StructuredHTMLLoader(temp_file.name)
        else:
            logger.warning("Skipping unsupported file type for file=%s type=%s", file_name, file_type)
            return file_name, []

        logger.info("Loading parsed documents for file=%s using loader=%s", file_name, loader.__class__.__name__)
        documents = loader.load()
        logger.info("Loaded %d raw documents for file=%s", len(documents), file_name)
        split_docs = get_split_documents(documents, chunk_cfg)
        logger.info("Finished processing file=%s chunks=%d", file_name, len(split_docs))
        return file_name, split_docs


def process_cos_file(cos_client, bucket_name: str, file_key: str) -> Dict[str, bytes]:
    logger.info("Fetching COS object bucket=%s key=%s", bucket_name, file_key)
    map_file_content: Dict[str, bytes] = {}

    response = cos_client.get_object(Bucket=bucket_name, Key=file_key)
    file_body = response["Body"].read()
    file_type = file_key.split(".")[-1].lower()

    logger.info("Fetched COS object key=%s size_bytes=%d type=%s", file_key, len(file_body), file_type)
    if file_type == "tar":
        tar_bytes = BytesIO(file_body)
        if tar_bytes.getbuffer().nbytes > 1:
            with tarfile.open(fileobj=tar_bytes, mode="r:") as tar:
                for member in tar.getmembers():
                    if member.isfile() and member.name.endswith(tuple(SUPPORTED_FILE_TYPES[1:])):
                        extracted = tar.extractfile(member)
                        if extracted:
                            map_file_content[member.name] = extracted.read()
    elif file_type in SUPPORTED_FILE_TYPES[1:]:
        map_file_content[file_key] = file_body

    logger.info("Expanded COS object key=%s into %d ingestible file(s)", file_key, len(map_file_content))
    return map_file_content


def generate_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8", errors="ignore")).hexdigest()


def get_embedding(embed_cfg: EmbeddingConfig) -> Embeddings:
    logger.info(
        "Initializing embeddings client url=%s project_id=%s model_id=%s",
        embed_cfg.watsonx_url,
        embed_cfg.project_id,
        embed_cfg.embedding_model_id,
    )
    credentials = Credentials(api_key=embed_cfg.watsonx_api_key, url=embed_cfg.watsonx_url)
    return Embeddings(
        model_id=embed_cfg.embedding_model_id,
        credentials=credentials,
        project_id=embed_cfg.project_id,
        verify=True,
    )


def _opensearch_client(vdb: VectorDbConfig) -> OpenSearch:
    logger.info(
        "Initializing OpenSearch client host=%s port=%s use_ssl=%s index=%s",
        vdb.opensearch_host,
        vdb.opensearch_port,
        vdb.opensearch_use_ssl,
        vdb.opensearch_index,
    )
    http_auth = None
    if vdb.opensearch_username or vdb.opensearch_password:
        http_auth = (vdb.opensearch_username, vdb.opensearch_password)

    return OpenSearch(
        hosts=[{"host": vdb.opensearch_host, "port": vdb.opensearch_port}],
        http_auth=http_auth,
        use_ssl=vdb.opensearch_use_ssl,
        verify_certs=vdb.opensearch_use_ssl,
    )


def _ensure_opensearch_index(os_client: OpenSearch, index_name: str, embedding_dim: int) -> None:
    logger.info("Ensuring OpenSearch index exists index=%s embedding_dim=%d", index_name, embedding_dim)
    if os_client.indices.exists(index=index_name):
        logger.info("OpenSearch index already exists index=%s", index_name)
        return

    mapping = {
        "settings": {"index": {"mapping.total_fields.limit": 1000000, "number_of_shards": 1}},
        "mappings": {
            "properties": {
                "content": {"type": "text"},
                "content_vector": {"type": "knn_vector", "dimension": embedding_dim},
                "title": {"type": "keyword"},
                "source": {"type": "keyword"},
                "document_url": {"type": "keyword"},
                "page_number": {"type": "keyword"},
                "chunk_seq": {"type": "integer"},
                "text": {"type": "text"},
            }
        },
    }
    os_client.indices.create(index=index_name, body=mapping)
    logger.info("Created OpenSearch index index=%s", index_name)


def _milvus_connect(vdb: VectorDbConfig) -> None:
    logger.info(
        "Connecting to Milvus host=%s port=%s secure=%s user_set=%s",
        vdb.milvus_host,
        vdb.milvus_port,
        vdb.milvus_secure,
        bool(vdb.milvus_user),
    )
    kwargs: Dict[str, Any] = {"host": vdb.milvus_host, "port": str(vdb.milvus_port), "secure": vdb.milvus_secure}
    if vdb.milvus_user:
        kwargs["user"] = vdb.milvus_user
    if vdb.milvus_password:
        kwargs["password"] = vdb.milvus_password
    connections.connect(alias="default", **kwargs)
    logger.info("Connected to Milvus alias=default")


def create_collection(collection_name: str, embedding: Embeddings, vdb: VectorDbConfig) -> Collection:
    logger.info(
        "Ensuring Milvus collection exists collection=%s hybrid_search=%s",
        collection_name,
        vdb.milvus_hybrid_search,
    )
    dim = len(embedding.embed_query("a"))
    logger.info("Resolved embedding dimension=%d for collection=%s", dim, collection_name)

    if collection_name not in utility.list_collections():
        logger.info("Milvus collection does not exist and will be created collection=%s", collection_name)
        dense_index_params = {"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 1024}}
        sparse_index_params = {"metric_type": "BM25", "index_type": "SPARSE_INVERTED_INDEX", "params": {"drop_ratio_build": 0.2}}

        if vdb.milvus_hybrid_search:
            fields = [
                FieldSchema("id", DataType.VARCHAR, is_primary=True, max_length=65535, auto_id=False),
                FieldSchema("dense", DataType.FLOAT_VECTOR, dim=dim),
                FieldSchema("sparse", DataType.SPARSE_FLOAT_VECTOR),
                FieldSchema("title", DataType.VARCHAR, max_length=65535),
                FieldSchema("source", DataType.VARCHAR, max_length=65535),
                FieldSchema("document_url", DataType.VARCHAR, max_length=65535),
                FieldSchema("page_number", DataType.VARCHAR, max_length=65535),
                FieldSchema("chunk_seq", DataType.INT32),
                FieldSchema("text", DataType.VARCHAR, max_length=65535, enable_analyzer=True),
            ]
            bm25_func = Function(
                name="bm25_text",
                function_type=FunctionType.BM25,
                input_field_names=["text"],
                output_field_names=["sparse"],
            )
            coll_schema = CollectionSchema(fields)
            coll_schema.add_function(bm25_func)
            coll = Collection(name=collection_name, schema=coll_schema)
            logger.info("Created Milvus collection schema collection=%s mode=hybrid", collection_name)
            coll.create_index(field_name="dense", index_params=dense_index_params)
            logger.info("Created Milvus dense index collection=%s", collection_name)
            coll.create_index(field_name="sparse", index_params=sparse_index_params)
            logger.info("Created Milvus sparse index collection=%s", collection_name)
        else:
            fields = [
                FieldSchema("id", DataType.VARCHAR, is_primary=True, max_length=65535, auto_id=False),
                FieldSchema("vector", DataType.FLOAT_VECTOR, dim=dim),
                FieldSchema("title", DataType.VARCHAR, max_length=65535),
                FieldSchema("source", DataType.VARCHAR, max_length=65535),
                FieldSchema("document_url", DataType.VARCHAR, max_length=65535),
                FieldSchema("page_number", DataType.VARCHAR, max_length=65535),
                FieldSchema("chunk_seq", DataType.INT32),
                FieldSchema("text", DataType.VARCHAR, max_length=65535),
            ]
            coll_schema = CollectionSchema(fields)
            coll = Collection(name=collection_name, schema=coll_schema)
            logger.info("Created Milvus collection schema collection=%s mode=dense", collection_name)
            coll.create_index(field_name="vector", index_params=dense_index_params)
            logger.info("Created Milvus vector index collection=%s", collection_name)
    else:
        logger.info("Milvus collection already exists collection=%s", collection_name)
        coll = Collection(name=collection_name)

    logger.info("Milvus collection ready collection=%s schema_fields=%s", collection_name, [f.name for f in coll.schema.fields])
    return coll


def _remote_bulk_writer_connect_param(vdb: VectorDbConfig):
    logger.info(
        "Preparing RemoteBulkWriter connection endpoint=%s bucket=%s region=%s remote_path=%s",
        vdb.bulk_cos_endpoint,
        vdb.bulk_cos_bucket,
        vdb.bulk_cos_region,
        vdb.bulk_remote_path,
    )
    if not vdb.bulk_cos_endpoint or not vdb.bulk_cos_bucket:
        raise ValueError("Milvus bulk writer requires MILVUS_BULK_COS_* env vars (endpoint, bucket, keys/region).")

    return RemoteBulkWriter.ConnectParam(
        endpoint=vdb.bulk_cos_endpoint,
        access_key=vdb.bulk_cos_access_key,
        secret_key=vdb.bulk_cos_secret_key,
        bucket_name=vdb.bulk_cos_bucket,
        secure=True,
        region=vdb.bulk_cos_region or None,
    )


def create_remote_writer(collection_obj: Collection, vdb: VectorDbConfig) -> RemoteBulkWriter:
    logger.info("Creating RemoteBulkWriter for collection=%s", collection_obj.name)
    if not vdb.bulk_remote_path:
        raise ValueError("MILVUS_BULK_REMOTE_PATH is required for Milvus bulk writer.")
    conn = _remote_bulk_writer_connect_param(vdb)
    writer = RemoteBulkWriter(
        schema=collection_obj.schema,
        remote_path=vdb.bulk_remote_path,
        connect_param=conn,
        file_type=BulkFileType.NUMPY,
    )
    logger.info("RemoteBulkWriter created collection=%s file_type=%s", collection_obj.name, BulkFileType.NUMPY)
    return writer


def prepare_docs_for_ingestion(
    processed_files: List[Tuple[str, List[Document]]],
    embedding: Embeddings,
    vdb: VectorDbConfig,
) -> List[Dict[str, Any]]:
    logger.info("Preparing documents for ingestion file_groups=%d vector_db=%s", len(processed_files), vdb.db_type)
    all_documents: List[Document] = []
    all_embeddings: List[List[float]] = []

    for _, documents in processed_files:
        if not documents:
            continue
        logger.info("Generating embeddings for file=%s chunks=%d", _, len(documents))
        doc_embeddings = embedding.embed_documents([str(doc.page_content) for doc in documents])
        logger.info("Generated embeddings for file=%s chunks=%d", _, len(documents))
        all_documents.extend(documents)
        all_embeddings.extend(doc_embeddings)

    records: List[Dict[str, Any]] = []
    for i, doc in enumerate(all_documents):
        clean_embedding_val = list(map(float, all_embeddings[i]))
        doc_id = generate_hash(
            doc.page_content
            + "\nTitle: " + doc.metadata.get("title", "")
            + "\nUrl: " + doc.metadata.get("document_url", "")
            + "\nPage: " + doc.metadata.get("page_number", "")
        )

        base: Dict[str, Any] = {
            "id": doc_id,
            "title": doc.metadata.get("title", ""),
            "document_url": doc.metadata.get("document_url", ""),
            "page_number": doc.metadata.get("page_number", ""),
            "source": doc.metadata.get("source", ""),
            "chunk_seq": int(doc.metadata.get("chunk_seq", 0) or 0),
            "text": doc.page_content,
        }

        if vdb.db_type == "opensearch":
            base["content"] = doc.page_content
            base["content_vector"] = clean_embedding_val
        elif vdb.db_type == "milvus":
            if vdb.milvus_hybrid_search:
                base["dense"] = clean_embedding_val
            else:
                base["vector"] = clean_embedding_val

        records.append(base)

    logger.info("Prepared %d records for ingestion into vector_db=%s", len(records), vdb.db_type)
    return records


async def ingest_from_cos_prefix(
    *,
    prefix: Optional[str] = None,
    bucket: Optional[str] = None,
    destination_index: Optional[str] = None,
) -> Dict[str, Any]:
    logger.info(
        "Starting ingestion request prefix=%s bucket=%s destination_override=%s",
        prefix,
        bucket,
        destination_index,
    )
    cos_cfg = load_cos_config()
    embed_cfg = load_embedding_config()
    chunk_cfg = load_chunking_config()
    vdb = load_vector_db_config()

    if not cos_cfg.is_configured():
        raise ValueError("COS is not configured. Set COS_ENDPOINT, COS_API_KEY, COS_INSTANCE_CRN, COS_BUCKET.")
    if not embed_cfg.is_configured():
        raise ValueError("Embedding is not configured. Set WATSONX_URL, WATSONX_API_KEY, WATSONX_PROJECT_ID, EMBEDDING_MODEL_ID.")
    if not vdb.is_configured():
        raise ValueError("Vector DB is not configured. Set VECTOR_DB_TYPE and required backend env vars.")

    source_bucket = (bucket or "").strip() or cos_cfg.bucket
    cos_prefix = (prefix if prefix is not None else cos_cfg.prefix) or ""
    dest = (destination_index or "").strip()
    logger.info(
        "Resolved ingestion configuration vector_db=%s source_bucket=%s cos_prefix=%s use_bulk=%s",
        vdb.db_type,
        source_bucket,
        cos_prefix or "<root>",
        vdb.milvus_use_bulk_ingestion if vdb.db_type == "milvus" else None,
    )

    if vdb.db_type == "opensearch":
        dest_name = dest or vdb.opensearch_index
    else:
        dest_name = dest or vdb.milvus_collection

    cos_client = _cos_client_from_config(cos_cfg)
    cos_objects = get_cos_objects(cos_client, source_bucket, cos_prefix)
    cos_files = [k for k in cos_objects if k.lower().endswith(tuple(SUPPORTED_FILE_TYPES))]
    logger.info("Filtered ingestible COS files count=%d from total_objects=%d", len(cos_files), len(cos_objects))

    embedding = get_embedding(embed_cfg)

    processed_count = 0
    chunk_count = 0

    if vdb.db_type == "opensearch":
        os_client = _opensearch_client(vdb)
        embedding_dim = len(embedding.embed_query("a"))
        _ensure_opensearch_index(os_client, dest_name, embedding_dim)

        actions = []
        for key in cos_files:
            logger.info("OpenSearch ingestion processing COS key=%s", key)
            file_map = process_cos_file(cos_client, source_bucket, key)
            for fname, content in file_map.items():
                processed_count += 1
                _, split_docs = process_file((fname, content), chunk_cfg)
                chunk_count += len(split_docs)

                records = prepare_docs_for_ingestion([(fname, split_docs)], embedding, vdb)
                logger.info("Prepared %d OpenSearch records for file=%s", len(records), fname)
                for rec in records:
                    actions.append({"_index": dest_name, "_id": rec["id"], "_source": rec})

        if actions:
            logger.info("Bulk indexing %d records into OpenSearch index=%s", len(actions), dest_name)
            os_bulk(os_client, actions)
            logger.info("OpenSearch bulk indexing completed index=%s", dest_name)

        logger.info("OpenSearch ingestion complete index=%s files_seen=%d files_processed=%d chunks_created=%d", dest_name, len(cos_files), processed_count, chunk_count)
        return {
            "status": "success",
            "vector_db": "opensearch",
            "destination_index": dest_name,
            "cos_bucket": source_bucket,
            "cos_prefix": cos_prefix,
            "files_seen": len(cos_files),
            "files_processed": processed_count,
            "chunks_created": chunk_count,
        }

    # Milvus ingestion path
    _milvus_connect(vdb)
    coll = create_collection(dest_name, embedding, vdb)

    if vdb.milvus_use_bulk_ingestion:
        # Bulk insert path
        logger.info("Using Milvus bulk ingestion mode")
        writer = create_remote_writer(coll, vdb)

        batch_files: List[List[str]] = []
        for key in cos_files:
            file_map = process_cos_file(cos_client, source_bucket, key)
            for fname, content in file_map.items():
                processed_count += 1
                _, split_docs = process_file((fname, content), chunk_cfg)
                chunk_count += len(split_docs)

                records = prepare_docs_for_ingestion([(fname, split_docs)], embedding, vdb)
                logger.info("Prepared %d Milvus bulk records for file=%s", len(records), fname)
                for rec in records:
                    writer.append_row(rec)

            logger.info("Committing RemoteBulkWriter batch for COS key=%s", key)
            files = writer.commit()
            logger.info("RemoteBulkWriter commit completed key=%s files=%s", key, files)
            if files:
                batch_files.append(files)

        task_ids = []
        for files in batch_files:
            logger.info("Submitting Milvus bulk insert collection=%s files=%s", dest_name, files)
            task_id = utility.do_bulk_insert(collection_name=dest_name, files=files)
            logger.info("Milvus bulk insert submitted collection=%s task_id=%s", dest_name, task_id)
            task_ids.append(task_id)

        logger.info("Milvus bulk ingestion submitted collection=%s files_seen=%d files_processed=%d chunks_created=%d bulk_batches=%d", dest_name, len(cos_files), processed_count, chunk_count, len(batch_files))
        return {
            "status": "started",
            "vector_db": "milvus",
            "destination_collection": dest_name,
            "cos_bucket": source_bucket,
            "cos_prefix": cos_prefix,
            "files_seen": len(cos_files),
            "files_processed": processed_count,
            "chunks_created": chunk_count,
            "bulk_tasks": [str(t) for t in task_ids],
        }
    else:
        # Direct insert path
        logger.info("Using Milvus direct insert mode")
        all_records = []
        file_details = []
        
        for key in cos_files:
            logger.info("Milvus direct ingestion processing COS key=%s", key)
            file_map = process_cos_file(cos_client, source_bucket, key)
            for fname, content in file_map.items():
                processed_count += 1
                _, split_docs = process_file((fname, content), chunk_cfg)
                file_chunk_count = len(split_docs)
                chunk_count += file_chunk_count

                records = prepare_docs_for_ingestion([(fname, split_docs)], embedding, vdb)
                logger.info("Prepared %d Milvus records for file=%s", len(records), fname)
                all_records.extend(records)
                
                # Track file details
                file_details.append({
                    "filename": fname,
                    "chunks": file_chunk_count
                })

        documents_inserted = 0
        if all_records:
            logger.info("Inserting %d records into Milvus collection=%s", len(all_records), dest_name)
            coll.insert(all_records)
            coll.flush()
            logger.info("Milvus direct insert completed collection=%s", dest_name)
            
            # Verify insertion by getting collection count
            coll.load()
            documents_inserted = coll.num_entities
            logger.info("Verified Milvus collection=%s total_documents=%d", dest_name, documents_inserted)

        logger.info("Milvus direct ingestion complete collection=%s files_seen=%d files_processed=%d chunks_created=%d documents_in_collection=%d", dest_name, len(cos_files), processed_count, chunk_count, documents_inserted)
        
        return {
            "status": "success",
            "vector_db": "milvus",
            "destination_collection": dest_name,
            "cos_bucket": source_bucket,
            "cos_prefix": cos_prefix,
            "files_seen": len(cos_files),
            "files_processed": processed_count,
            "chunks_created": chunk_count,
            "documents_inserted": len(all_records),
            "total_documents_in_collection": documents_inserted,
            "file_details": file_details[:10] if len(file_details) > 10 else file_details,
            "summary": f"Successfully ingested {processed_count} files into '{dest_name}' collection. Created {chunk_count} chunks from {len(cos_files)} files. Collection now contains {documents_inserted} total documents."
        }


# =============================================================================
# Bootstrap connectivity checks
# =============================================================================

def _print_bootstrap_status(name: str, ok: bool, detail: str = "") -> None:
    status = "OK" if ok else "FAIL"
    msg = f"[BOOTSTRAP] {name}: {status}"
    if detail:
        msg += f" - {detail}"
    if ok:
        logger.info(msg)
    else:
        logger.error(msg)
    print(msg, flush=True)


def bootstrap_check_connections() -> None:
    # COS
    try:
        cos_cfg = load_cos_config()
        if not cos_cfg.is_configured():
            _print_bootstrap_status("COS", False, "Not configured (missing COS_* env vars)")
        else:
            cos = _cos_client_from_config(cos_cfg)
            # cheap connectivity check: HEAD bucket
            cos.head_bucket(Bucket=cos_cfg.bucket)
            _print_bootstrap_status("COS", True, f"bucket={cos_cfg.bucket}")
    except Exception as e:
        _print_bootstrap_status("COS", False, f"{type(e).__name__}: {e}")

    # Embeddings (Watsonx)
    try:
        emb_cfg = load_embedding_config()
        if not emb_cfg.is_configured():
            _print_bootstrap_status("WATSONX_EMBEDDINGS", False, "Not configured (missing WATSONX_* / EMBEDDING_MODEL_ID)")
        else:
            emb = get_embedding(emb_cfg)
            # lightweight sanity check (calls service)
            _ = emb.embed_query("ping")
            _print_bootstrap_status("WATSONX_EMBEDDINGS", True, f"model={emb_cfg.embedding_model_id}")
    except Exception as e:
        _print_bootstrap_status("WATSONX_EMBEDDINGS", False, f"{type(e).__name__}: {e}")

    # Vector DB
    try:
        vdb = load_vector_db_config()
        if not vdb.is_configured():
            _print_bootstrap_status("VECTOR_DB", False, "Not configured (missing VECTOR_DB_TYPE + backend env vars)")
        elif vdb.db_type == "opensearch":
            os_client = _opensearch_client(vdb)
            ok = bool(os_client.ping())
            _print_bootstrap_status("OPENSEARCH", ok, f"host={vdb.opensearch_host}:{vdb.opensearch_port}")
        elif vdb.db_type == "milvus":
            _milvus_connect(vdb)
            ver = utility.get_server_version()
            _print_bootstrap_status("MILVUS", True, f"server_version={ver}")
        else:
            _print_bootstrap_status("VECTOR_DB", False, f"Unknown VECTOR_DB_TYPE={vdb.db_type}")
    except Exception as e:
        _print_bootstrap_status("VECTOR_DB", False, f"{type(e).__name__}: {e}")


# Run checks at import/startup so running "python server.py" prints status immediately.
bootstrap_check_connections()


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


@mcp.tool(description="Get current ingestion configuration from ENV only (secrets masked).")
def get_ingestion_configuration() -> Dict[str, Any]:
    cos_cfg = load_cos_config()
    embed_cfg = load_embedding_config()
    chunk_cfg = load_chunking_config()
    vdb = load_vector_db_config()

    return {
        "cos": {
            "configured": cos_cfg.is_configured(),
            "endpoint": cos_cfg.endpoint,
            "bucket": cos_cfg.bucket,
            "prefix": cos_cfg.prefix,
            "api_key": _mask_secret(cos_cfg.api_key, show_start=2, show_end=2) if cos_cfg.api_key else "",
            "instance_crn": _mask_secret(cos_cfg.instance_crn, show_start=6, show_end=6) if cos_cfg.instance_crn else "",
        },
        "embedding": {
            "configured": embed_cfg.is_configured(),
            "watsonx_url": embed_cfg.watsonx_url,
            "project_id": embed_cfg.project_id,
            "embedding_model_id": embed_cfg.embedding_model_id,
            "watsonx_api_key": _mask_secret(embed_cfg.watsonx_api_key, show_start=2, show_end=2) if embed_cfg.watsonx_api_key else "",
        },
        "chunking": asdict(chunk_cfg),
        "vector_db": {
            "configured": vdb.is_configured(),
            "db_type": vdb.db_type,
            "opensearch": {
                "host": vdb.opensearch_host,
                "port": vdb.opensearch_port,
                "use_ssl": vdb.opensearch_use_ssl,
                "index": vdb.opensearch_index,
                "username": _mask_username(vdb.opensearch_username),
                "password_set": bool(vdb.opensearch_password),
            },
            "milvus": {
                "host": vdb.milvus_host,
                "port": vdb.milvus_port,
                "secure": vdb.milvus_secure,
                "collection": vdb.milvus_collection,
                "hybrid_search": vdb.milvus_hybrid_search,
                "username": _mask_username(vdb.milvus_user),
                "password_set": bool(vdb.milvus_password),
                "bulk": {
                    "remote_path": vdb.bulk_remote_path,
                    "cos_endpoint": vdb.bulk_cos_endpoint,
                    "cos_bucket": vdb.bulk_cos_bucket,
                    "cos_region": vdb.bulk_cos_region,
                    "cos_access_key": _mask_secret(vdb.bulk_cos_access_key, show_start=2, show_end=2) if vdb.bulk_cos_access_key else "",
                    "cos_secret_key_set": bool(vdb.bulk_cos_secret_key),
                    "cos_is_ibm": vdb.bulk_cos_is_ibm,
                },
            },
        },
    }


@mcp.tool(description="Ingest files from COS into the configured vector database. Supports per-call bucket and destination index/collection.")
async def ingest_from_cos(prefix: str = "", bucket: str = "", destination_index: str = "") -> Dict[str, Any]:
    logger.info("MCP tool ingest_from_cos called prefix=%s bucket=%s destination_index=%s", prefix, bucket, destination_index)
    p = prefix if prefix is not None else ""
    b = bucket if bucket is not None else ""
    d = destination_index if destination_index is not None else ""
    return await ingest_from_cos_prefix(
        prefix=p if p != "" else None,
        bucket=b if b != "" else None,
        destination_index=d if d != "" else None,
    )


@mcp.tool(description="Verify ingestion by checking document count in Milvus collection")
async def verify_milvus_collection(collection_name: str = "") -> Dict[str, Any]:
    logger.info("MCP tool verify_milvus_collection called collection_name=%s", collection_name)
    vdb = load_vector_db_config()
    
    if vdb.db_type != "milvus":
        return {
            "status": "error",
            "message": f"Vector DB type is {vdb.db_type}, not milvus. This tool only works with Milvus."
        }
    
    coll_name = collection_name.strip() if collection_name else vdb.milvus_collection
    
    try:
        _milvus_connect(vdb)
        
        # Check if collection exists
        if coll_name not in utility.list_collections():
            return {
                "status": "error",
                "collection": coll_name,
                "message": f"Collection '{coll_name}' does not exist",
                "available_collections": utility.list_collections()
            }
        
        # Get collection and load it
        coll = Collection(name=coll_name)
        coll.load()
        
        # Get document count
        num_entities = coll.num_entities
        
        # Get a sample document if any exist
        sample_doc = None
        if num_entities > 0:
            results = coll.query(
                expr="",
                output_fields=["id", "title", "source", "text"],
                limit=1
            )
            if results:
                doc = results[0]
                sample_doc = {
                    "id": doc.get("id", "N/A"),
                    "title": doc.get("title", "N/A"),
                    "source": doc.get("source", "N/A"),
                    "text_preview": doc.get("text", "N/A")[:200] + "..." if doc.get("text") else "N/A"
                }
        
        logger.info("Milvus collection verification complete collection=%s count=%d", coll_name, num_entities)
        
        return {
            "status": "success",
            "collection": coll_name,
            "document_count": num_entities,
            "sample_document": sample_doc,
            "message": f"Collection has {num_entities} documents"
        }
        
    except Exception as e:
        logger.error("Error verifying Milvus collection collection=%s error=%s", coll_name, str(e))
        return {
            "status": "error",
            "collection": coll_name,
            "message": f"Error: {str(e)}"
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
                "get_ingestion_configuration",
                "ingest_from_cos",
            ],
        }
    )


app.add_route("/", index, methods=["GET"])
app.add_route("/health", health, methods=["GET"])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
