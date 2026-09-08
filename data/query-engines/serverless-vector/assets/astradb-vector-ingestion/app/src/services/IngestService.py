"""
DataStax Astra DB vector ingestion service.

Uses:
  - astrapy (official Python SDK) for Astra DB Data API
  - IBM watsonx.ai for embedding generation
  - IBM COS for document source
  - unstructured for document parsing

Astra DB Data API reference:
  https://docs.datastax.com/en/astra/astra-db-vector/api-reference/data-api.html
"""
from __future__ import annotations

import hashlib
import logging
import os
import shutil
from typing import Any

from astrapy import DataAPIClient
from astrapy.constants import VectorMetric
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm
from unstructured.partition.auto import partition

from app.src.utils.cos_ops import download_objects, list_objects

logger = logging.getLogger(__name__)

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "128"))
BATCH_SIZE = int(os.getenv("INDEX_CHUNK_BATCH_SIZE", "20"))

_EMBEDDING_DIMS: dict[str, int] = {
    "ibm/slate-125m-english-rtrvr": 768,
    "ibm/slate-30m-english-rtrvr": 384,
    "intfloat/multilingual-e5-large": 1024,
}


# ---------------------------------------------------------------------------
# Astra DB helpers
# ---------------------------------------------------------------------------

def _get_collection(collection_name: str, dimension: int):
    """Get or create a vector collection in Astra DB using astrapy Data API."""
    client = DataAPIClient(os.environ["ASTRA_DB_APPLICATION_TOKEN"])
    db = client.get_database(os.environ["ASTRA_DB_API_ENDPOINT"])
    try:
        collection = db.get_collection(collection_name)
        logger.info("Using existing Astra DB collection: %s", collection_name)
    except Exception:
        collection = db.create_collection(
            collection_name,
            dimension=dimension,
            metric=VectorMetric.COSINE,
        )
        logger.info("Created Astra DB collection: %s (dim=%d)", collection_name, dimension)
    return collection


# ---------------------------------------------------------------------------
# IBM watsonx.ai embeddings
# ---------------------------------------------------------------------------

def _get_embedder(model_id: str) -> Embeddings:
    return Embeddings(
        model_id=model_id,
        credentials=Credentials(
            url=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
            api_key=os.environ["IBM_API_KEY"],
        ),
        project_id=os.environ["WATSONX_PROJECT_ID"],
    )


# ---------------------------------------------------------------------------
# Document processing
# ---------------------------------------------------------------------------

def _parse_files(file_paths: list[str]) -> list[dict[str, Any]]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    docs: list[dict[str, Any]] = []
    for path in file_paths:
        try:
            text = "\n".join(str(e) for e in partition(filename=path))
            for i, chunk in enumerate(splitter.split_text(text)):
                docs.append({
                    "text": chunk,
                    "title": os.path.basename(path),
                    "source": path,
                    "page_number": str(i),
                    "chunk_seq": i,
                })
        except Exception as exc:
            logger.warning("Failed to parse %s: %s", path, exc)
    return docs


def _doc_id(doc: dict) -> str:
    return hashlib.sha256((doc["text"] + doc["title"] + doc["page_number"]).encode()).hexdigest()[:40]


# ---------------------------------------------------------------------------
# Main ingestion function
# ---------------------------------------------------------------------------

def ingest(
    bucket_name: str,
    directory: str,
    collection_name: str,
    embedding_model_id: str = "ibm/slate-125m-english-rtrvr",
) -> int:
    """
    Full pipeline:
      1. Download from IBM COS
      2. Parse + chunk with unstructured
      3. Embed with IBM watsonx.ai
      4. Upsert into Astra DB vector collection
    """
    logger.info("Starting Astra DB ingestion: bucket=%s prefix=%s collection=%s",
                bucket_name, directory, collection_name)

    keys = list_objects(bucket_name, directory)
    if not keys:
        logger.warning("No COS objects found: %s / %s", bucket_name, directory)
        return 0

    local_dir = os.path.join("downloads", collection_name)
    try:
        file_paths = download_objects(bucket_name, keys, local_dir)
        docs = _parse_files(file_paths)
        logger.info("Parsed %d chunks", len(docs))

        embedder = _get_embedder(embedding_model_id)
        dim = _EMBEDDING_DIMS.get(embedding_model_id, 768)
        collection = _get_collection(collection_name, dim)

        total = 0
        with tqdm(total=len(docs), desc="Inserting into Astra DB", unit="docs") as pbar:
            for i in range(0, len(docs), BATCH_SIZE):
                batch = docs[i: i + BATCH_SIZE]
                texts = [d["text"] for d in batch]
                try:
                    vectors = embedder.embed_documents(texts)
                except Exception as exc:
                    logger.warning("Embedding batch failed: %s", exc)
                    pbar.update(len(batch))
                    continue

                records = [
                    {
                        "_id": _doc_id(doc),
                        "$vector": vec,
                        "text": doc["text"],
                        "title": doc["title"],
                        "source": doc["source"],
                        "page_number": doc["page_number"],
                        "chunk_seq": doc["chunk_seq"],
                    }
                    for doc, vec in zip(batch, vectors)
                ]

                result = collection.insert_many(records, ordered=False)
                total += len(result.inserted_ids)
                pbar.update(len(batch))

        logger.info("Astra DB ingestion complete: %d documents inserted into '%s'", total, collection_name)
        return total

    finally:
        if os.path.exists(local_dir):
            shutil.rmtree(local_dir)
