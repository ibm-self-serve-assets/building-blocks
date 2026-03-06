import os
import shutil
import warnings
import logging
import hashlib
from tqdm import tqdm

from dotenv import load_dotenv
from pymilvus import MilvusClient

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Embeddings

from app.src.utils import rag_helper_functions
from app.src.utils.cos_ops import COSOperations
from app.src.utils import config
from app.src.utils.ingestion_helper import DocumentProcessor
from app.src.utils.milvus_ops import MilvusOperations
from app.src.utils.milvus_connection import MilvusConnection
from app.src.utils.connection_factory import ConnectionFactory
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
    if connection_name != "milvus_connect":
        raise ValueError(f"Unsupported connection: {connection_name}")

    """ logger.info("Connecting to Milvus")

    db_connection = {
        "uri": f"https://{parameters["milvus_host"]}:{parameters["milvus_port"]}",  
        "token": f"{parameters['milvus_user']}:{parameters['milvus_password']}",
        "database": parameters.get("milvus_database", "default"),
        "secure": parameters["milvus_ssl"].lower() == "true"
    }

    client = MilvusClient(**db_connection)

    logger.info("MilvusClient connection established")
    return client """

    logger.debug("Initializing Milvus connection with connection_name=%s", connection_name)

    if connection_name != "milvus_connect":
        raise ValueError("Only milvus_connect is supported")

    connection = ConnectionFactory.create_connection("milvus_connect",parameters)
    client, connection_args = connection.connect()
    logger.info("MilvusClient connection established")

    return client, connection_args

# Connect to Milvus
logger.info("Setting up connection to Milvus")
milvus_client, milvus_connection_args = connection_setup("milvus_connect")
logger.debug("Milvus connection args: %s", milvus_connection_args)
logger.info("Connection to Milvus established")


def ensure_token_limit(text: str, max_tokens: int) -> str:
    """
    Lightweight token limiter using whitespace split.
    Keeps ingestion safe from model max token violations.
    """
    words = text.split()
    if len(words) > max_tokens:
        return " ".join(words[:max_tokens])
    return text

def get_embedding(environment: str, parameters: dict, project_id: str):
    """
    Returns:
        embedding instance
        model_config dict (max_tokens, prefix)
        embedding_dimension
    """
    logger.debug("Initializing embedding model")
    if environment != "cloud":
        raise ValueError("Only cloud environment is supported")

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

    logger.debug("Embedding model config: %s", model_config)
    test_vector = embedding.embed_documents(["test"])[0]
    embedding_dim = len(test_vector)
    logger.info("Embedding dimension detected: %s", embedding_dim)

    return embedding, model_config, embedding_dim

def generate_hash(content):
    return hashlib.sha256(content.encode()).hexdigest()

def insert_docs_to_milvus(collection_name, split_docs, embedding, model_config):
    max_tokens = model_config["max_tokens"]
    prefix = model_config["prefix"]

    with tqdm(total=len(split_docs), desc="Inserting Documents", unit="docs") as pbar:

        try:
            logger.info("Starting document insertion into Milvus collection '%s'", collection_name)
            logger.debug("Total split_docs received: %s", len(split_docs))

            for i in range(0, len(split_docs), index_chunk_size):
                logger.debug("Processing chunk batch from %s to %s", i, i + index_chunk_size)
                chunk = split_docs[i:i + index_chunk_size]
                texts = []
                valid_docs = []

                for doc in chunk:
                    safe_text = ensure_token_limit(
                        doc.page_content,
                        max_tokens - 20  # safety margin
                    )

                    formatted_text = f"{prefix}{safe_text}"

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
                    milvus_client.insert(
                        collection_name=collection_name,
                        data=data
                    )
                    logger.info("Inserted %s documents into Milvus collection '%s'", len(data), collection_name)

                pbar.update(len(chunk))

            logger.info("Documents inserted into Milvus successfully")

        except Exception as e:
            logger.exception(f"Ingestion error: {e}")
            raise

def ingest_files(payload):

    """
    Ingest data from COS into vector database
    """

    logger.info("Starting ingestion process")
    logger.debug("Ingestion payload: %s", payload)

    connection_name = payload['connection_name']
    bucket_name = payload["bucket_name"]
    directory = payload["directory"]   
    index_name = payload["index_name"]

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
        
        if connection_name != "milvus_connect":
            logger.error("currently only milvus connection is supported")
            raise ConnectionError("currently only milvus connection is supported")

        milvus_ops = None

        milvus_ops = MilvusOperations(client=milvus_client, parameters=parameters)

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

        # Create milvus collection & Insert chunks
        if connection_name == "milvus_connect":

            embedding, model_config, embedding_dim = get_embedding( environment, parameters, project_id)

            logger.debug("Creating Milvus collection: %s", index_name)
            milvus_ops.create_collection( embedding_dim=embedding_dim, index_name=index_name)

            logger.info("Inserting documents into Milvus")

            logger.info("Inserting documents into Milvus")
            insert_docs_to_milvus(collection_name=index_name, split_docs=split_docs,
                embedding=embedding, model_config=model_config)

            return doc_length

        else:
            logger.error(f"Unsupported connection: {connection_name}")
            raise ValueError(f"Unsupported connection: {connection_name}")

    except Exception as e:
        logger.exception(
            f"Failed to ingest data in vector database. Please check logs {e}"
        )
        raise