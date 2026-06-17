"""Vector ingestion route."""
from __future__ import annotations
import logging, os, time
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from app.src.model.IngestModel import VectorIngestRequest, VectorIngestResponse
import app.src.services.IngestService as svc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ingest", tags=["Vector Ingestion"])
_KEY = APIKeyHeader(name="REST_API_KEY", auto_error=False)


def _auth(key: str = Security(_KEY)) -> str:
    if key != os.environ.get("REST_API_KEY"):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API key")
    return key


@router.post(
    "",
    summary="Ingest IBM COS documents into Astra DB vector collection",
    description=(
        "Downloads documents from IBM COS, generates IBM watsonx.ai embeddings, "
        "and upserts them into a DataStax Astra DB vector collection using the Data API."
    ),
    response_model=VectorIngestResponse,
)
async def ingest(req: VectorIngestRequest, _: str = Security(_auth)) -> VectorIngestResponse:
    try:
        tic = time.perf_counter()
        n = svc.ingest(req.bucket_name, req.directory, req.collection_name, req.embedding_model_id)
        elapsed = round(time.perf_counter() - tic, 2)
        return VectorIngestResponse(
            status="success",
            message=f"Inserted {n} document chunks in {elapsed}s",
            collection_name=req.collection_name,
            documents_inserted=n,
        )
    except Exception as exc:
        logger.exception("ingest failed: %s", exc)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
