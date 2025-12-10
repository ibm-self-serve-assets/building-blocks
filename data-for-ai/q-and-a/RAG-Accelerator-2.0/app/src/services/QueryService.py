from elasticsearch import Elasticsearch, helpers
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Embeddings
from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames as EmbedParams
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai import APIClient
import json
import warnings
warnings.filterwarnings("ignore")
from pymilvus import(IndexType,Status,connections,FieldSchema,DataType,Collection,CollectionSchema,utility)
from dotenv import load_dotenv

from app.src.utils import rag_helper_functions
from app.src.utils import config


# Get parameters from config
parameter_sets = config.PARAMETERS
parameter_sets_list = list(parameter_sets.keys())
parameters=rag_helper_functions.get_parameter_sets(parameter_sets_list)

load_dotenv()  # Load values from .env

environment = parameters['environment'].strip().lower() if parameters['environment'] else "cloud"
runtime_region = parameters['runtime_env_region']
WML_SERVICE_URL = f"https://{runtime_region}.ml.cloud.ibm.com"
ibm_api_key = parameters['watsonx_ai_api_key']
project_id = parameters['watsonx_project_id']
wml_credentials = {"apikey": ibm_api_key, "url": WML_SERVICE_URL}

def init_environment():
    client = APIClient(wml_credentials)
    client.set.default_project(project_id)
    return client

client = init_environment()

# connection_name = "milvus_connect"

def connection_setup(connection_name, question):
    """
    Get the milvius data source credentails or connect to elastic search instance.

    Parameters:
    - connection_name (str): Name of the connection
    - question (str) : user query

    Returns:
    - milvius credentials (dict)/ es_client(client instance) and connection_type (str).
    """
    connection_list = ['milvus_connect','elasticsearch_connect','datastax_connect']
    if(next((conn for conn in connection_list if conn == connection_name), None)):
        print(connection_name, "Connection found in the project")

        connections = client.connections.get_details()
            
        ids = [resource['metadata']['id'] for resource in connections['resources'] if resource['entity']['name'] == connection_name]
        connection_id = ids[0]
        db_connection = client.connections.get_details(connection_id)['entity']['properties']
        # Create the Elasticsearch client instance
        print("Reading from the connection..")
        ssl_certificate_content = db_connection.get('ssl_certificate') if db_connection.get('ssl_certificate') else ""
        connection_datatypesource_id = [resource['entity']['datasource_type'] for resource in connections['resources'] if resource['entity']['name'] == connection_name]
        connection_type = client.connections.get_datasource_type_details_by_id(connection_datatypesource_id[0])['entity']['name']
        
        print("Successfully retrieved the connection details")
        print("Connection type is identified as:",connection_type)

        if connection_type=="elasticsearch":
            print('connection check', parameters['elastic_search_model_id'])
            es_client=rag_helper_functions.create_and_check_elastic_client(db_connection, parameters['elastic_search_model_id'])
            return es_client, connection_type
        elif connection_type=="milvus" or connection_type=="milvuswxd":
            milvus_credentials = rag_helper_functions.connect_to_milvus_database(db_connection, parameters)
            return milvus_credentials, connection_type

        elif connection_type=="datastax" or connection_type=="datastax-astradb":
            if connection_type=="datastax-astradb":
                # wslib.download_file(parameters["astradb_scb_zip_filename"])
                datastax_session,datastax_cluster = rag_helper_functions.connect_to_astradb_using_cassandra(db_connection, parameters)
            else:
                datastax_session,datastax_cluster = rag_helper_functions.connect_to_datastax(db_connection, parameters)
            import cassio
            cassio.init(session=datastax_session, keyspace=db_connection.get('keyspace'))

    else:
        db_connection=""
        raise ValueError(f"No connection named {connection_name} found in the project.")

# Elastic search query template

