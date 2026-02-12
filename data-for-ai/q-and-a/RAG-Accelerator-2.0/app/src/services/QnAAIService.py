import os
import json
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from app.src.utils import config
from app.src.utils import rag_helper_functions


# load .env
load_dotenv()

# Logging configuration controlled via .env
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("rag_service")

# IBM client import (lazy)
try:
    from ibm_watsonx_ai import APIClient
except Exception as e:
    logger.exception("Failed to import ibm_watson_studio_lib: %s", e)

# IBM Watsonx Governance imports (optional)
governance_available = False
try:
    from ibm_watsonx_gov.config import Credentials, GenAIConfiguration
    from ibm_watsonx_gov.clients.api_client import APIClient as GovAPIClient
    from ibm_watsonx_gov.evaluators import MetricsEvaluator
    from ibm_watsonx_gov.metrics import (
        ContextRelevanceMetric,
        FaithfulnessMetric,
        AnswerRelevanceMetric
    )
    governance_available = True
    logger.info("IBM Watsonx Governance library loaded successfully")
except ImportError as e:
    logger.warning(f"IBM Watsonx Governance library not available: {e}")

# Environment variables
#ENVIRONMENT = os.getenv("ENVIRONMENT", "cloud")
#RUNTIME_ENV_APSX_URL = os.getenv("RUNTIME_ENV_APSX_URL")
#RUNTIME_ENV_REGION = os.getenv("RUNTIME_ENV_REGION")
#USER_ACCESS_TOKEN = os.getenv("USER_ACCESS_TOKEN")
#WATSONX_DEPLOYMENT_ID = os.getenv("WATSONX_DEPLOYMENT_ID")
#WATSONX_SPACE_ID = os.getenv("WATSONX_SPACE_ID")
#WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")

# Get parameters from config
parameter_sets = config.PARAMETERS
parameter_sets_list = list(parameter_sets.keys())
parameters=rag_helper_functions.get_parameter_sets(parameter_sets_list)


# Global governance evaluator
governance_evaluator = None
governance_config = None


def init_governance_evaluator():
    """Initialize the IBM Watsonx Governance evaluator."""
    global governance_evaluator, governance_config
    
    if not governance_available:
        logger.info("Governance library not available, skipping initialization")
        return None
    
    try:
        # Get credentials from environment
        api_key = os.getenv("IBM_API_KEY")
        service_instance_id = os.getenv("WXG_SERVICE_INSTANCE_ID")
        
        if not api_key or not service_instance_id:
            logger.warning("IBM Watsonx Governance credentials not found. Governance evaluation disabled.")
            return None
        
        # Configure field mappings
        governance_config = GenAIConfiguration(
            input_fields=["question"],
            context_fields=["contexts"],
            output_fields=["answer"],
            reference_fields=["ground_truth"]
        )
        
        # Create credentials and evaluator
        credentials = Credentials(
            api_key=api_key,
            service_instance_id=service_instance_id,
        )
        
        governance_evaluator = MetricsEvaluator(
            api_client=GovAPIClient(credentials=credentials),
            configuration=governance_config
        )
        
        logger.info("IBM Watsonx Governance evaluator initialized successfully")
        return governance_evaluator
        
    except Exception as e:
        logger.error(f"Failed to initialize Governance evaluator: {e}")
        return None


def extract_top_context(documents: Any) -> str:
    """
    Extract the most relevant document text from the documents field.
    Handles both Milvus and Elasticsearch response formats.
    
    Args:
        documents: The documents field from QnA API response
        
    Returns:
        str: The text content of the top-ranked document
    """
    logger.info(f"extract_top_context - documents type: {type(documents)}")
    logger.info(f"extract_top_context - documents value: {str(documents)[:500]}")
    
    if not documents:
        logger.warning("Documents is None or empty")
        return ""
    
    # Check if documents is a list (Milvus format with tuples)
    if isinstance(documents, list) and len(documents) > 0:
        logger.info(f"Documents is a list with {len(documents)} items")
        top_doc = documents[0]
        logger.info(f"First document type: {type(top_doc)}")
        
        # Handle tuple format: (Document, score)
        if isinstance(top_doc, tuple) and len(top_doc) >= 2:
            doc_obj = top_doc[0]
            logger.info(f"Tuple document object type: {type(doc_obj)}")
            if hasattr(doc_obj, 'page_content'):
                context = doc_obj.page_content
                logger.info(f"Extracted context from page_content: {len(context)} chars")
                return context
            elif isinstance(doc_obj, dict):
                context = doc_obj.get('page_content', doc_obj.get('text', ''))
                logger.info(f"Extracted context from dict: {len(context)} chars")
                return context
        
        # Handle direct Document object
        elif hasattr(top_doc, 'page_content'):
            context = top_doc.page_content
            logger.info(f"Extracted context from Document.page_content: {len(context)} chars")
            return context
        
        # Handle dict format
        elif isinstance(top_doc, dict):
            context = top_doc.get('page_content', top_doc.get('text', ''))
            logger.info(f"Extracted context from dict: {len(context)} chars")
            return context
        
        logger.warning(f"Could not extract context from document type: {type(top_doc)}")
    
    # Check if documents is a dict (Elasticsearch format)
    elif isinstance(documents, dict):
        if 'hits' in documents and 'hits' in documents['hits']:
            hits = documents['hits']['hits']
            if len(hits) > 0:
                return hits[0].get('_source', {}).get('text', '')
        elif 'results' in documents and len(documents['results']) > 0:
            return documents['results'][0].get('text', documents['results'][0].get('page_content', ''))
    
    # Fallback
    logger.warning(f"Unexpected documents format: {type(documents)}")
    return str(documents)[:500]


