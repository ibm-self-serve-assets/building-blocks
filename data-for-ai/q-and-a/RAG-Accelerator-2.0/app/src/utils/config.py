import os
from dotenv import load_dotenv
load_dotenv()  # Load values from .env

# parameter configuration for milvus and elastic search
PARAMETERS = {
    "RUNTIME":{
        "environment": os.getenv("RUNTIME_ENVIRONMENT"),
        "runtime_env_apsx_url": os.getenv("RUNTIME_ENV_APSX_URL"),
        "runtime_env_region": os.getenv("RUNTIME_REGION"),
        "user_access_token": os.getenv("USER_ACCESS_TOKEN"),
        "ibm_iam_url": os.getenv("IBM_IAM_URL"),
        "server_url": os.getenv("SERVER_URL"),
        "astradb_scb_zip_filename":os.getenv("ASTRADB_SCB_ZIP_FILENAME"),
        "connection_name":os.getenv("CONNECTION_NAME")
    },
    "RAG_parameter_set" : {
        "vectorsearch_top_n_results" : os.getenv("RAG_VECTORSEARCH_TOP_N_RESULTS"),
        "es_number_of_shards" : os.getenv("RAG_ES_NUMBER_OF_SHARDS"),
        "rag_es_min_score" : os.getenv("RAG_ES_MIN_SCORE"),
        "include_all_html_tags" : os.getenv("RAG_INCLUDE_ALL_HTML_TAGS"),
        # "vector_store_index_name": os.getenv("RAG_VECTOR_STORE_INDEX_NAME"),
        "watsonx_ai_api_key": os.getenv("RAG_WATSONX_AI_API_KEY"),
        "elastic_search_template_file": os.getenv("RAG_ELASTIC_SEARCH_TEMPLATE_FILE"),
        "watsonx_url": os.getenv("RAG_WATSONX_URL"),
        "watsonx_deployment_id": os.getenv("RAG_WATSONX_DEPLOYMENT_ID"),
        "watsonx_space_id": os.getenv("RAG_WATSONX_SPACE_ID"),
        "watsonx_project_id": os.getenv("RAG_WATSONX_PROJECT_ID"),
        "watsonx_max_tokens": os.getenv("RAG_WATSONX_MAX_TOKENS"),
        "watsonx_min_tokens": os.getenv("RAG_WATSONX_MIN_TOKENS")
    },
    "RAG_advanced_parameter_set" : {
        "embedding_model_id":  os.getenv("RAG_ADV_MILVUS_EMBEDDING_MODEL_ID"),
        "milvus_hybrid_search" :  os.getenv("RAG_ADV_MILVUS_HYBRID_SEARCH"),
        "milvus_reranker" :  os.getenv("RAG_ADV_MILVUS_RERANKER"),
        "elastic_search_model_id" :  os.getenv("RAG_ADV_ELASTIC_SEARCH_MODEL_ID"),
        "elastic_search_vector_type" :  os.getenv("RAG_ADV_ELASTIC_SEARCH_VECTOR_TYPE"),
        "chunk_size" :  os.getenv("RAG_ADV_CHUNK_SIZE"),
        "chunk_overlap" :  os.getenv("RAG_ADV_CHUNK_OVERLAP"),
        "index_chunk_size" :  os.getenv("RAG_ADV_INDEX_CHUNK_SIZE")
    }
}