def search_query_template(connection_type, conn_credentials, index_name, question, parameters):

    """
    Check the connection type and perform search query.

    Parameters:
    - connection_type (str): Type of connection
    - conn_credentials (dict): A dictionary containing the connection parameters for Milvus/Elasticsearch client instance.
    - question (str) : user query
    - parameters (dict): Configuration parameters to perform search operations.

    Returns:
    - search_results (dict): The search results.
    """

    if connection_type=="elasticsearch":
        es_client = conn_credentials
        with open(parameters['elastic_search_template_file']) as f:
            es_query_json = json.load(f)
    
        es_query_str = json.dumps(es_query_json)
        if 'dense' in parameters['elastic_search_vector_type']:
            from langchain_elasticsearch import ElasticsearchEmbeddings
            embeddings = ElasticsearchEmbeddings.from_es_connection(
                        model_id=parameters['elastic_search_model_id'],
                        es_connection=es_client,
                    )
            query_vector = embeddings.embed_documents([question])[0]
            es_query_str = es_query_str.replace('"{{query_vector}}"', str(query_vector))
        else:
            es_query_str = es_query_str.replace("{{model_id}}", parameters['elastic_search_model_id'])
            es_query_str = es_query_str.replace("{{model_text}}", question)
        
        # Convert back to dictionary
        es_query_template = json.loads(es_query_str)
        es_query=es_query_template.get("query",es_query_template)
        print(es_query)

        query_temp_args = {'query': es_query}
        if 'sub_searches' in es_query:
            query_temp_args = {'body': es_query}

        try:
            response = es_client.search(
                index=index_name, 
                size=parameters['vectorsearch_top_n_results'],
                **query_temp_args
            )
            print("\nResponse:")
            for hit in response['hits']['hits']:

                score = hit['_score']
                title = hit['_source']['metadata']['title']
                page_content=hit['_source']['text']
                source = hit['_source']['metadata']['source']
                url = hit['_source']['metadata']['document_url']
                page_number = hit['_source']['metadata']['page_number']


                # print(f"\nRelevance Score  : {score}\nTitle            : {title}\nSource     : {source}\nDocument Content : {page_content}\nDocument URL : {url}\nPage Number : {page_number}")
            
        except Exception as e:
                print("\nAn error occurred while querying elastic search, please retry after sometime:", e)


    embedding = get_embedding(environment, parameters, project_id, wml_credentials, WML_SERVICE_URL)
    
    # ### Vector Search Query to obtain most relevant result using the Langchain retrievers
    match connection_type:
        case "elasticsearch":
            search_kwargs = {
            "k": parameters['vectorsearch_top_n_results'],
            "score_threshold": float(parameters['rag_es_min_score']),
            "include_scores": True,
            "verbose": True
            }

            def custom_body_func(query: str) -> dict:
                print(f"Reading from the template {parameters['elastic_search_template_file']}")
                return es_query_template
            
            from langchain_elasticsearch import ElasticsearchRetriever
            retriever = ElasticsearchRetriever(
                            es_client=es_client,
                            index_name=index_name,
                            body_func=custom_body_func,
                            content_field="text",
                            # document_mapper = document_mapper,
                            search_kwargs=search_kwargs
                        )
            
            print("ElasticsearchRetriever Created with",parameters['elastic_search_model_id'])
            search_result = retriever.invoke(question)
            # print(f"Question: {question}")
            # print("Response: ")
            # print([{"page_content": doc.page_content, "metadata":doc.metadata['_source']['metadata'], "score": doc.metadata['_score'] or doc.metadata['_rank']} for doc in results])
            
        case "milvus" | "milvuswxd":
            milvus_credentials = conn_credentials
            from langchain_milvus import Milvus, BM25BuiltInFunction
            if environment=="cloud":
                credentials=Credentials(
                    api_key = parameters['watsonx_ai_api_key'],
                    url =WML_SERVICE_URL)
                embedding = Embeddings(
                model_id=parameters['embedding_model_id'],
                credentials=credentials,
                project_id=project_id,
                verify=True
                )
                
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
                            raise Exception(parameters["embedding_model_id"] + "model is missing. Please check and update embedding_model_id adv param")
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
                
            hybrid_search = True if parameters['milvus_hybrid_search'].lower()=="true" else False
            dense_index_param = {"metric_type": "L2", "index_type": "IVF_FLAT","params": {"nlist": 1024}}
            print(f"using the embedding model {parameters['embedding_model_id']} for dense embeddings.")
            if hybrid_search:
                sparse_index_param = {"metric_type": "BM25","index_type": "SPARSE_INVERTED_INDEX", "params": {"drop_ratio_build": 0.2}}
                print("using BM25 sparse embeddings.")
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
                search_result = vector_store.similarity_search_with_score(question,  ranker_type=parameters["milvus_reranker"], ranker_params = {"k": 60}  if parameters["milvus_reranker"]=="rrf" else {"weights": [0.6, 0.4]})
            else:
                vector_store = Milvus(
                    embedding_function=embedding,
                    index_params=dense_index_param,
                    connection_args=milvus_credentials,
                    primary_field='id',
                    consistency_level="Strong",
                    collection_name=index_name 
                )
                search_result = vector_store.similarity_search_with_score_by_vector(embedding.embed_query(question), k=parameters['vectorsearch_top_n_results'])
            print(search_result[0])
    

        case "datastax" | "datastax-astradb":
            
            print("using the model",parameters['embedding_model_id'], "to create embeddings")
            embedding = get_embedding(environment, parameters, project_id, wml_credentials, WML_SERVICE_URL) if environment == "cloud" else get_embedding(environment, parameters, project_id, wml_credentials, None)  
    
            from langchain_community.vectorstores import Cassandra
            vector_store = Cassandra(
                embedding=embedding,
                table_name=index_name 
            )
            print("Datastax vector store Created on the index",index_name)
            
            search_result= vector_store.similarity_search_with_score_by_vector(embedding.embed_query(question), k=parameters['vectorsearch_top_n_results'])
            print("\nQuestion:",question, "\nSearch Results:", search_result)

        case _:
            raise ValueError(f"Unsupported connection_type: {connection_type}")
        
    return search_result
        


