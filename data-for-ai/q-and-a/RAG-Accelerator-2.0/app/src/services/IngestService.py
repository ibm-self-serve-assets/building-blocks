from ibm_watsonx_ai import APIClient
import os
import shutil
import warnings
warnings.filterwarnings("ignore")
from app.src.utils import rag_helper_functions
from app.src.utils.COSConnector import COSService
from app.src.utils import config
from app.src.utils.ingestion_helper import DocumentProcessor
from pymilvus import(FieldSchema,DataType,Collection,CollectionSchema,utility,Function,FunctionType)
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create a logger
logger = logging.getLogger(__name__)

# Get parameters from config
parameter_sets = config.PARAMETERS
parameter_sets_list = list(parameter_sets.keys())
parameters=rag_helper_functions.get_parameter_sets(parameter_sets_list)

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Embeddings
from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames as EmbedParams
from ibm_watsonx_ai.foundation_models.utils.enums import EmbeddingTypes
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai import APIClient
import hashlib
import os

import shutil 
import warnings
from tqdm import tqdm


from pymilvus import(FieldSchema,DataType,Collection,CollectionSchema,utility)
from langchain_milvus import BM25BuiltInFunction
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv()

environment = parameters["environment"]
wml_service_url = parameters["watsonx_url"]
ibm_api_key = parameters["watsonx_ai_api_key"]
project_id = parameters["watsonx_project_id"]
wml_credentials = {"apikey": ibm_api_key, "url": wml_service_url}

index_chunk_size = int(parameters["index_chunk_size"])
chunk_size = int(parameters["chunk_size"])
chunk_overlap = int(parameters["chunk_overlap"])


def init_environment():

    client = APIClient(wml_credentials)
    client.set.default_project(project_id)
    return client

client = init_environment()

def connection_setup(connection_name):
    """
    Get the milvus data source credentails or connect to elastic search instance.

    Parameters:
    - connection_name (str): Name of the connection
  

    Returns:
    - milvus credentials (dict)/ es_client(client instance) and connection_type (str).
    """

    connection_list = ['milvus_connect','elasticsearch_connect','datastax_connect']
    if(next((conn for conn in connection_list if conn == connection_name), None)):
        print(connection_name, "Connection found in the project")

        connections = client.connections.get_details()
            
        ids = [resource['metadata']['id'] for resource in connections['resources'] if resource['entity']['name'] == connection_name]
        connection_id = ids[0]
        db_connection = client.connections.get_details(connection_id)['entity']['properties']
        # Create the Elasticsearch client instance
        logger.info("Reading from the connection..")
        ssl_certificate_content = db_connection.get('ssl_certificate') if db_connection.get('ssl_certificate') else ""
        connection_datatypesource_id = [resource['entity']['datasource_type'] for resource in connections['resources'] if resource['entity']['name'] == connection_name]
        connection_type = client.connections.get_datasource_type_details_by_id(connection_datatypesource_id[0])['entity']['name']
        
        logger.info("Successfully retrieved the connection details")
        logger.info(f"Connection type is identified as:{connection_type}")
    
        if connection_type=="elasticsearch":
            print('connection check', parameters['elastic_search_model_id'])
            es_client=rag_helper_functions.create_and_check_elastic_client(db_connection, parameters['elastic_search_model_id'])
            return es_client, connection_type
        elif connection_type=="milvus" or connection_type=="milvuswxd":
            milvus_credentials = rag_helper_functions.connect_to_milvus_database(db_connection, parameters)
            return milvus_credentials, connection_type
        # datastax is not tested 
        elif connection_type=="datastax" or connection_type=="datastax-astradb":
            if connection_type=="datastax-astradb":
                datastax_session,datastax_cluster = rag_helper_functions.connect_to_astradb_using_cassandra(db_connection, parameters)
            else:
                datastax_session,datastax_cluster = rag_helper_functions.connect_to_datastax(db_connection, parameters)
            import cassio
            cassio.init(session=datastax_session, keyspace=db_connection.get('keyspace'))
    else:
        db_connection=""
        raise ValueError(f"No connection named {connection_name} found in the project.")

        

