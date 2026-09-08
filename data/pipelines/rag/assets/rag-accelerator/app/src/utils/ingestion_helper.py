from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import BSHTMLLoader, DirectoryLoader,PyPDFLoader
from bs4 import BeautifulSoup
import os
import warnings

warnings.filterwarnings("ignore")

from app.src.utils import rag_helper_functions as rag_helper_functions
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create a logger
logger = logging.getLogger(__name__)
import nltk
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
# Ensure NLTK dependencies
nltk.download("punkt_tab", quiet=True)
nltk.download("averaged_perceptron_tagger_eng", quiet=True)

from langchain.schema import Document
        

class StructuredHTMLLoader(BSHTMLLoader):
    """Custom HTML loader that includes all HTML tags in the extracted text."""
    def load(self):
        with open(self.file_path, "r", encoding=self.encoding) as f:
            soup = BeautifulSoup(f, "html.parser")
            texts = soup.find_all(text=True)
            visible_texts = [t.strip() for t in texts if t.strip()]
            full_text = "\n".join(visible_texts)
            return [Document(page_content=full_text, metadata={"source": self.file_path})]


class DocumentProcessor:
    """Handles document loading and processing for RAG pipelines."""

    def __init__(self, parameters):
        """
        Initialize the DocumentProcessor with configuration parameters.

        Args:
            parameters (dict): Configuration parameters including:
                - include_all_html_tags: Whether to use StructuredHTMLLoader
                - ingestion_chunk_size: Size of text chunks
                - ingestion_chunk_overlap: Overlap between chunks
        """
        self.parameters = parameters
    
    def load_documents(self, directory):
        """
        Load documents from a directory using appropriate loaders for each file type.
        logger.infos detailed information about each loaded document.

        Args:
            directory (str): Path to the directory containing documents

        Returns:
            list: List of loaded Document objects
        """
        try:
            loaders = [
                DirectoryLoader(
                    directory,
                    glob="**/*.html",
                    show_progress=True,
                    recursive=True,
                    loader_cls=BSHTMLLoader if self.parameters['include_all_html_tags'].lower() == "false"
                    else StructuredHTMLLoader
                ),
                DirectoryLoader(directory, glob="**/*.pdf", show_progress=True, loader_cls=PyPDFLoader),
                DirectoryLoader(directory, glob="**/*.pptx", show_progress=True),
                DirectoryLoader(directory, glob="**/*.docx", show_progress=True),
                DirectoryLoader(directory, glob="**/*.md", show_progress=True),
                DirectoryLoader(directory, glob="**/*.txt", show_progress=True)
            ]

            documents = []
            total_loaded = 0

            logger.info("\n=== Document Loading Summary ===")
            for loader in loaders:
                try:
                    logger.info(f"\nLoading {loader.glob} files...")
                    data = loader.load()

                    if not data:
                        logger.info(f"No documents found for {loader.glob}")
                        continue

                    documents.extend(data)
                    total_loaded += len(data)

                    logger.info(f"Loaded {len(data)} documents from {loader.glob}:")
                    for i, doc in enumerate(data, 1):
                        source = doc.metadata.get('source', 'Unknown source')
                        title = doc.metadata.get('title', os.path.basename(source))
                        logger.info(f"  {i}. {title} ({source})")

                except Exception as e:
                    logger.error(f"Error loading documents with {loader.glob}: {str(e)}")
                    continue

            logger.info(f"\n=== Loading Complete ===")
            logger.info(f"Total documents loaded: {total_loaded}")
            if total_loaded > 0:
                logger.info("Document types loaded:")
                for loader in loaders:
                    count = sum(1 for doc in documents if doc.metadata.get('source', '').endswith(loader.glob[4:].replace('*', '')))
                    if count > 0:
                        logger.info(f"  - {loader.glob}: {count} documents")

            return documents
        
        except Exception as e:
            logger.error(f"Error during loading documents {e}")
            raise

    def _enrich_metadata(self, doc):
        """
        Enrich document metadata with additional information.

        Args:
            doc (Document): The document to process

        Returns:
            tuple: (content, metadata) for the document
        """
        try:
            document_url = ""
            document_title = doc.metadata.get("title", doc.metadata['source'].split("/")[-1].split(".")[0])

            if ".html" in doc.metadata['source']:
                try:
                    with open(doc.metadata['source'], 'r', encoding='utf-8') as html_file:
                        html_content = html_file.read()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    canonical_tag = soup.find('link', {'rel': 'canonical'})
                    title_tag = soup.find('title')

                    if canonical_tag:
                        document_url = canonical_tag.get('href')

                    if title_tag:
                        document_title = title_tag.get_text()
                except Exception as e:
                    print(f"Error processing HTML metadata for {doc.metadata['source']}: {str(e)}")
                    
            metadata = {
                "title": document_title,
                "source": doc.metadata['source'],
                "document_url": document_url,
                "page_number": str(doc.metadata['page']) if 'page' in doc.metadata else ''
            }

            return doc.page_content, metadata
        
        except Exception as e:
            logger.error(f"Error during enriching metadata {e}")
            raise

    def split_documents(self, documents, rag_helper_functions):
        """
        Split documents into chunks and enrich with metadata.

        Args:
            documents (list): List of Document objects to split
            rag_helper_functions: Helper functions for RAG processing

        Returns:
            list: List of split Document objects
        """
        try:
            content = []
            metadata = []

            for doc in documents:
                try:
                    doc_content, doc_metadata = self._enrich_metadata(doc)
                    content.append(doc_content)
                    metadata.append(doc_metadata)
                except Exception as e:
                    print(f"Error processing document {doc.metadata.get('source', 'unknown')}: {str(e)}")
                    continue

            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=self.parameters['ingestion_chunk_size'],
                chunk_overlap=self.parameters['ingestion_chunk_overlap'],
                disallowed_special=()
            )

            split_documents = text_splitter.create_documents(content, metadatas=metadata)
            print(f"{len(documents)} Documents are split into {len(split_documents)} documents with chunk size {self.parameters['ingestion_chunk_size']}")

            # Add chunk sequencing
            chunk_id = 0
            chunk_source = ''
            for chunk in split_documents:
                chunk.metadata["title"] = chunk.metadata.get("title", "Unknown Title")
                chunk.page_content = f"Document Title: {chunk.metadata['title']}\n Document Content: {chunk.page_content}"

                if chunk_source == '' or chunk_source != chunk.metadata["source"]:
                    chunk_id = 1
                    chunk_source = chunk.metadata["source"]
                chunk.metadata["chunk_seq"] = chunk_id
                chunk_id += 1

            # Remove duplicates
            split_docs = rag_helper_functions.remove_duplicate_records(split_documents)
            print(f'After de-duplication, there are {len(split_docs)} documents present')

            return split_docs
        
        except Exception as e:
            logger.error(f"Error during splitting documents into chunks {e}")
            raise
   

    def process_directory(self, directory, rag_helper_functions):
        """
        Complete processing pipeline: load and split documents from a directory.

        Args:
            directory (str): Path to the directory containing documents
            rag_helper_functions: Helper functions for RAG processing

        Returns:
            list: List of processed Document objects
        """
        documents = self.load_documents(directory)
        return self.split_documents(documents, rag_helper_functions)
    
    