def evaluate_with_governance(question: str, answer_text: str, documents: Any) -> Optional[Dict[str, Any]]:
    """
    Evaluate a QnA response using IBM Watsonx Governance metrics.
    
    Args:
        question: The user's question
        answer_text: The generated answer text
        documents: The retrieved documents/contexts
        
    Returns:
        Dict containing governance metrics or None if evaluation fails
    """
    logger.info(f"evaluate_with_governance called - evaluator status: {governance_evaluator is not None}")
    
    if not governance_evaluator:
        logger.warning("Governance evaluator not initialized, skipping evaluation")
        logger.warning(f"governance_available: {governance_available}")
        return None
    
    try:
        # Extract top context from documents
        top_context = extract_top_context(documents)
        
        if not top_context:
            logger.warning("No context extracted from documents. Skipping governance evaluation.")
            return None
        
        # Prepare data for evaluation
        governance_data = {
            'question': [question],
            'contexts': [[top_context]],  # Must be list of lists
            'answer': [answer_text]
        }
        
        # Define metrics (excluding those that require ground_truth)
        metrics = [
            ContextRelevanceMetric(),
            FaithfulnessMetric(),
            AnswerRelevanceMetric()
        ]
        
        # Run evaluation
        logger.info("Running governance evaluation...")
        evaluation_result = governance_evaluator.evaluate(
            data=governance_data,
            metrics=metrics
        )
        
        # Extract metric scores
        result_dict = {
            'evaluation_status': 'success',
            'metrics': {}
        }
        
        # Convert evaluation result to dictionary format
        if hasattr(evaluation_result, 'to_df'):
            df = evaluation_result.to_df()
            if not df.empty:
                # Extract metric columns (exclude input/output columns)
                metric_columns = [col for col in df.columns 
                                if col not in ['question', 'contexts', 'answer', 'ground_truth']]
                
                for col in metric_columns:
                    result_dict['metrics'][col] = float(df[col].iloc[0]) if df[col].iloc[0] is not None else None
        
        logger.info(f"Governance evaluation completed: {result_dict['metrics']}")
        return result_dict
        
    except Exception as e:
        logger.error(f"Error during governance evaluation: {e}", exc_info=True)
        return {
            'evaluation_status': 'error',
            'error_message': str(e),
            'metrics': {}
        }


def init_api_client():
    global client
    client = None

    # init API client
    try:
        if parameters['watsonx_ai_api_key']:
            if parameters['runtime_env_apsx_url'] and parameters['runtime_env_apsx_url'].endswith("cloud.ibm.com"):
                runtime_region = parameters['runtime_env_region']
                wml_credentials = {
                        "apikey": parameters['watsonx_ai_api_key'],
                        "url": f"https://{runtime_region}.ml.cloud.ibm.com"
                        }
            else:
                wml_credentials = {
                    "token": parameters['user_access_token'],
                    "instance_id" : "openshift",
                    "url": parameters['runtime_env_apsx_url']
                }

            client = APIClient(wml_credentials)

            if parameters['watsonx_space_id']:
                client.set.default_space(parameters['watsonx_space_id'])
            logger.info("Initialized IBM watsonx.ai APIClient")
        else:
            logger.warning("WATSONX_API_KEY not set; IBM client not initialized")
        
    except Exception as e:
        logger.exception("Failed to initialize IBM client: %s", e)

    # Initialize governance evaluator
    init_governance_evaluator()

    return client