import logging
from dotenv import load_dotenv

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Embeddings

from app.src.utils import rag_helper_functions
from app.src.utils import config
from app.src.utils.milvus_connection import MilvusConnection
from app.src.utils.connection_factory import ConnectionFactory
from langchain.vectorstores import Milvus
import os


load_dotenv()


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("query_service")

# Load parameters
parameter_sets = config.PARAMETERS
parameter_sets_list = list(parameter_sets.keys())
parameters = rag_helper_functions.get_parameter_sets(parameter_sets_list)

logger.debug("Loaded QueryService parameters successfully")

environment = parameters["environment"]
project_id = parameters["watsonx_project_id"]


def connection_setup(connection_name: str):
    """
    Only milvus_connect supported
    """

    if connection_name != "milvus_connect":
        raise ValueError("Only milvus_connect is supported")

    connection = ConnectionFactory.create_connection("milvus_connect",parameters)
    client, connection_args = connection.connect()

    return client, connection_args

# Connect to Milvus
logger.info("Setting up connection to Milvus")
milvus_client, milvus_connection_args = connection_setup("milvus_connect")
logger.debug("Milvus connection args: %s", milvus_connection_args)
logger.info("Connection to Milvus established")

### embedding from watsonx.ai
def get_embedding():
    logger.debug("Initializing embedding model for QueryService")
    if environment != "cloud":
        raise ValueError("Only cloud environment supported")

    credentials = Credentials(
        api_key=parameters["watsonx_ai_api_key"],
        url=parameters["watsonx_url"],
    )

    model_id = parameters["embedding_model_id"]

    embedding = Embeddings(
        model_id=model_id,
        credentials=credentials,
        project_id=project_id,
        verify=True,
    )

    model_id_lower = model_id.lower()

    if "e5" in model_id_lower:
        model_config = {
            "max_tokens": 512,
            "prefix": "passage: ",
        }
    else:
        model_config = {
            "max_tokens": 8000,
            "prefix": "",
        }

    logger.debug("Embedding model_id: %s", model_id)
    test_vector = embedding.embed_documents(["test"])[0]
    embedding_dim = len(test_vector)

    return embedding


def search_milvus(index_name: str, question: str, top_k: int = 5):
    """
    Dense search only using Milvus (L2 + IVF_FLAT)
    """
    logger.info("Milvus search started")
    logger.debug("Search parameters: index_name=%s, top_k=%s", index_name, top_k)
    try:
        embedding = get_embedding()

        """
        dense_index_param = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024},
        }
        """

        hybrid_search = (parameters.get("milvus_hybrid_search", "false").lower()== "true")
        logger.debug("Hybrid search enabled: %s", hybrid_search)

        if hybrid_search:
            vector_field_name = "dense"
        else:
            vector_field_name = "vector"

        logger.info(f"Index name: {index_name} and question: {question}")

        logger.info("Initializing Milvus vector store...")
        vector_store = Milvus(
            embedding_function=embedding,
            #index_params=dense_index_param,
            vector_field=vector_field_name,
            connection_args=milvus_connection_args,
            primary_field="id",
            consistency_level="Strong",
            collection_name=index_name,
        )

        logger.info("Performing similarity search in Milvus...")

        if parameters["vectorsearch_top_n_results"]:
            top_k = int(parameters["vectorsearch_top_n_results"])
        
        logger.info("Performing similarity search in Milvus")
        search_result = vector_store.similarity_search_with_score(
            question,
            k=top_k
        )
        logger.debug("Search result: %s", search_result)
        return search_result

    except Exception as e:
        logger.exception("Milvus search failed: %s", e)
        raise


def generate_answer(payload: dict):
    """
    Called from /query route
    """

    logger.info("Generating answer for query")
    logger.debug("Payload received: %s", payload)

    question = payload["query"]
    index_name = payload["index_name"]

    # Perform search
    search_result = search_milvus(index_name, question)

    if not search_result:
        return [], "No relevant documents found."

    # Format results
    formatted_results = []

    for doc, score in search_result:
        formatted_results.append({
            "text": doc.page_content,
            "metadata": doc.metadata,
            "score": score
        })

    logger.debug("Formatted results count: %s", len(formatted_results))
    top_result = formatted_results[0]["text"]

    logger.info("Answer generation completed")
    return formatted_results, top_result