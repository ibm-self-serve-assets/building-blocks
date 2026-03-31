import os
import shutil
import warnings
import logging
import hashlib
from tqdm import tqdm

from dotenv import load_dotenv
from pymilvus import MilvusClient

from app.src.utils import rag_helper_functions
from app.src.utils.cos_ops import COSOperations
from app.src.utils import config
from app.src.utils.ingestion_helper import DocumentProcessor
from app.src.utils.milvus_ops import MilvusOperations
from app.src.utils.opensearch_ops import OpenSearchOperations
from app.src.utils.milvus_connection import MilvusConnection
from app.src.utils.connection_factory import ConnectionFactory
from app.src.utils.embeddings.factory import EmbeddingFactory
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging configuration controlled via .env
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("ingest_service")

# Get parameters from config
parameter_sets = config.PARAMETERS
parameter_sets_list = list(parameter_sets.keys())
parameters=rag_helper_functions.get_parameter_sets(parameter_sets_list)
logger.debug("Loaded ingestion parameters successfully")


environment = parameters["environment"]
ibm_api_key = parameters["watsonx_ai_api_key"]
project_id = parameters["watsonx_project_id"]

index_chunk_size = int(parameters["index_chunk_size"])
chunk_size = int(parameters["chunk_size"])
chunk_overlap = int(parameters["chunk_overlap"])


def connection_setup(connection_name):
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

# Initialize connections lazily - will be set up when needed
milvus_client = None
milvus_connection_args = None
opensearch_client = None
opensearch_connection_args = None


def get_embedding(environment: str, parameters: dict, project_id: str):
    """
    Returns:
        embedding instance
        model_config dict (max_tokens, prefix)
        embedding_dimension
    """
    logger.debug("Initializing embedding model using EmbeddingFactory")
    
    # Get embedding provider from parameters
    embedding_provider = parameters.get("embedding_provider", "watsonx")
    
    # Add device and local model path for non-watsonx providers
    if embedding_provider in ["huggingface", "local"]:
        parameters["device"] = parameters.get("device", "cpu")
        parameters["local_model_path"] = parameters.get("local_model_path", "")
        parameters["cache_folder"] = parameters.get("cache_folder", "")
    
    # Create embedding instance using factory
    embedding = EmbeddingFactory.create_embedding(embedding_provider, parameters)
    
    # Get model configuration and dimension
    model_config = embedding.get_model_config()
    embedding_dim = embedding.get_embedding_dimension()
    
    logger.debug("Embedding model config: %s", model_config)
    logger.info("Embedding dimension detected: %s", embedding_dim)

    return embedding, model_config, embedding_dim

def generate_hash(content):
    return hashlib.sha256(content.encode()).hexdigest()

def insert_docs_to_milvus(client, collection_name, split_docs, embedding, model_config):
    """Insert documents into Milvus collection."""
    with tqdm(total=len(split_docs), desc="Inserting Documents into Milvus", unit="docs") as pbar:

        try:
            logger.info("Starting document insertion into Milvus collection '%s'", collection_name)
            logger.debug("Total split_docs received: %s", len(split_docs))

            for i in range(0, len(split_docs), index_chunk_size):
                logger.debug("Processing chunk batch from %s to %s", i, i + index_chunk_size)
                chunk = split_docs[i:i + index_chunk_size]
                texts = []
                valid_docs = []

                for doc in chunk:
                    # Use embedding's format_text method
                    formatted_text = embedding.format_text(doc.page_content)
                    texts.append(formatted_text)
                    valid_docs.append(doc)

                try:
                    vectors = embedding.embed_documents(texts)
                except Exception as e:
                    logger.warning(f"Embedding batch failed. Skipping batch. Error: {e}")
                    pbar.update(len(chunk))
                    continue

                data = []

                for doc, vector in zip(valid_docs, vectors):

                    doc_id = generate_hash(
                        doc.page_content +
                        '\nTitle: ' + doc.metadata.get('title', '') +
                        '\nUrl: ' + doc.metadata.get('document_url', '') +
                        '\nPage: ' + str(doc.metadata.get('page_number', ''))
                    )

                    data.append({
                        "id": doc_id,
                        "vector": vector,
                        "title": doc.metadata.get("title", ""),
                        "source": doc.metadata.get("source", ""),
                        "document_url": doc.metadata.get("document_url", ""),
                        "page_number": str(doc.metadata.get("page_number", "")),
                        "chunk_seq": int(doc.metadata.get("chunk_seq", 0)),
                        "text": doc.page_content,
                    })

                if data:
                    client.insert(
                        collection_name=collection_name,
                        data=data
                    )
                    logger.info("Inserted %s documents into Milvus collection '%s'", len(data), collection_name)

                pbar.update(len(chunk))

            logger.info("Documents inserted into Milvus successfully")

        except Exception as e:
            logger.exception(f"Ingestion error: {e}")
            raise


