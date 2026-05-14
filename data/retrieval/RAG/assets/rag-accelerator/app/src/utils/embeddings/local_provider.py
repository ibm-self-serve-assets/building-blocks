"""
Local embedding provider implementation using sentence-transformers.
"""

from typing import List, Dict, Any
import logging
import os

from .base import BaseEmbedding

logger = logging.getLogger(__name__)


class LocalEmbedding(BaseEmbedding):
    """
    Local embedding provider using sentence-transformers with local model files.
    This provider loads models from a local directory for offline usage.
    """
    
    def __init__(self, parameters: Dict[str, Any]):
        """
        Initialize Local embedding provider.
        
        Args:
            parameters: Configuration parameters including:
                - embedding_model_id: Model name or path to local model directory
                - local_model_path: Optional path to local model directory
                - device: Device to run model on ('cpu' or 'cuda')
                - cache_folder: Optional cache folder for models
        """
        super().__init__(parameters)
        self._initialize_embedding()
    
    def _initialize_embedding(self) -> None:
        """
        Initialize the local embedding model using sentence-transformers.
        """
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info("Initializing Local embedding model")
            
            # Get model path - can be a model name or local directory
            model_id = self.parameters.get("embedding_model_id", "all-MiniLM-L6-v2")
            local_model_path = self.parameters.get("local_model_path")
            device = self.parameters.get("device", "cpu")
            cache_folder = self.parameters.get("cache_folder")
            
            # Use local path if provided, otherwise use model_id
            model_path = local_model_path if local_model_path else model_id
            
            # Check if local path exists
            if local_model_path and not os.path.exists(local_model_path):
                logger.warning(f"Local model path does not exist: {local_model_path}. Will attempt to download.")
            
            # Initialize sentence transformer model
            kwargs = {"device": device}
            if cache_folder:
                kwargs["cache_folder"] = cache_folder
            
            self._embedding_instance = SentenceTransformer(model_path, **kwargs)
            
            # Set model configuration
            self._model_config = {
                "max_tokens": self._embedding_instance.max_seq_length,
                "prefix": "",
            }
            
            logger.info(f"Local embedding model initialized: {model_path} on {device}")
            
        except ImportError:
            logger.exception("sentence-transformers library not installed. Install with: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.exception(f"Failed to initialize Local embedding: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents using local model.
        Ensures texts are within token limits before embedding.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            if not self._embedding_instance:
                raise RuntimeError("Embedding model not initialized")
            
            logger.debug(f"Embedding {len(texts)} documents with Local model")
            
            # Get model token limit and apply safety margin
            model_max_tokens = self._model_config.get("max_tokens", 512)
            safe_token_limit = int(model_max_tokens * 0.8)
            
            safe_texts = []
            
            for i, text in enumerate(texts):
                safe_text = self.ensure_token_limit(text, safe_token_limit)
                safe_texts.append(safe_text)
                
                if len(safe_text) < len(text):
                    logger.warning(f"Document {i} truncated from {len(text)} to {len(safe_text)} characters")
            
            # Encode texts to embeddings
            embeddings = self._embedding_instance.encode(
                safe_texts,
                convert_to_numpy=True,
                show_progress_bar=False,
                batch_size=32  # Process in batches for efficiency
            )
            
            # Convert numpy arrays to lists
            vectors = [embedding.tolist() for embedding in embeddings]
            
            return vectors
            
        except Exception as e:
            logger.exception(f"Failed to embed documents: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query text using local model.
        Ensures text is within token limits before embedding.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
        """
        try:
            if not self._embedding_instance:
                raise RuntimeError("Embedding model not initialized")
            
            logger.debug("Embedding query with Local model")
            
            # Get model token limit and apply safety margin
            model_max_tokens = self._model_config.get("max_tokens", 512)
            safe_token_limit = int(model_max_tokens * 0.8)
            
            safe_text = self.ensure_token_limit(text, safe_token_limit)
            
            if len(safe_text) < len(text):
                logger.warning(f"Query truncated from {len(text)} to {len(safe_text)} characters")
            
            # Encode single text
            embedding = self._embedding_instance.encode(
                safe_text,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            
            # Convert numpy array to list
            return embedding.tolist()
            
        except Exception as e:
            logger.exception(f"Failed to embed query: {e}")
            raise
