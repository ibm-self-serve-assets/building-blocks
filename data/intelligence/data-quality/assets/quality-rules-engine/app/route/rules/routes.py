"""DQ Rules and quality score API routes."""
from __future__ import annotations
import logging, os
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from app.src.model.RulesModel import DQRuleCreate
from app.src.model.ResultsModel import QualityScoreResponse
import app.src.services.RulesService as rules_svc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rules", tags=["Data Quality Rules"])
_KEY = APIKeyHeader(name="REST_API_KEY", auto_error=False)


def _auth(key: str = Security(_KEY)) -> str:
    if key != os.environ.get("REST_API_KEY"):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API key")
    return key


@router.post("", summary="Create a watsonx.data Intelligence DQ rule")
async def create_rule(rule: DQRuleCreate, _: str = Security(_auth)) -> dict:
    try:
        payload = rule.model_dump(exclude_none=True)
        payload["asset_ref"] = {"asset_id": rule.asset_ref.asset_id}
        return rules_svc.create_rule(payload)
    except Exception as exc:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("", summary="List DQ rules")
async def list_rules(_: str = Security(_auth)) -> dict:
    try:
        return rules_svc.list_rules()
    except Exception as exc:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post("/{rule_id}/execute", summary="Execute a DQ rule")
async def execute_rule(rule_id: str, _: str = Security(_auth)) -> dict:
    try:
        return rules_svc.execute_rule(rule_id)
    except Exception as exc:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/score", summary="Get aggregate quality score", response_model=QualityScoreResponse)
async def get_quality_score(_: str = Security(_auth)) -> QualityScoreResponse:
    try:
        return QualityScoreResponse(**rules_svc.get_quality_score())
    except Exception as exc:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
