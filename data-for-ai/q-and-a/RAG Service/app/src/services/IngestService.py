from dotenv import load_dotenv
import os
import sys
import pandas as pd
import json
import numpy as np
import warnings
import logging
import ast

from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.document_converter import DocumentConverter, PdfFormatOption # import extra support for .json, markdown, HTML
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.chunking import HybridChunker
import time

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter # more splitter support / code-level custom splitters

from pymilvus.model.hybrid import BGEM3EmbeddingFunction
from pymilvus.model.dense import SentenceTransformerEmbeddingFunction, InstructorEmbeddingFunction
from pymilvus.model.sparse import SpladeEmbeddingFunction

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

from app.src.utils.ingestion_helper_functions import json_document_converter


# remove if debugging
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

########## Functions to initialize environment ##########

def init_environment(collection_name, chunk_type): # chunk type is where you can choose between a markdown and a recursive text splitter
    try:
        load_dotenv()
        config = {
            'wxd_milvus_host': os.getenv("WXD_MILVUS_HOST"),
            'wxd_milvus_port': os.getenv("WXD_MILVUS_PORT"),          
            'wxd_milvus_user': os.getenv("WXD_MILVUS_USER"),
            'wxd_milvus_password': os.getenv("WXD_MILVUS_PASSWORD"),
            'watsonx_apikey': os.getenv("WATSONX_APIKEY"),
            'watsonx_project_id': os.getenv("WATSONX_PROJECT_ID"),
            'collection_name': collection_name,
            'chunk_type': chunk_type
        }
        validate_environment(config)
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