def get_embedding(environment, parameters, project_id, wml_credentials, WML_SERVICE_URL):

    if environment=="cloud":
        try:
            credentials=Credentials(
                api_key = parameters['watsonx_ai_api_key'],
                url = wml_service_url)
            embedding = Embeddings(
            model_id=parameters['embedding_model_id'],
            credentials=credentials,
            project_id=project_id,
            verify=True
            )
        except Exception as e:
            logger.error("Exception in loading Embedding Models:" + str(e))
            raise
        
    elif environment == "on-prem":
        try:
            if client.foundation_models.EmbeddingModels.__members__:
                if client.foundation_models.EmbeddingModels(parameters["embedding_model_id"]).name:
                    embedding = Embeddings(
                        model_id=parameters['embedding_model_id'],
                        credentials=wml_credentials,
                        project_id=project_id,
                        verify=True
                    )
                else:
                    print(f"Encoder model {parameters['embedding_model_id']} not found on the cluster. Please update embedding model_id param to a model which exists or deploy missing model on this cluster")
            else:
                print("Local on-prem embedding models not found, using models from IBM Cloud API if required parameters are provided")
                credentials = Credentials(
                    api_key=parameters['watsonx_ai_api_key'],
                    url=parameters['watsonx_ai_url']
                )
                embedding = Embeddings(
                    model_id=parameters['embedding_model_id'],
                    credentials=credentials,
                    space_id=parameters["wx_ai_inference_space_id"],
                    verify=True
                )
        except Exception as e:
            print(f"Exception in loading Embedding Models: {str(e)}")
            raise
    else:
        raise ValueError(f"Invalid environment: {environment}. Must be 'cloud' or 'on-prem'.")
    
    return embedding

def create_collection(index_name):
    if environment=="cloud":
        try:
            credentials=Credentials(
                api_key = parameters['watsonx_ai_api_key'],
                url = wml_service_url)
            embedding = Embeddings(
            model_id=parameters['embedding_model_id'],
            credentials=credentials,
            project_id=project_id,
            verify=True
            )
        except Exception as e:
            logger.error("Exception in loading Embedding Models:" + str(e))
            raise   
    elif environment=="on-prem":
        try:
            if client.foundation_models.EmbeddingModels.__members__:
                if client.foundation_models.EmbeddingModels(parameters["embedding_model_id"]).name:
                    embedding = Embeddings(
                      model_id=parameters['embedding_model_id'],
                      credentials=wml_credentials,
                      project_id=project_id,
                      verify=True
                    )
            else:
                print("local on prem embeddng models are not found, using models from IBM Cloud API")
                credentials=Credentials(
                    api_key = parameters['watsonx_ai_api_key'],
                    url =parameters['watsonx_ai_url'])
                embedding = Embeddings(
                  model_id=parameters['embedding_model_id'],
                  credentials=credentials,
                  space_id=parameters["wx_ai_inference_space_id"],
                  verify=True
                )
        except Exception as e:
            print("Exception in loading Embedding Models:" + str(e))
            raise

    embedding_dim = embedding.embed_documents(['a'])[0]

    # Creates/retrieves collection
    try:
        if index_name not in utility.list_collections():
            dense_index_params = {"metric_type": "L2", "index_type": "IVF_FLAT","params": {"nlist": 1024},}
            sparse_index_params = {"metric_type": "BM25","index_type": "SPARSE_INVERTED_INDEX", "params": {"drop_ratio_build": 0.2}}

            hybrid_search = True if parameters['milvus_hybrid_search'].lower()=="true" else False
            if hybrid_search:
                fields = [
                    FieldSchema("id", DataType.VARCHAR, is_primary=True, max_length=65535, auto_id=False),
                    FieldSchema("dense", DataType.FLOAT_VECTOR, dim=len(embedding_dim)),
                    FieldSchema("sparse", DataType.SPARSE_FLOAT_VECTOR),
                    FieldSchema("title", DataType.VARCHAR, max_length=65535),
                    FieldSchema("source", DataType.VARCHAR, max_length=65535),
                    FieldSchema("document_url", DataType.VARCHAR, max_length=65535),
                    FieldSchema("page_number", DataType.VARCHAR, max_length=65535),
                    FieldSchema("chunk_seq", DataType.INT32),
                    FieldSchema("text", DataType.VARCHAR, max_length=65535, enable_analyzer=True)
                ]
                bm25_func = Function(
                    name=f"bm25_text",
                    function_type=FunctionType.BM25,
                    input_field_names=['text'],
                    output_field_names=['sparse'],
                    )
                coll_schema = CollectionSchema(fields)
                coll_schema.add_function(bm25_func)
                coll = Collection(name=index_name, schema=coll_schema)

                coll.create_index(field_name="dense", index_params=dense_index_params)
                coll.create_index(field_name="sparse", index_params=sparse_index_params)
            else:
                fields = [
                    FieldSchema("id", DataType.VARCHAR, is_primary=True, max_length=65535, auto_id=False),
                    FieldSchema("vector", DataType.FLOAT_VECTOR, dim=len(embedding_dim)),
                    FieldSchema("title", DataType.VARCHAR, max_length=65535),
                    FieldSchema("source", DataType.VARCHAR, max_length=65535),
                    FieldSchema("document_url", DataType.VARCHAR, max_length=65535),
                    FieldSchema("page_number", DataType.VARCHAR, max_length=65535),
                    FieldSchema("chunk_seq", DataType.INT32),
                    FieldSchema("text", DataType.VARCHAR, max_length=65535)
                ]
                coll_schema = CollectionSchema(fields)
                coll = Collection(name=index_name, schema=coll_schema)
            
                coll.create_index(field_name="vector", index_params=dense_index_params)
                
            logger.info('Milvus collection is created!')
        else:
            coll = Collection(name=index_name)
            logger.info('Milvus collection is retrieved!')

        return coll
    
    except Exception as e:  
        logger.error(f"Error while creating or retreiving collection {e}")
        raise
    

