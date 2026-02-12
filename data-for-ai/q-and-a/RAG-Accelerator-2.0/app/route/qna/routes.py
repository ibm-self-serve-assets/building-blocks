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
    Returns answer, documents, expert_answer, log_id, and governance metrics.
    """
    if client is None:
        logger.error("IBM API client is not initialized")
        raise HTTPException(status_code=500, detail="IBM watsonx.ai client not initialized")

    try:
        q = req.question
        answer, documents, expert_answer, log_id = rag_helper_functions.query_llm(client, parameters['watsonx_deployment_id'], q, req.query_filter)
        html = rag_helper_functions.display_results(q, documents, True, answer, False)
        logger.info("html content: %s", html)
        
        # Evaluate with governance if available
        governance_metrics = None
        try:
            logger.info("Attempting governance evaluation...")
            answer_text = answer.get('response', '') if isinstance(answer, dict) else str(answer)
            logger.info(f"Answer text extracted: {len(answer_text)} characters")
            
            # Get contexts from query endpoint if documents are empty
            contexts_for_governance = documents
            if not documents or (isinstance(documents, dict) and len(documents) == 0):
                logger.info("Documents empty from QnA, fetching from query endpoint...")
                try:
                    import app.src.services.QueryService as query_service
                    query_payload = {
                        'query': q,
                        'connection_name': parameters.get('connection_name', 'milvus_connect'),
                        'index_name': parameters.get('vector_store_index_name', 'sample')
                    }
                    search_results, top_result = query_service.generate_answer(query_payload)
                    contexts_for_governance = search_results
                    logger.info(f"Retrieved {len(search_results) if search_results else 0} contexts from query endpoint")
                except Exception as query_error:
                    logger.warning(f"Could not fetch contexts from query endpoint: {query_error}")
            
            logger.info(f"Contexts type: {type(contexts_for_governance)}, length: {len(contexts_for_governance) if contexts_for_governance else 0}")
            
            governance_metrics = service.evaluate_with_governance(q, answer_text, contexts_for_governance)
            
            if governance_metrics:
                logger.info(f"Governance metrics received: {governance_metrics}")
            else:
                logger.warning("Governance evaluation returned None")
        except Exception as gov_error:
            logger.error(f"Governance evaluation failed (non-critical): {gov_error}", exc_info=True)
        
        # Create response with governance metrics
        response_data = {
            "answer": answer,
            "documents": documents,
            "expert_answer": expert_answer,
            "log_id": log_id
        }
        
        # Add governance metrics if available
        if governance_metrics:
            response_data["governance_metrics"] = governance_metrics
        
        return QueryResponse(**response_data)
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