def ingest_files(config, files, search_type='hybrid', window_size='L'): 

    # Flag to determine if custom embedding models are used
    is_dual = False

    if search_type == 'dense': 
        # NEW: window_size parameters
        if window_size == 'S': 
            ef_max_tokens = 512
            embedding_model='all-MiniLM-L6-v2' 
            ef = SentenceTransformerEmbeddingFunction(embedding_model=embedding_model, device='cpu')

        elif window_size == 'M':
            ef_max_tokens = 2048
            embedding_model='all-MiniLM-L6-v2' 
            ef = SentenceTransformerEmbeddingFunction(embedding_model=embedding_model, device='cpu')

        elif window_size == 'L':
            ef_max_tokens = 8192
            embedding_model='hkunlp/instructor-xl' 
            ef = InstructorEmbeddingFunction(model_name=embedding_model)
        
        # Enter custom choice of model and context window size here: 
        elif window_size == 'C':            
            embedding_model=''
            ef_max_tokens = AutoTokenizer.from_pretrained(embedding_model).model_max_length
            ef = InstructorEmbeddingFunction(model_name=embedding_model)
    

    elif search_type == 'hybrid':
        if window_size == 'S': 
            ef_max_tokens = 512
            embedding_model='BAAI/bge-small-en-v1.5'    # 'Snowflake/snowflake-arctic-embed-s', 'intfloat/multilingual-e5-large'
            ef = BGEM3EmbeddingFunction(model_name=embedding_model, use_fp16=False, device="cpu") 

        elif window_size == 'M':
            ef_max_tokens = 2048
            embedding_model='Snowflake/snowflake-arctic-embed-m-long'   # 'nbroad/xlm-roberta-base-2048', 'nomic-ai/nomic-bert-2048'
            ef = BGEM3EmbeddingFunction(model_name=embedding_model, use_fp16=False, device="cpu")

        elif window_size == 'L':
            ef_max_tokens = 8192
            embedding_model='BAAI/bge-m3'   # 'nomic-ai/nomic-embed-text-v1', 'jinaai/jina-embeddings-v2-base-en'
            ef = BGEM3EmbeddingFunction(model_name=embedding_model, use_fp16=False, device="cpu")

        elif window_size == 'C': 
            # Sparse embedding functionality
            sparse_ef = SpladeEmbeddingFunction(model_name="naver/splade-cocondenser-ensembledistil")

            # Dense embedding functionality
            embedding_model=''
            ef_max_tokens = AutoTokenizer.from_pretrained(embedding_model).model_max_length

            # Update flag
            is_dual = True
        

    ef_tokenizer = AutoTokenizer.from_pretrained(embedding_model)

    if ef_max_tokens > ef_tokenizer.model_max_length:
        raise ValueError(
            f"Requested max token size ({ef_max_tokens}) exceeds "
            f"the model's supported limit ({ef_tokenizer.model_max_length}) for {embedding_model}"
        )

    ef_tokenizer.model_max_length = ef_max_tokens


    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True
    pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE  # use ACCURATE if you prefer more accurate TableFormer model, however it's slower

    document_converter = DocumentConverter(format_options=
                                        {
                                            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                                            })
    
    print(1)
    
    EXPORT_TYPE = config['chunk_type']
    print(EXPORT_TYPE)
    if EXPORT_TYPE == "DOCLING_DOCS":
        def extract_metadata(chunk):
            metadata = {
                    "page_no": None,
                    "filename": None
                }
            if hasattr(chunk, 'meta'):

                # Extract page information and content type
                if hasattr(chunk.meta, 'doc_items'):
                    for item in chunk.meta.doc_items:
                        if hasattr(item, 'prov') and item.prov:
                            for prov in item.prov:
                                if hasattr(prov, 'page_no'):
                                    metadata["page_no"] = prov.page_no
                
                if hasattr(chunk.meta, 'origin'):
                    if hasattr(chunk.meta.origin, 'filename'):
                        metadata['filename'] = chunk.meta.origin.filename
                
                return metadata

        def convert_and_hybrid_chunk(file):
            file_full_path = file['full_path']
            filename = file['filename']
            file_ext = filename.lower().split('.')[-1]

            print(f"Converting {file_full_path} to a docling document and using hybrid chunker...")
            start_time = time.time()

            if file_ext == 'json':
                doc = json_document_converter(file_full_path)
            else: 
                doc = document_converter.convert(file_full_path).document

            chunker = HybridChunker(tokenizer=ef_tokenizer)
            chunk_iter = chunker.chunk(dl_doc=doc)

            # iterate over chunks, creating a chunk document object per chunk with the content and metadata
            chunked_document_objects = []
            for chunk in chunk_iter:
                chunked_document_object = {"page_content": chunker.contextualize(chunk=chunk), "metadata": extract_metadata(chunk)}
                chunked_document_objects.append(chunked_document_object)
            end_time = time.time()
            print(f"Converted {file_full_path} to a docling document and chunked\nNumber of chunks: {len(chunked_document_objects)}\nExecution time: {round(end_time - start_time, 2)}")
            return chunked_document_objects
        
        document_objects = []
        for file in files:
            chunked_document_objects = convert_and_hybrid_chunk(file)
            document_objects += chunked_document_objects

    if EXPORT_TYPE == "MARKDOWN":
        def convert_and_markdown_split(file):
            file_full_path = file['full_path']
            filename = file['filename']
            file_ext = filename.lower().split('.')[-1]

            print(f"Converting {filename} to a docling document and using markdown splitter...")
            start_time = time.time()

            if file_ext == 'json':
                doc = json_document_converter(file_full_path).export_to_markdown()
            else: 
                doc = document_converter.convert(file_full_path).document.export_to_markdown()

            splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header_1"),
                ("##", "Header_2"),
                ("###", "Header_3"),
            ],
            strip_headers=False
            )

            md_chunks = splitter.split_text(doc)

            rcs_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = sum((rcs_splitter.split_documents([d]) for d in md_chunks), [])

            chunked_document_objects = []
            for chunk in chunks:
                print(chunk)
                chunked_document_object = {"page_content": chunk.page_content}
                chunked_document_object['metadata'] = chunk.metadata
                chunked_document_object['metadata']['filename'] = filename
                chunked_document_objects.append(chunked_document_object)
            end_time = time.time()
            print(f"Converted {file_full_path} to a markdown document and split\nNumber of chunks: {len(chunked_document_objects)}\nExecution time: {round(end_time - start_time, 2)}")
            return chunked_document_objects
        
        document_objects = []
        for file in files:
            chunked_document_objects = convert_and_markdown_split(file)
            document_objects += chunked_document_objects
            
    if EXPORT_TYPE == "RECURSIVE": 
        def convert_and_recursive_split(file): 
            file_full_path = file['full_path']
            filename = file['filename']
            print(f"Converting {filename} to a markdown document and using markdown splitter...")
            file_ext = filename.lower().split('.')[-1]

            start_time = time.time()
                        
            if file_ext == 'json':
                doc = json_document_converter(file_full_path).export_to_markdown()
            else: 
                doc = document_converter.convert(file_full_path).document.export_to_markdown()
                
            chunk_size = 1000
            chunk_overlap = 200
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size, chunk_overlap=chunk_overlap
            )

            # # Split
            # splits = text_splitter.split_documents(md_header_chunks)
            # chunk
            chunks = splitter.create_documents([split for split in splitter.split_text(doc)])

            chunked_document_objects = []
            for chunk in chunks:
                print(chunk)
                chunked_document_object = {"page_content": chunk.page_content}
                chunked_document_object['metadata'] = chunk.metadata
                chunked_document_object['metadata']['filename'] = filename
                chunked_document_objects.append(chunked_document_object)
            end_time = time.time()
            print(f"Converted {file_full_path} to a markdown document and recursively split\nNumber of chunks: {len(chunked_document_objects)}\nExecution time: {round(end_time - start_time, 2)}")
            return chunked_document_objects

        document_objects = []
        for file in files: 
            chunked_document_objects = convert_and_recursive_split(file)
            document_objects += chunked_document_objects



    print(EXPORT_TYPE)
        
    # show all chunks    
    for i, chunk in enumerate(document_objects):
        print(f"===Chunk {i}===")
        print(f"chunk page content:\n{chunk['page_content']}\n")
        print(f"chunk metadata:\n{chunk['metadata']}\n")

    # get fields into lists
    docs_list = [str(doc['page_content']) for doc in document_objects]
    filename_list = [doc['metadata']['filename'] for doc in document_objects]
    if EXPORT_TYPE == "DOCLING_DOCS":
        page_no_list = [str(doc['metadata']['page_no']) for doc in document_objects]
    elif EXPORT_TYPE == "MARKDOWN" or EXPORT_TYPE == 'RECURSIVE':
        page_no_list = ["None"] * len(document_objects)



    # create embeddings
    dense_dim = ef.dim["dense"]

    if is_dual: 
        dense_embeddings = ef(docs_list)
        sparse_embeddings = sparse_ef(docs_list)
        
        docs_embeddings = {
            "dense": dense_embeddings,
            "sparse": sparse_embeddings
        }
    else: 
        docs_embeddings = ef(docs_list)


    # load into milvus collection
    connections.connect(host=config['wxd_milvus_host'],
                        port=config['wxd_milvus_port'],
                        secure=True, user=config['wxd_milvus_user'],
                        password=config['wxd_milvus_password'])

    client = MilvusClient(
        uri=f"https://{config['wxd_milvus_host']}:{config['wxd_milvus_port']}",
        user=config['wxd_milvus_user'],
        password=config['wxd_milvus_password']
    )
    
