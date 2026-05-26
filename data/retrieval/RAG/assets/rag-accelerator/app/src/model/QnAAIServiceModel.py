from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    query_filter: dict | None = None

class QueryResponse(BaseModel):
    answer: dict | None
    documents: dict | None
    expert_answer: str | None
    log_id: str | None