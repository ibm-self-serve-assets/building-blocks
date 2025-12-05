import os
from dotenv import load_dotenv
load_dotenv()  # Load values from .env

# parameter configuration
PARAMETERS = {
    "RAG_parameter_set" : {
        "vectorsearch_top_n_results" : os.getenv("RAG_VECTORSEARCH_TOP_N_RESULTS"),
        "es_number_of_shards" : os.getenv("RAG_ES_NUMBER_OF_SHARDS"),
        "rag_es_min_score" : os.getenv("RAG_ES_MIN_SCORE"),
        "include_all_html_tags" : os.getenv("RAG_INCLUDE_ALL_HTML_TAGS"),
        "vector_store_index_name": os.getenv("RAG_VECTOR_STORE_INDEX_NAME"),
        "watsonx_ai_api_key": os.getenv("RAG_WATSONX_AI_API_KEY")
    },
    "RAG_advanced_parameter_set" : {
    "embedding_model_id":  os.getenv("RAG_ADV_MILVUS_EMBEDDING_MODEL_ID"),
    "milvus_hybrid_search" :  os.getenv("RAG_ADV_MILVUS_HYBRID_SEARCH"),
    "milvus_reranker" :  os.getenv("RAG_ADV_MILVUS_RERANKER")
    }
}

# Milius connection
WXD_MILVUS = {
    'database': os.getenv("WXD_MILVUS_DATABASE"),
    'password': os.getenv("WXD_MILVUS_PASSWORD"), 
    'port': os.getenv("WXD_MILVUS_PORT"), 
    'host': os.getenv("WXD_MILVUS_HOST"),
    'ssl': os.getenv("WXD_MILVUS_SSL"),
    'username': os.getenv("WXD_MILVUS_USERNAME"),
    '.': {
        'name': os.getenv("WXD_MILVUS_NAME"),
        'description': os.getenv("WXD_MILVUS_DESCRIPTION"),
        'asset_id': os.getenv("WXD_MILVUS_ASSET_ID"),
        'asset_type': os.getenv("WXD_MILVUS_ASSET_TYPE")
        }
    }