def create_vector_store(es_client,milvus_credentials,connection_type,index_name,parameters):
    try:
        if connection_type=="elasticsearch":
            from langchain_elasticsearch import ElasticsearchStore
            if 'dense' in parameters['elastic_search_vector_type']:
                vector_store=ElasticsearchStore(
                                es_connection=es_client,
                                index_name=index_name,
                                strategy=ElasticsearchStore.ApproxRetrievalStrategy(query_model_id=parameters['elastic_search_model_id']),
                                )
            else:
                vector_store=ElasticsearchStore(
                                es_connection=es_client,
                                index_name=index_name,
                                strategy=ElasticsearchStore.SparseVectorRetrievalStrategy(model_id=parameters['elastic_search_model_id']),
                                custom_index_settings={"number_of_shards": parameters["es_number_of_shards"]}
                                )
            logger.info(f"Elastic Search Vector Store Created with{parameters['elastic_search_model_id']}")
        elif connection_type=="milvus" or connection_type=="milvuswxd":
            from langchain_milvus import Milvus
            print("using the model",parameters['embedding_model_id'], "to create embeddings")
            embedding = get_embedding(environment, parameters, project_id, wml_credentials, wml_service_url) if environment == "cloud" else get_embedding(environment, parameters, project_id, wml_credentials, None)  
        
            dense_index_param = {"metric_type": "L2", "index_type": "IVF_FLAT","params": {"nlist": 1024},}
            sparse_index_param = {"metric_type": "BM25","index_type": "SPARSE_INVERTED_INDEX", "params": {"drop_ratio_build": 0.2}}

            hybrid_search = True if parameters['milvus_hybrid_search'].lower()=="true" else False
            if hybrid_search:
                print("Adding sparse and Dense embeddings")
                vector_store = Milvus(
                embedding_function=embedding,
                builtin_function=BM25BuiltInFunction(output_field_names="sparse"), 
                index_params=[dense_index_param, sparse_index_param],
                vector_field=["dense", "sparse"],
                connection_args=milvus_credentials,
                primary_field='id',
                consistency_level="Strong",
                collection_name=index_name
                )
            else:
                print("Adding Dense embeddings")
                vector_store = Milvus(
                    embedding_function=embedding,
                    index_params=dense_index_param,
                    connection_args=milvus_credentials,
                    primary_field='id',
                    consistency_level="Strong",
                    collection_name=index_name
                )
            logger.info("Milvus Vector Store Created")

        elif connection_type == "datastax" or connection_type=="datastax-astradb":
            print("using the model",parameters['embedding_model_id'], "to create embeddings")
            embedding = get_embedding(environment, parameters, project_id, wml_credentials,wml_service_url) if environment == "cloud" else get_embedding(environment, parameters, project_id, wml_credentials, None)  
            from langchain_community.vectorstores import Cassandra
            vector_store = Cassandra(
                embedding=embedding,
                table_name=index_name
            )
            logger.info("Datastax Vector Store Created")

        return vector_store
    
    except Exception as e:
        logger.error(f"Error while creating vector store {e}")
        raise
        

def generate_hash(content):
    return hashlib.sha256(content.encode()).hexdigest()


