"""
IBM watsonx.data OpenSearch Ingestion Service.
Downloads documents from IBM COS, generates watsonx.ai embeddings,
creates a k-NN index in watsonx.data OpenSearch, and bulk-inserts vectors.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import time
from typing import Any

from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk
from tqdm import tqdm
from unstructured.partition.auto import partition

from app.src.utils.cos_ops import download_objects, list_objects
from app.src.utils.opensearch_conn import get_opensearch_client

logger = logging.getLogger(__name__)

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "128"))
BATCH_SIZE = int(os.getenv("INDEX_CHUNK_BATCH_SIZE", "256"))


# ---------------------------------------------------------------------------
# IBM watsonx.ai embedding helper
# ---------------------------------------------------------------------------

def _get_embedding_client(model_id: str) -> Embeddings:
    """Return an IBM watsonx.ai Embeddings client."""
    creds = Credentials(
        url=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
        api_key=os.environ["IBM_API_KEY"],
    )
    return Embeddings(
        model_id=model_id,
        credentials=creds,
        project_id=os.environ["WATSONX_PROJECT_ID"],
    )


def _embedding_dim(model_id: str) -> int:
    """Return embedding dimension for known watsonx.ai embedding models."""
    dims = {
        "ibm/slate-125m-english-rtrvr": 768,
        "ibm/slate-30m-english-rtrvr": 384,
        "intfloat/multilingual-e5-large": 1024,
    }
    return dims.get(model_id, 768)


# ---------------------------------------------------------------------------
# OpenSearch index management
# ---------------------------------------------------------------------------

def _create_knn_index(client: OpenSearch, index_name: str, dim: int) -> None:
    """Create a k-NN index in IBM watsonx.data OpenSearch if it doesn't exist."""
    if client.indices.exists(index=index_name):
        logger.info("Index '%s' already exists — skipping creation", index_name)
        return

    body = {
        "settings": {
            "index": {
                "knn": True,
                "knn.algo_param.ef_search": 100,
                "number_of_shards": 1,
                "number_of_replicas": 1,
            }
        },
        "mappings": {
            "properties": {
                "id":            {"type": "keyword"},
                "text":          {"type": "text"},
                "title":         {"type": "keyword"},
                "source":        {"type": "keyword"},
                "document_url":  {"type": "keyword"},
                "page_number":   {"type": "keyword"},
                "chunk_seq":     {"type": "integer"},
                "vector": {
                    "type": "knn_vector",
                    "dimension": dim,
                    "method": {
                        "name": "hnsw",
                        "space_type": "l2",
                        "engine": "nmslib",
                        "parameters": {"ef_construction": 128, "m": 24},
                    },
                },
            }
        },
    }
    client.indices.create(index=index_name, body=body)
    logger.info("Created k-NN index '%s' with dim=%d", index_name, dim)


# ---------------------------------------------------------------------------
# Document processing
# ---------------------------------------------------------------------------

def _parse_documents(file_paths: list[str]) -> list[dict[str, Any]]:
    """Use unstructured to extract text from PDF, DOCX, TXT, HTML, etc."""
    docs: list[dict[str, Any]] = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

    for path in file_paths:
        try:
            elements = partition(filename=path)
            full_text = "\n".join([str(e) for e in elements])
            chunks = splitter.split_text(full_text)
            for i, chunk in enumerate(chunks):
                docs.append({
                    "text": chunk,
                    "title": os.path.basename(path),
                    "source": path,
                    "document_url": "",
                    "page_number": str(i),
                    "chunk_seq": i,
                })
        except Exception as e:
            logger.warning("Failed to parse %s: %s", path, e)

    return docs


def _doc_id(doc: dict) -> str:
    return hashlib.sha256(
        (doc["text"] + doc["title"] + doc["source"] + doc["page_number"]).encode()
    ).hexdigest()


# ---------------------------------------------------------------------------
# Ingestion main
# ---------------------------------------------------------------------------

def ingest(
    bucket_name: str,
    directory: str,
    index_name: str,
    embedding_model_id: str = "ibm/slate-125m-english-rtrvr",
) -> int:
    """
    Full ingestion pipeline:
      1. List + download files from IBM COS
      2. Parse + chunk with unstructured
      3. Embed with IBM watsonx.ai
      4. Create k-NN index in IBM watsonx.data OpenSearch
      5. Bulk insert document vectors
    Returns number of documents indexed.
    """
    logger.info("Starting OpenSearch ingestion: bucket=%s prefix=%s index=%s",
                bucket_name, directory, index_name)

    # 1. COS download
    keys = list_objects(bucket_name, directory)
    if not keys:
        logger.warning("No objects found in COS: bucket=%s prefix=%s", bucket_name, directory)
        return 0

    local_dir = os.path.join("downloads", index_name)
    try:
        file_paths = download_objects(bucket_name, keys, local_dir)

        # 2. Parse + chunk
        docs = _parse_documents(file_paths)
        logger.info("Parsed %d document chunks", len(docs))

        # 3. Embeddings
        embed_client = _get_embedding_client(embedding_model_id)
        dim = _embedding_dim(embedding_model_id)

        # 4. OpenSearch index
        os_client = get_opensearch_client()
        _create_knn_index(os_client, index_name, dim)

        # 5. Bulk insert in batches
        total = 0
        with tqdm(total=len(docs), desc="Indexing into OpenSearch", unit="docs") as pbar:
            for i in range(0, len(docs), BATCH_SIZE):
                batch = docs[i: i + BATCH_SIZE]
                texts = [d["text"] for d in batch]
                try:
                    vectors = embed_client.embed_documents(texts)
                except Exception as e:
                    logger.warning("Embedding batch failed: %s", e)
                    pbar.update(len(batch))
                    continue

                actions = [
                    {
                        "_index": index_name,
                        "_id": _doc_id(doc),
                        "_source": {
                            "id":           _doc_id(doc),
                            "text":         doc["text"],
                            "title":        doc["title"],
                            "source":       doc["source"],
                            "document_url": doc["document_url"],
                            "page_number":  doc["page_number"],
                            "chunk_seq":    doc["chunk_seq"],
                            "vector":       vec,
                        },
                    }
                    for doc, vec in zip(batch, vectors)
                ]
                success, _ = bulk(os_client, actions, refresh=True)
                total += success
                pbar.update(len(batch))

        logger.info("Ingestion complete: %d documents indexed into '%s'", total, index_name)
        return total

    finally:
        if os.path.exists(local_dir):
            shutil.rmtree(local_dir)
            logger.debug("Cleaned up local dir: %s", local_dir)
