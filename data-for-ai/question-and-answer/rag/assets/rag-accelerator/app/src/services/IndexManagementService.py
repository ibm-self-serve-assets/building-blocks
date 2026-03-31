import os
import logging
from dotenv import load_dotenv

from app.src.utils import rag_helper_functions
from app.src.utils import config
from app.src.utils.connection_factory import ConnectionFactory
from app.src.utils.milvus_ops import MilvusOperations
from app.src.utils.opensearch_ops import OpenSearchOperations

# Load environment variables
load_dotenv()

# Logging configuration controlled via .env
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("index_management_service")

# Get parameters from config
parameter_sets = config.PARAMETERS
parameter_sets_list = list(parameter_sets.keys())
parameters = rag_helper_functions.get_parameter_sets(parameter_sets_list)
logger.debug("Loaded IndexManagementService parameters successfully")


def connection_setup(connection_name: str):
    """
    Setup connection based on connection_name.
    Supports both 'milvus_connect' and 'opensearch_connect'.
    """
    logger.debug("Initializing connection with connection_name=%s", connection_name)

    if connection_name not in ["milvus_connect", "opensearch_connect"]:
        raise ValueError(f"Unsupported connection: {connection_name}. Supported: milvus_connect, opensearch_connect")

    connection = ConnectionFactory.create_connection(connection_name, parameters)
    client, connection_args = connection.connect()
    logger.info(f"{connection_name} connection established")

    return client, connection_args


def list_indices(payload: dict):
    """
    List all indices/collections based on connection type.
    Supports both Milvus and OpenSearch based on connection_name.
    
    Args:
        payload: Dictionary containing connection_name
        
    Returns:
        List of index/collection names
    """
    logger.info("Listing indices/collections")
    logger.debug("Payload received: %s", payload)

    connection_name = payload.get("connection_name")

    if not connection_name:
        raise ValueError("connection_name is required")

    # Setup connection dynamically based on connection_name
    logger.info(f"Setting up {connection_name} connection for listing indices")
    client, connection_args = connection_setup(connection_name)
    logger.debug(f"{connection_name} connection args: %s", connection_args)

    try:
        # List indices based on connection type
        if connection_name == "milvus_connect":
            milvus_ops = MilvusOperations(client=client, parameters=parameters)
            indices = milvus_ops.list_collections()
            logger.info(f"Found {len(indices)} Milvus collections")
            return indices
            
        elif connection_name == "opensearch_connect":
            opensearch_ops = OpenSearchOperations(client=client, parameters=parameters)
            indices = opensearch_ops.list_indices()
            logger.info(f"Found {len(indices)} OpenSearch indices")
            return indices
            
        else:
            raise ValueError(f"Unsupported connection: {connection_name}")

    except Exception as e:
        logger.exception(f"Failed to list indices: {e}")
        raise


def delete_index(payload: dict):
    """
    Delete an index/collection based on connection type.
    Supports both Milvus and OpenSearch based on connection_name.
    
    Args:
        payload: Dictionary containing connection_name and index_name
        
    Returns:
        None
    """
    logger.info("Deleting index/collection")
    logger.debug("Payload received: %s", payload)

    connection_name = payload.get("connection_name")
    index_name = payload.get("index_name")

    if not connection_name:
        raise ValueError("connection_name is required")
    
    if not index_name:
        raise ValueError("index_name is required")

    # Setup connection dynamically based on connection_name
    logger.info(f"Setting up {connection_name} connection for deleting index")
    client, connection_args = connection_setup(connection_name)
    logger.debug(f"{connection_name} connection args: %s", connection_args)

    try:
        # Delete index based on connection type
        if connection_name == "milvus_connect":
            milvus_ops = MilvusOperations(client=client, parameters=parameters)
            milvus_ops.delete_collection(index_name=index_name)
            logger.info(f"Successfully deleted Milvus collection: {index_name}")
            
        elif connection_name == "opensearch_connect":
            opensearch_ops = OpenSearchOperations(client=client, parameters=parameters)
            opensearch_ops.delete_index(index_name=index_name)
            logger.info(f"Successfully deleted OpenSearch index: {index_name}")
            
        else:
            raise ValueError(f"Unsupported connection: {connection_name}")

    except Exception as e:
        logger.exception(f"Failed to delete index '{index_name}': {e}")
        raise

# Made with Bob