def insert_docs_to_opensearch(client, index_name, split_docs, embedding, model_config):
    """Insert documents into OpenSearch index."""
    with tqdm(total=len(split_docs), desc="Inserting Documents into OpenSearch", unit="docs") as pbar:

        try:
            logger.info("Starting document insertion into OpenSearch index '%s'", index_name)
            logger.debug("Total split_docs received: %s", len(split_docs))

            for i in range(0, len(split_docs), index_chunk_size):
                logger.debug("Processing chunk batch from %s to %s", i, i + index_chunk_size)
                chunk = split_docs[i:i + index_chunk_size]
                texts = []
                valid_docs = []

                for doc in chunk:
                    # Use embedding's format_text method
                    formatted_text = embedding.format_text(doc.page_content)
                    texts.append(formatted_text)
                    valid_docs.append(doc)

                try:
                    vectors = embedding.embed_documents(texts)
                except Exception as e:
                    logger.warning(f"Embedding batch failed. Skipping batch. Error: {e}")
                    pbar.update(len(chunk))
                    continue

                # Bulk insert into OpenSearch
                bulk_data = []
                for doc, vector in zip(valid_docs, vectors):

                    doc_id = generate_hash(
                        doc.page_content +
                        '\nTitle: ' + doc.metadata.get('title', '') +
                        '\nUrl: ' + doc.metadata.get('document_url', '') +
                        '\nPage: ' + str(doc.metadata.get('page_number', ''))
                    )

                    # OpenSearch bulk format: action and source
                    bulk_data.append({"index": {"_index": index_name, "_id": doc_id}})
                    bulk_data.append({
                        "id": doc_id,
                        "vector": vector,
                        "title": doc.metadata.get("title", ""),
                        "source": doc.metadata.get("source", ""),
                        "document_url": doc.metadata.get("document_url", ""),
                        "page_number": str(doc.metadata.get("page_number", "")),
                        "chunk_seq": int(doc.metadata.get("chunk_seq", 0)),
                        "text": doc.page_content,
                    })

                if bulk_data:
                    # Bulk insert
                    response = client.bulk(body=bulk_data, refresh=True)
                    if response.get("errors"):
                        logger.warning("Some documents failed to index in OpenSearch")
                    else:
                        logger.info("Inserted %s documents into OpenSearch index '%s'", len(valid_docs), index_name)

                pbar.update(len(chunk))

            logger.info("Documents inserted into OpenSearch successfully")

        except Exception as e:
            logger.exception(f"Ingestion error: {e}")
            raise

