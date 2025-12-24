"""
Vector store utilities for RAG agent evaluation.

This module provides helpers for creating and managing vector stores with IBM Watsonx embeddings.
"""

import os
import json
import requests
from typing import List, Optional, Union
from pathlib import Path

import warnings
warnings.filterwarnings('ignore')


def load_documents_from_url(url: str, file_type: str = "json") -> List[dict]:
    """Load documents from a URL.

    Args:
        url: URL to download documents from.
        file_type: Type of file (json, pdf, csv).

    Returns:
        List of document dictionaries.

    Raises:
        requests.exceptions.RequestException: If download fails.

    Example:
        ```python
        docs = load_documents_from_url(
            "https://example.com/data.json",
            file_type="json"
        )
        ```
    """
    response = requests.get(url)
    response.raise_for_status()

    if file_type == "json":
        return response.json()
    elif file_type == "pdf":
        # Save PDF and return path for processing
        temp_path = "temp_document.pdf"
        with open(temp_path, "wb") as f:
            f.write(response.content)
        return [{"path": temp_path, "type": "pdf"}]
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def create_vector_store(
    documents: Union[List[dict], str],
    embedding_model_id: str = "ibm/slate-30m-english-rtrvr-v2",
    apikey: Optional[str] = None,
    project_id: Optional[str] = None,
    chunk_size: int = 400,
    chunk_overlap: int = 50,
    persist_directory: str = "vector_store"
):
    """Create a Chroma vector store with Watsonx embeddings.

    Args:
        documents: List of documents or path to PDF file.
        embedding_model_id: Watsonx embedding model ID.
        apikey: Watsonx API key (uses env var if not provided).
        project_id: Watsonx project ID (uses env var if not provided).
        chunk_size: Size of document chunks.
        chunk_overlap: Overlap between chunks.
        persist_directory: Directory to persist the vector store.

    Returns:
        Chroma vector store instance.

    Example:
        ```python
        vector_store = create_vector_store(
            documents=docs,
            chunk_size=400,
            persist_directory="my_vector_store"
        )

        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        ```
    """
    from langchain_community.vectorstores import Chroma
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_ibm import WatsonxEmbeddings

    # Get credentials
    apikey = apikey or os.getenv("WATSONX_APIKEY")
    project_id = project_id or os.getenv("WATSONX_PROJECT_ID")

    if not apikey or not project_id:
        raise ValueError("API key and project ID required")

    # Process documents
    if isinstance(documents, str):
        # Load from file path
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(documents)
        docs = loader.load()
    elif isinstance(documents, list) and documents and isinstance(documents[0], dict):
        # Convert dict documents to LangChain Documents
        docs = []
        for item in documents:
            if "document" in item and item["document"].strip():
                docs.append(
                    Document(
                        page_content=item["document"],
                        metadata={"id": str(item.get("id", ""))}
                    )
                )
    else:
        docs = documents

    # Chunk documents
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunked_docs = splitter.split_documents(docs)

    # Create embedding model
    embedding_model = WatsonxEmbeddings(
        model_id=embedding_model_id,
        url="https://us-south.ml.cloud.ibm.com",
        apikey=apikey,
        project_id=project_id,
    )

    # Create vector store
    vector_store = Chroma.from_documents(
        documents=chunked_docs,
        embedding=embedding_model,
        persist_directory=persist_directory
    )

    # Persist to disk
    vector_store.persist()

    return vector_store


def create_retriever(
    vector_store,
    search_type: str = "similarity_score_threshold",
    top_k: int = 3,
    score_threshold: float = 0.1
):
    """Create a retriever from a vector store.

    Args:
        vector_store: Chroma vector store instance.
        search_type: Type of search (similarity, similarity_score_threshold, mmr).
        top_k: Number of documents to retrieve.
        score_threshold: Minimum similarity score threshold.

    Returns:
        Retriever instance.

    Example:
        ```python
        retriever = create_retriever(
            vector_store,
            search_type="similarity_score_threshold",
            top_k=3,
            score_threshold=0.1
        )

        docs = retriever.invoke("What is AI?")
        ```
    """
    if search_type == "similarity_score_threshold":
        return vector_store.as_retriever(
            search_type=search_type,
            search_kwargs={"k": top_k, "score_threshold": score_threshold}
        )
    else:
        return vector_store.as_retriever(
            search_type=search_type,
            search_kwargs={"k": top_k}
        )
