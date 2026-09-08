"""
Abstract base class for embedding providers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class BaseEmbedding(ABC):
    """
    Abstract base class for all embedding providers.
    
    All embedding providers must implement this interface to ensure
    consistent behavior across different embedding models.
    """
    
    def __init__(self, parameters: Dict[str, Any]):
        """
        Initialize the embedding provider.
        
        Args:
            parameters: Configuration parameters for the embedding provider
        """
        self.parameters = parameters
        self._embedding_instance = None
        self._model_config = None
        self._embedding_dim = None
        logger.debug(f"Initializing {self.__class__.__name__}")
    
    @abstractmethod
    def _initialize_embedding(self) -> None:
        """
        Initialize the embedding model instance.
        Must be implemented by subclasses.
        """
        pass
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        pass
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query text.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector as a list of floats
        """
        pass
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            Integer representing the embedding dimension
        """
        if self._embedding_dim is None:
            # Test with a sample text to determine dimension
            test_vector = self.embed_query("test")
            self._embedding_dim = len(test_vector)
            logger.info(f"Embedding dimension detected: {self._embedding_dim}")
        
        return self._embedding_dim
    
    def get_model_config(self) -> Dict[str, Any]:
        """
        Get the model configuration including max_tokens and prefix.
        
        Returns:
            Dictionary containing model configuration
        """
        if self._model_config is None:
            self._model_config = self._get_default_model_config()
        
        return self._model_config
    
    def _get_default_model_config(self) -> Dict[str, Any]:
        """
        Get default model configuration.
        Can be overridden by subclasses.
        
        Returns:
            Dictionary with default configuration
        """
        return {
            "max_tokens": 8000,
            "prefix": "",
        }
    
    def ensure_token_limit(self, text: str, max_tokens: Optional[int] = None) -> str:
        """
        Ensure text doesn't exceed token limit using very conservative character-based estimation.
        Uses 2 characters per token as a very safe approximation.
        
        Args:
            text: Input text
            max_tokens: Maximum number of tokens (uses model config if not provided)
            
        Returns:
            Truncated text if necessary
        """
        token_limit = max_tokens if max_tokens is not None else self.get_model_config()["max_tokens"]
        
        # Very conservative estimate: 2 characters per token
        # This ensures we stay well under the limit even for dense text
        max_chars = token_limit * 2
        
        if len(text) > max_chars:
            logger.warning(f"Text length ({len(text)} chars) exceeds estimated limit ({max_chars} chars for {token_limit} tokens). Truncating.")
            return text[:max_chars]
        
        return text
    
    def format_text(self, text: str, apply_prefix: bool = True) -> str:
        """
        Format text with model-specific prefix and token limits.
        
        Args:
            text: Input text
            apply_prefix: Whether to apply the model prefix
            
        Returns:
            Formatted text
        """
        config = self.get_model_config()
        max_tokens = config["max_tokens"]
        prefix = config["prefix"] if apply_prefix else ""
        
        # Calculate available tokens for text (accounting for prefix and safety margin)
        # Prefix typically uses 2-5 tokens, use 10 to be safe
        # Add 100 token safety margin for tokenization differences and overhead
        prefix_overhead = 10 if prefix else 0
        safety_margin = 100
        available_tokens = max_tokens - prefix_overhead - safety_margin
        
        # Apply token limit
        safe_text = self.ensure_token_limit(text, available_tokens)
        
        return f"{prefix}{safe_text}"
