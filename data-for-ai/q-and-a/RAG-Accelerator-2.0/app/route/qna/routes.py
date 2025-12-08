import os
import json
import time
import logging
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Security
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from app.src.model.QnAAIServiceModel import QueryRequest, QueryResponse
import app.src.services.QnAAIService as service
import app.src.utils.rag_helper_functions as rag_helper_functions
from app.src.utils import config
from app.src.utils import rag_helper_functions


# load .env
load_dotenv()

# Logging configuration controlled via .env
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("rag_service")

# Get parameters from config
parameter_sets = config.PARAMETERS
parameter_sets_list = list(parameter_sets.keys())
parameters=rag_helper_functions.get_parameter_sets(parameter_sets_list)


# Initialize router
qna_ai_service_route = APIRouter(
    prefix="",
    tags=["QnA AI Service"]
)

client = service.init_api_client()

@qna_ai_service_route.post("/ai/qna/query", response_model=QueryResponse)
async def query_api(req: QueryRequest):
    """Query the watsonx.ai LLM using the same helper functions as the notebook.
    Returns answer, documents, expert_answer and log_id.
    """
    if client is None:
        logger.error("IBM API client is not initialized")
        raise HTTPException(status_code=500, detail="IBM watsonx.ai client not initialized")

    try:
        q = req.question
        answer, documents, expert_answer, log_id = rag_helper_functions.query_llm(client, parameters['watsonx_deployment_id'], q, req.query_filter)        
        html = rag_helper_functions.display_results(q, documents, True, answer, False)
        logger.info("html content: %s", html)
        return QueryResponse(answer=answer, documents=documents, expert_answer=expert_answer, log_id=log_id)
    except Exception as e:
        logger.exception("Error while querying LLM: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
    
@qna_ai_service_route.post("/ai/qna/qa")
async def run_qa():
    """Run the interactive QA flow (calls rag_helper_functions.qa_with_llm).
    Useful for running the same notebook functionality programmatically.
    """
    if client is None:
        logger.error("IBM API client is not initialized")
        raise HTTPException(status_code=500, detail="IBM watsonx.ai client not initialized")

    try:
        retrieval_flag = False
        ## Commented below code to disable parameter set fetching
        #try:
        #    parameters = rag_helper_functions.get_parameter_sets(None, ["RAG_parameter_set"]) if hasattr(rag_helper_functions, "get_parameter_sets") else {}
        #    retrieval_flag = parameters.get("retrieval_flag", "false").strip().lower() == "true"
        #except Exception:
        #    pass

        rag_helper_functions.qa_with_llm(client, parameters['watsonx_deployment_id'], retrieval_flag)
        return {"status": "qa invoked"}
    except Exception as e:
        logger.exception("Error running qa_with_llm: %s", e)
        raise HTTPException(status_code=500, detail=str(e))