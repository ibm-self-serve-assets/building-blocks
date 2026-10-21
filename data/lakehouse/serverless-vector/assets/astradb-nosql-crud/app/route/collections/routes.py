"""NoSQL CRUD API routes for DataStax Astra DB."""
from __future__ import annotations
import logging, os
from typing import Any
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from app.src.model.DocumentModel import (
    DocumentInsert, DocumentQuery, DocumentUpdate, DocumentDelete, CRUDResponse
)
import app.src.services.CRUDService as svc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/collections", tags=["NoSQL CRUD"])
_KEY = APIKeyHeader(name="REST_API_KEY", auto_error=False)


def _auth(key: str = Security(_KEY)) -> str:
    if key != os.environ.get("REST_API_KEY"):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API key")
    return key


@router.post("/insert", summary="Insert documents into an Astra DB collection",
             response_model=CRUDResponse)
async def insert_documents(req: DocumentInsert, _: str = Security(_auth)) -> CRUDResponse:
    try:
        n = svc.insert_documents(req.collection_name, req.documents)
        return CRUDResponse(status="success", collection_name=req.collection_name,
                            affected_count=n, message=f"Inserted {n} documents")
    except Exception as exc:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/find", summary="Query documents from an Astra DB collection")
async def find_documents(req: DocumentQuery, _: str = Security(_auth)) -> list[dict[str, Any]]:
    try:
        return svc.find_documents(req.collection_name, req.filter, req.limit, req.projection)
    except Exception as exc:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/update", summary="Update documents in an Astra DB collection",
             response_model=CRUDResponse)
async def update_document(req: DocumentUpdate, _: str = Security(_auth)) -> CRUDResponse:
    try:
        n = svc.update_document(req.collection_name, req.filter, req.update, req.upsert)
        return CRUDResponse(status="success", collection_name=req.collection_name,
                            affected_count=n, message=f"Updated {n} documents")
    except Exception as exc:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/delete", summary="Delete documents from an Astra DB collection",
             response_model=CRUDResponse)
async def delete_documents(req: DocumentDelete, _: str = Security(_auth)) -> CRUDResponse:
    try:
        n = svc.delete_documents(req.collection_name, req.filter)
        return CRUDResponse(status="success", collection_name=req.collection_name,
                            affected_count=n, message=f"Deleted {n} documents")
    except Exception as exc:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
