"""Health check route."""
from fastapi import APIRouter
router = APIRouter(tags=["Health"])


@router.get("/", summary="Health check")
async def root() -> dict:
    return {"status": "ok", "service": "IBM watsonx.data OpenSearch Ingestion Service"}
