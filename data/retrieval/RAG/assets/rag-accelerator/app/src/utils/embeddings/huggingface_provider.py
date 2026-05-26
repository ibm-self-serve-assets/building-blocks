"""
Hugging Face embedding provider implementation.
"""

from typing import List, Dict, Any
import logging

from .base import BaseEmbedding

logger = logging.getLogger(__name__)


class HuggingFaceEmbedding(BaseEmbedding):
    """
    Hugging Face embedding provider using sentence-transformers library.
    """
    
    def __init__(self, parameters: Dict[str, Any]):
        """
        Initialize Hugging Face embedding provider.
        
        Args:
            parameters: Configuration parameters including:
                - embedding_model_id: Hugging Face model ID (e.g., 'sentence-transformers/all-MiniLM-L6-v2')
                - device: Device to run model on ('cpu' or 'cuda')
        """
        super().__init__(parameters)
        self._initialize_embedding()
    
    def _initialize_embedding(self) -> None:
        """
        Initialize the Hugging Face embedding model using sentence-transformers.
        """
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info("Initializing Hugging Face embedding model")
            
            model_id = self.parameters.get("embedding_model_id", "sentence-transformers/all-MiniLM-L6-v2")
            device = self.parameters.get("device", "cpu")
            
            # Initialize sentence transformer model
            self._embedding_instance = SentenceTransformer(model_id, device=device)
            
            # Set model configuration
            self._model_config = {
                "max_tokens": self._embedding_instance.max_seq_length,
                "prefix": "",
            }
            
            logger.info(f"Hugging Face embedding model initialized: {model_id} on {device}")
            
        except ImportError:
            logger.exception("sentence-transformers library not installed. Install with: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.exception(f"Failed to initialize Hugging Face embedding: {e}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents using Hugging Face model.
        Ensures texts are within token limits before embedding.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            if not self._embedding_instance:
                raise RuntimeError("Embedding model not initialized")
            
            logger.debug(f"Embedding {len(texts)} documents with Hugging Face")
            
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
                show_progress_bar=False
            )
            
            # Convert numpy arrays to lists
            vectors = [embedding.tolist() for embedding in embeddings]
            
            return vectors
            
        except Exception as e:
            logger.exception(f"Failed to embed documents: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query text using Hugging Face model.
        Ensures text is within token limits before embedding.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
        """
        try:
            if not self._embedding_instance:
                raise RuntimeError("Embedding model not initialized")
            
            logger.debug("Embedding query with Hugging Face")
            
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