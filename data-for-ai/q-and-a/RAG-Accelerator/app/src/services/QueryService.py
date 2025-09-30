from dotenv import load_dotenv
import os
import sys
import pandas as pd
import json
import numpy as np
import warnings
import logging
import ast

from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.chunking import HybridChunker
import time

from pymilvus.model.hybrid import BGEM3EmbeddingFunction
from transformers import AutoTokenizer
from pymilvus import (
FieldSchema,
CollectionSchema,
DataType,
Collection,
AnnSearchRequest,
RRFRanker,
WeightedRanker,
connections,
MilvusClient
)

from ibm_watsonx_ai.foundation_models import Model


# remove if debugging
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

########## Functions to initialize environment ##########

def init_environment():
    try:
        load_dotenv()
        config = {
            'watsonx_apikey': os.getenv("WATSONX_APIKEY"),
            'watsonx_project_id': os.getenv("WATSONX_PROJECT_ID"),          
            'watsonx_model_id': os.getenv("WATSONX_MODEL_ID"),
            'watsonx_url': os.getenv("WATSONX_URL"),
            'wxd_milvus_host': os.getenv("WXD_MILVUS_HOST"),
            'wxd_milvus_port': os.getenv("WXD_MILVUS_PORT"),          
            'wxd_milvus_user': os.getenv("WXD_MILVUS_USER"),
            'wxd_milvus_password': os.getenv("WXD_MILVUS_PASSWORD"),
        }
        validate_environment(config)

        # Authentication to Milvus Client
        MilvusURL=f"https://{config['wxd_milvus_host']}:{config['wxd_milvus_port']}"
        client = MilvusClient(
            uri=MilvusURL,
            user=config['wxd_milvus_user'],
            password=config['wxd_milvus_password']
        )

        client.list_collections()

        # load in embedding model
        embedding_model='BAAI/bge-m3'
        ef = BGEM3EmbeddingFunction(model_name=embedding_model,
                                    use_fp16=False, device="cpu")
        
        # Define model parameters and ID
        model_id = config['watsonx_model_id']
        parameters = {
            "decoding_method": "greedy",
            "min_new_tokens":1,
            "max_new_tokens": 400,
            "repetition_penalty": 1,
            "stop_sequences":[],
        }

        # Initialize watsonx.ai model
        model = Model(
            model_id=model_id,
            params=parameters,
            credentials={"url": config['watsonx_url'], "apikey": config['watsonx_apikey']},
            project_id=config['watsonx_project_id']
        )

        prompt_template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a helpful and professional assistant for answering questions based on provided documents. You are given the extracted parts of several documents as your context and a question. Output an answer to the question based strictly on the information in the documents. If you cannot base your answer on the given documents, please state that you do not have an answer. Do not make up an answer. You should use a professional tone and provide clear and concise answers. However, if the answer contains several steps from the documents, output the entire list of steps in a numbered list. Do not reference symbols or table values in your answer.

 Context: {context} 
 Question: {query} <|eot_id|><|start_header_id|>user<|end_header_id|> 

 Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

        config['client'] = client
        config['ef'] = ef
        config['model'] = model
        config['prompt_template'] = prompt_template

        logging.info("Environment initialized successfully")
        return config
    except Exception as e:
        logging.exception("Error initializing environment")
        raise

def validate_environment(config):
    """
    Validates required environment variables and logs warnings for missing variables.
    """
    missing_vars = [key for key, value in config.items() if not value]
    
    if missing_vars:
        error_msg = f"Required environment variables are missing: {', '.join(missing_vars)}"
        logging.error(error_msg)
        raise EnvironmentError(error_msg)
    