def insert_docs_to_vector_store(vector_store,split_docs,insert_type="docs"):
    with tqdm(total=len(split_docs), desc="Inserting Documents", unit="docs") as pbar:
        try:
            for i in range(0, len(split_docs), index_chunk_size):
                chunk = split_docs[i:i + index_chunk_size]
                if insert_type=="docs":
                    id_chunk = [generate_hash(doc.page_content+'\nTitle: '+doc.metadata['title']+'\nUrl: '+doc.metadata['document_url']+'\nPage: '+doc.metadata['page_number']) for doc in chunk]
                elif insert_type=="profiles":
                    id_chunk = [generate_hash(doc.page_content) for doc in chunk]
                vector_store.add_documents(chunk, ids=id_chunk)
                pbar.update(len(chunk))
            logger.info("Documents are inserted into vector database")
        except Exception as e:
            logger.error(f"An error occurred during  data ingestion: {e}")
            raise
        
        

def ingest_files(payload):

    """
    Ingest data from cos into vector database

    Parameters:
    - payload (dict): It contains connection_name,bucket_name,directory and index_name

    Returns:
    - doc_length (int): split documents count
    """
    connection_name = payload['connection_name']
    bucket_name = payload['bucket_name']
    directory = payload["directory"]
    index_name = payload["index_name"] 
    
    try:
        
        es_client = None
        milvus_credentials = None
        
        # Connect to vector database
        if connection_name == "milvus_connect":
            logger.info("Connecting to milvus")
            milvus_credentials, connection_type = connection_setup(connection_name)
                    
        if connection_name == "elasticsearch_connect":
            logger.info("Connecting to elastic search")
            es_client, connection_type = connection_setup(connection_name)
     
        logger.info(f"Downloading files from COS bucket: {bucket_name}")
        cos_service = COSService(bucket_name=bucket_name)
        documents_info = cos_service.get_all_objects_from_cos(download_files=True)
        
        # Create download directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)

        # Copy files to local directory
        logger.info(f"Copying files to local directory: {directory}")
        for doc in documents_info:
            source_path = doc['full_path']
            if os.path.isfile(source_path):
                dest_path = os.path.join(directory, os.path.basename(source_path))
                shutil.copy2(source_path, dest_path)
            else:
                logger.info(f"File not found: {source_path}")
                
        # Process documents
        logger.info("Processing documents")
        processor_params = {
            "include_all_html_tags": "false",
            "ingestion_chunk_size": chunk_size,
            "ingestion_chunk_overlap": chunk_overlap
        }

        processor = DocumentProcessor(processor_params)
        
        split_docs = processor.process_directory(
            directory=directory,
            rag_helper_functions=rag_helper_functions or {}
        )
        
        logger.info(len(split_docs))
        
        doc_length = len(split_docs)
        
        # Create collection/index
        
        if connection_type=="milvus" or connection_type=="milvuswxd":
            logger.info("Creating milvus collection")
            create_collection(index_name)
                    
        if connection_type=="elasticsearch":
            try:
                es_client.options(ignore_status=400).indices.create(
                        index=index_name,
                        mappings={
                            'properties': {
                                'vector.tokens': {
                                    'type': 'sparse_vector' if 'sparse' in parameters['elastic_search_vector_type'] else 'dense_vector',
                                },
                            }
                        },
                        settings={
                            'index': {
                                'default_pipeline': 'ingest-pipeline',
                                "mapping.total_fields.limit": 1000000
                            },
                            "number_of_shards": parameters["es_number_of_shards"],
                        }
                    )
                
                es_client.ingest.put_pipeline(
                        id='ingest-pipeline',
                        processors=[
                            {
                                'inference': {
                                    'model_id': parameters['elastic_search_model_id'],
                                    'input_output': [
                                        {
                                            'input_field': 'text',
                                            'output_field': 'vector.tokens',
                                        }
                                    ]
                                }
                            }
                        ]
                    )
                print(f'Elastic search index created with {parameters["elastic_search_model_id"]}!')
            except Exception as e:
                print(f'Error creating index: {e}')
                raise
            
        # Creating a vector store
        logger.info("Creating Vector store")
        vector_store=create_vector_store(es_client,milvus_credentials,connection_type,index_name, parameters)
        
        # Inserting documents into vector store
        logger.info("Inserting Documents into vector store")
        insert_docs_to_vector_store(vector_store,split_docs,"docs")
        
        return doc_length
    
    except Exception as e:
        
        logger.error("Failed to ingest data in vector database. Please check logs.")
        raise
        
    
