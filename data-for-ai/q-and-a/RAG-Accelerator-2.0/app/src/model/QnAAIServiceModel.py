from pydantic import BaseModel
from typing import Optional, Dict, Any


class QueryRequest(BaseModel):
    question: str
    query_filter: dict | None = None

class QueryResponse(BaseModel):
    answer: dict | None
    documents: dict | None
    expert_answer: str | None
    log_id: str | None
    governance_metrics: Optional[Dict[str, Any]] = None