"""
Astra DB CRUD service — wraps astrapy Data API for NoSQL operations.
Uses the Document API (non-vector collections).
Ref: https://docs.datastax.com/en/astra/astra-db-vector/api-reference/data-api.html
"""
from __future__ import annotations

import logging
import os
from typing import Any

from astrapy import DataAPIClient

logger = logging.getLogger(__name__)


def _get_db():
    client = DataAPIClient(os.environ["ASTRA_DB_APPLICATION_TOKEN"])
    return client.get_database(os.environ["ASTRA_DB_API_ENDPOINT"])


def get_or_create_collection(collection_name: str):
    """Get existing collection or create a new NoSQL (non-vector) collection."""
    db = _get_db()
    try:
        col = db.get_collection(collection_name)
        logger.debug("Found existing collection: %s", collection_name)
    except Exception:
        col = db.create_collection(collection_name)
        logger.info("Created new collection: %s", collection_name)
    return col


def insert_documents(collection_name: str, documents: list[dict[str, Any]]) -> int:
    """Insert documents into an Astra DB NoSQL collection. Returns inserted count."""
    col = get_or_create_collection(collection_name)
    result = col.insert_many(documents, ordered=False)
    logger.info("Inserted %d documents into '%s'", len(result.inserted_ids), collection_name)
    return len(result.inserted_ids)


def find_documents(
    collection_name: str,
    filter_expr: dict,
    limit: int = 20,
    projection: dict | None = None,
) -> list[dict[str, Any]]:
    """Query documents from an Astra DB collection."""
    col = get_or_create_collection(collection_name)
    cursor = col.find(filter=filter_expr, limit=limit, projection=projection or {})
    return list(cursor)


def update_document(
    collection_name: str,
    filter_expr: dict,
    update_expr: dict,
    upsert: bool = False,
) -> int:
    """Update document(s) matching filter. Returns modified count."""
    col = get_or_create_collection(collection_name)
    result = col.update_many(filter=filter_expr, update=update_expr, upsert=upsert)
    logger.info("Updated documents in '%s': modified=%s", collection_name, result.update_info.get("nModified", 0))
    return result.update_info.get("nModified", 0)


def delete_documents(collection_name: str, filter_expr: dict) -> int:
    """Delete document(s) matching filter. Returns deleted count."""
    col = get_or_create_collection(collection_name)
    result = col.delete_many(filter=filter_expr)
    logger.info("Deleted %d documents from '%s'", result.deleted_count, collection_name)
    return result.deleted_count
