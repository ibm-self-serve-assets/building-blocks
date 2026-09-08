"""Ingest API route."""
from __future__ import annotations
import logging, os, time
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from app.src.model.IngestDataModel import IngestRequest, IngestResponse
import app.src.services.IngestService as ingest_svc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ingest", tags=["Ingest Documents"])
_KEY = APIKeyHeader(name="REST_API_KEY", auto_error=False)


def _auth(key: str = Security(_KEY)) -> str:
    if key != os.environ.get("REST_API_KEY"):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API key")
    return key


@router.post(
    "",
    summary="Ingest documents from IBM COS into watsonx.data OpenSearch",
    description=(
        "Downloads documents from IBM COS, generates IBM watsonx.ai embeddings "
        "(ibm/slate-125m-english-rtrvr), creates a k-NN index in IBM watsonx.data "
        "OpenSearch, and bulk-inserts document vectors with metadata."
    ),
    response_model=IngestResponse,
)
async def ingest_documents(req: IngestRequest, _: str = Security(_auth)) -> IngestResponse:
    try:
        tic = time.perf_counter()
        count = ingest_svc.ingest(
            bucket_name=req.bucket_name,
            directory=req.directory,
            index_name=req.index_name,
            embedding_model_id=req.embedding_model_id,
        )
        elapsed = round(time.perf_counter() - tic, 2)
        return IngestResponse(
            status="success",
            message=f"Ingested {count} document chunks in {elapsed}s",
            index_name=req.index_name,
            documents_indexed=count,
        )
    except Exception as exc:
        logger.exception("Ingestion failed: %s", exc)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