def ingest_files(payload):

    """
    Ingest data from COS into vector database.
    Supports both Milvus and OpenSearch based on connection_name.
    """

    logger.info("Starting ingestion process")
    logger.debug("Ingestion payload: %s", payload)

    connection_name = payload['connection_name']
    bucket_name = payload["bucket_name"]
    directory = payload["directory"]
    index_name = payload["index_name"]
    local_directory = None  # Initialize to track for cleanup

    try:

        if bucket_name is None:
            logger.error("Bucket name is required for COS ingestion")
            raise ValueError("Bucket name is required for COS ingestion")
        
        if directory is None:
            logger.error("Directory (prefix) is required for COS ingestion")
            raise ValueError("Directory (prefix) is required for COS ingestion")
        
        if index_name is None:
            logger.error("Index name is required for vector database ingestion")
            raise ValueError("Index name is required for vector database ingestion")
        
        if connection_name not in ["milvus_connect", "opensearch_connect"]:
            logger.error(f"Unsupported connection: {connection_name}")
            raise ConnectionError(f"Unsupported connection: {connection_name}. Supported: milvus_connect, opensearch_connect")

        # Setup connection dynamically based on connection_name
        logger.info(f"Setting up {connection_name} connection")
        client, connection_args = connection_setup(connection_name)
        logger.debug(f"{connection_name} connection args: %s", connection_args)

        # COS Operations download files from prefix
        cos_ops = COSOperations(bucket_name=bucket_name)

        filtered_keys = cos_ops.get_filtered_keys(prefix=directory)
        logger.info("Number of files found in COS: %s", len(filtered_keys))

        if not filtered_keys:
            logger.warning(f"No files found under prefix: {directory}")
            return 0

        local_directory = os.path.join("downloads", index_name)

        documents_info = cos_ops.download_files(
            keys=filtered_keys,
            local_directory=local_directory
        )

        logger.debug("Downloaded documents info: %s", documents_info)

        # Process documents
        logger.info("Processing documents")

        processor_params = {
            "include_all_html_tags": "false",
            "ingestion_chunk_size": chunk_size,
            "ingestion_chunk_overlap": chunk_overlap
        }

        processor = DocumentProcessor(processor_params)

        split_docs = processor.process_directory(
            directory=local_directory,
            rag_helper_functions=rag_helper_functions or {}
        )
        
        
        doc_length = len(split_docs)
        logger.info("Total split documents: %s", doc_length)

        # Get embeddings
        embedding, model_config, embedding_dim = get_embedding(environment, parameters, project_id)

        # Create index/collection & Insert chunks based on connection type
        if connection_name == "milvus_connect":

            logger.info("Processing Milvus ingestion")
            milvus_ops = MilvusOperations(client=client, parameters=parameters)

            logger.debug("Creating Milvus collection: %s", index_name)
            milvus_ops.create_collection(embedding_dim=embedding_dim, index_name=index_name)

            logger.info("Inserting documents into Milvus")
            insert_docs_to_milvus(client=client, collection_name=index_name, split_docs=split_docs,
                embedding=embedding, model_config=model_config)

            # Cleanup: Remove local directory after successful ingestion
            if os.path.exists(local_directory):
                shutil.rmtree(local_directory)
                logger.info(f"Cleaned up local directory: {local_directory}")

            return doc_length

        elif connection_name == "opensearch_connect":

            logger.info("Processing OpenSearch ingestion")
            opensearch_ops = OpenSearchOperations(client=client, parameters=parameters)

            logger.debug("Creating OpenSearch index: %s", index_name)
            opensearch_ops.create_index(embedding_dim=embedding_dim, index_name=index_name)

            logger.info("Inserting documents into OpenSearch")
            insert_docs_to_opensearch(client=client, index_name=index_name, split_docs=split_docs,
                embedding=embedding, model_config=model_config)

            # Cleanup: Remove local directory after successful ingestion
            if os.path.exists(local_directory):
                shutil.rmtree(local_directory)
                logger.info(f"Cleaned up local directory: {local_directory}")

            return doc_length

        else:
            logger.error(f"Unsupported connection: {connection_name}")
            raise ValueError(f"Unsupported connection: {connection_name}")

    except Exception as e:
        logger.exception(
            f"Failed to ingest data in vector database. Please check logs {e}"
        )
        # Cleanup: Remove local directory even on failure to avoid leaving orphaned files
        if local_directory and os.path.exists(local_directory):
            try:
                shutil.rmtree(local_directory)
                logger.info(f"Cleaned up local directory after error: {local_directory}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup local directory: {cleanup_error}")
        raise