########## Main functions ##########    
def query_hybrid_search(query, config):
    ef = config['ef']
    client = config['client']
    collection_name = config['collection_name']
    print(f"Querying collection: {collection_name}")
    query_embeddings = ef([query])

    search_param_dense = {
        "data": query_embeddings["dense"],
        "anns_field": "dense_vector",
        "param": {
            "metric_type": "COSINE",
            "params": {}
        },
        "limit": config['num_results']
    }
    request_1 = AnnSearchRequest(**search_param_dense)

    search_param_sparse = {
        "data": query_embeddings["sparse"],
        "anns_field": "sparse_vector",
        "param": {
            "metric_type": "IP",
            "params": {}
        },
        "limit": config['num_results']
    }
    request_2 = AnnSearchRequest(**search_param_sparse)

    reqs = [request_1, request_2]


    LIMIT = config['num_rerank_results']
    ranker= WeightedRanker(0.8, 0.3) 

    res = client.hybrid_search(
        collection_name=collection_name,
        reqs=reqs, 
        ranker=ranker, 
        limit=LIMIT, 
        output_fields=["text", "page_no", "filename"]
    )

    return res

def clean_tables_in_string(input_string):
    lines = input_string.split('\n')
    output_lines = []
    
    i = 0
    while i < len(lines):
        current_line = lines[i].strip()
        
        # Check if line is the start of a table
        if current_line.startswith('|') and current_line.endswith('|'):
            # Collect all lines that are part of this table
            table_lines = [lines[i]]
            i += 1
            
            while i < len(lines) and lines[i].strip().startswith('|') and lines[i].strip().endswith('|'):
                table_lines.append(lines[i])
                i += 1
            
            # Parse the table
            parsed_rows = []
            for line in table_lines:
                # Split by | and remove first and last empty items
                cells = line.split('|')
                # Remove the first and last empty elements
                if cells[0].strip() == '':
                    cells = cells[1:]
                if cells[-1].strip() == '':
                    cells = cells[:-1]
                parsed_rows.append([cell.strip() for cell in cells])
            
            # Check if any columns are completely empty in the DATA rows (not header/separator)
            col_count = max(len(row) for row in parsed_rows)
            empty_cols = []
            
            # Only check data rows (after header and separator)
            data_rows = parsed_rows[2:] if len(parsed_rows) > 2 else []
            
            # Find empty columns
            for col in range(col_count):
                if all(col >= len(row) or row[col] == '' for row in data_rows):
                    empty_cols.append(col)
            
            # If we found empty columns, rebuild the table
            if empty_cols:
                new_table_lines = []
                for row_idx, row in enumerate(parsed_rows):
                    # Create a new row excluding the empty columns
                    new_row = []
                    for j in range(len(row)):
                        if j not in empty_cols:
                            new_row.append(row[j])
                    # Format as a table row
                    new_table_lines.append('|' + '|'.join(f' {cell} ' for cell in new_row) + '|')
                
                # Add the processed table to output
                output_lines.extend(new_table_lines)
            else:
                # No empty columns, keep the table as is
                output_lines.extend(table_lines)
        else:
            # Not a table line, just add it to output
            output_lines.append(lines[i])
            i += 1
    
    return '\n'.join(output_lines)

def generate_answer(config):
    query = config['query']
    start_time = time.time()
    search_res = query_hybrid_search(query.lower(), config)
    end_time = time.time()
    print(f"Load and search time: {end_time - start_time:.2f}")
    retrieved_lines_with_distances = []
    for result in search_res:
        for hit in result:
            retrieved_lines_with_distances.append((str(hit['entity']['text']), hit['distance']))
    context_lines = []
    for i, line_with_distance in enumerate(retrieved_lines_with_distances):
        document_text = clean_tables_in_string(line_with_distance[0])
        context_lines.append(document_text)
    context = "\n\n".join(context_lines)
    generation_start_time = time.time()
    answer = config['model'].generate_text(prompt=config['prompt_template'].format(query = query, context=context)).strip()
    generation_end_time = time.time()
    print(f"Generation time: {generation_end_time - generation_start_time:.2f}")
    print(f"Context: {context}")
    print("==========")
    print(f"Answer: {answer}")
    return context, answer