# 2. Using the Langchain Retrievers

def get_embedding(environment, parameters, project_id, wml_credentials, WML_SERVICE_URL):
    """
    Generate embedding.

    Parameters:
    - environment (str): cloud/on-prem
    - parameters (str): connection parameters
    - project_id (str): IBM cloud project id
    - wml_credentials (str): WML credentials
    - WML_SERVICE_URL (str): service url

    Returns:
    - embedding  returns embedded results.
    """
    if environment == "cloud":
        credentials = Credentials(
            api_key=parameters['watsonx_ai_api_key'],
            url=WML_SERVICE_URL
        )
        embedding = Embeddings(
            model_id=parameters['embedding_model_id'],
            credentials=credentials,
            project_id=project_id,
            verify=True
        )
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
                    print("Local on-prem embedding models not found, using models from IBM Cloud API")
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


def generate_answer(payload):

    """
    Generate answer to the user query.

    Parameters:
    - payload (dict): It contains user query and connection_name

    Returns:
    - search_result (dict) Results of the search operation.
    """

    question = payload['query']
    connection_name = payload['connection_name']
    index_name = payload['index_name']

    # Tested for milvus
    if connection_name == "milvus_connect":
        milvus_credentials, connection_type = connection_setup(connection_name, question)
        search_result = search_query_template(connection_type, milvus_credentials, index_name, question, parameters)

    if connection_name == "elasticsearch_connect":
        es_client, connection_type = connection_setup(connection_name, question)
        search_result = search_query_template(connection_type, es_client, index_name, question, parameters)

    return search_result, search_result[0]