# if dual embeddings are used, start writing functionality for adding a sparse embedding function

    if search_type == 'hybrid':

        # CODE LEVEL: CUSTOM COLLECTION SCHEMA FORMAT
        '''
        fields = [
            FieldSchema(name='id', dtype=DataType.VARCHAR, description='IDs', is_primary=True, auto_id=True, max_length=100),
            FieldSchema(name='field_name', dtype=DataType.VARCHAR, description='custom field format', max_length=65535),
            FieldSchema(name="sparse_vector", dtype=DataType.SPARSE_FLOAT_VECTOR, description='sparse embedding vectors'),
            FieldSchema(name="dense_vector", dtype=DataType.FLOAT_VECTOR, description='dense embedding vectors', dim=dense_dim),
        ]
        '''

        fields = [
            # Use auto generated id as primary key
            FieldSchema(
                name="id", dtype=DataType.VARCHAR, description='IDs', is_primary=True, auto_id=True, max_length=100
            ),
            FieldSchema(name='text', dtype=DataType.VARCHAR, description='text', max_length=65535),
            FieldSchema(name='page_no', dtype=DataType.VARCHAR, description='page_no', max_length=100),    
            FieldSchema(name='filename', dtype=DataType.VARCHAR, description='filename', max_length=300),
            FieldSchema(name="sparse_vector", dtype=DataType.SPARSE_FLOAT_VECTOR, description='sparse embedding vectors'),
            FieldSchema(name="dense_vector", dtype=DataType.FLOAT_VECTOR, description='dense embedding vectors', dim=dense_dim),
        ]

        collection_name = config['collection_name']

        if client.has_collection(collection_name=collection_name):
            client.drop_collection(collection_name=collection_name)
            print(f"Dropped existing collection: {collection_name}")
        schema = CollectionSchema(fields, "")

        col = Collection(collection_name, schema, consistentcy_level="Strong")

        # creating indexes for vectors
        sparse_index = {"index_type": "SPARSE_INVERTED_INDEX", "metric_type": "IP"}
        dense_index = {"index_type": "FLAT", "metric_type": "COSINE"}
        col.create_index("sparse_vector", sparse_index)
        col.create_index("dense_vector", dense_index)

        # insert data into collection
        entities = [
            docs_list,
            page_no_list,
            filename_list,
            docs_embeddings["sparse"],
            docs_embeddings["dense"],
        ]

    elif search_type == 'dense':
         # defining collection
         # CODE LEVEL: CUSTOM COLLECTION SCHEMA FORMAT
        '''
        fields = [
            FieldSchema(name='id', dtype=DataType.VARCHAR, description='IDs', is_primary=True, auto_id=True, max_length=100),
            FieldSchema(name='field_name', dtype=DataType.VARCHAR, description='custom field format', max_length=65535),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, description='embedding vectors', dim=dense_dim),
        ]
        '''
    
        fields = [
            # Use auto generated id as primary key
            FieldSchema(
                name="id", dtype=DataType.VARCHAR, description='IDs', is_primary=True, auto_id=True, max_length=100
            ),
            FieldSchema(name='text', dtype=DataType.VARCHAR, description='text', max_length=65535),
            FieldSchema(name='page_no', dtype=DataType.VARCHAR, description='page_no', max_length=100),    
            FieldSchema(name='filename', dtype=DataType.VARCHAR, description='filename', max_length=300),
            FieldSchema(name="dense_vector", dtype=DataType.FLOAT_VECTOR, description='dense embedding vectors', dim=dense_dim),
        ]

        collection_name = config['collection_name']

        if client.has_collection(collection_name=collection_name):
            client.drop_collection(collection_name=collection_name)
            print(f"Dropped existing collection: {collection_name}")
        schema = CollectionSchema(fields, "")

        col = Collection(collection_name, schema, consistentcy_level="Strong")

        # creating indexes for vectors
        dense_index = {"index_type": "FLAT", "metric_type": "COSINE"}
        col.create_index("dense_vector", dense_index)

        # insert data into collection
        entities = [
            docs_list,
            page_no_list,
            filename_list,
            docs_embeddings,
        ]

    col.insert(entities)
    col.load()

    return len(docs_list)