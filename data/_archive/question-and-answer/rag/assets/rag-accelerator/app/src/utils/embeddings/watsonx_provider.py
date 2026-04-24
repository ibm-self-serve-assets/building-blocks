"""
Watsonx AI embedding provider implementation.
"""

from typing import List, Dict, Any
import logging

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Embeddings

from .base import BaseEmbedding

logger = logging.getLogger(__name__)


class WatsonxEmbedding(BaseEmbedding):
    """
    Watsonx AI embedding provider using IBM Watsonx AI Foundation Models.
    """
    
    def __init__(self, parameters: Dict[str, Any]):
        """
        Initialize Watsonx AI embedding provider.
        
        Args:
            parameters: Configuration parameters including:
                - watsonx_ai_api_key: IBM Cloud API key
                - watsonx_url: Watsonx AI service URL
                - watsonx_project_id: Project ID
                - embedding_model_id: Model ID for embeddings
        """
        super().__init__(parameters)
        self._initialize_embedding()
    
    def _initialize_embedding(self) -> None:
        """
        Initialize the Watsonx AI embedding model.
        """
        try:
            logger.info("Initializing Watsonx AI embedding model")
            
            # Create credentials
            credentials = Credentials(
                api_key=self.parameters["watsonx_ai_api_key"],
                url=self.parameters["watsonx_url"],
            )
            
            model_id = self.parameters["embedding_model_id"]
            project_id = self.parameters["watsonx_project_id"]
            
            # Initialize embedding model
            self._embedding_instance = Embeddings(
                model_id=model_id,
                credentials=credentials,
                project_id=project_id,
                verify=True,
            )
            
            # Set model configuration based on model type
            self._model_config = self._determine_model_config(model_id)
            
            logger.info(f"Watsonx AI embedding model initialized: {model_id}")
            
        except Exception as e:
            logger.exception(f"Failed to initialize Watsonx AI embedding: {e}")
            raise
    
    def _determine_model_config(self, model_id: str) -> Dict[str, Any]:
        """
        Determine model configuration based on model ID.
        
        Args:
            model_id: The embedding model ID
            
        Returns:
            Dictionary with model configuration
        """
        model_id_lower = model_id.lower()
        
        # E5 models have specific requirements
        if "e5" in model_id_lower:
            return {
                "max_tokens": 512,
                "prefix": "passage: ",
            }
        else:
            return {
                "max_tokens": 8000,
                "prefix": "",
            }
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents using Watsonx AI.
        Handles token limits by truncating texts that exceed the model's capacity.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            if not self._embedding_instance:
                raise RuntimeError("Embedding model not initialized")
            
            logger.debug(f"Embedding {len(texts)} documents with Watsonx AI")
            
            # Get model token limit and apply aggressive safety margin
            model_max_tokens = self._model_config.get("max_tokens", 512)
            # Use 80% of the limit to be extra safe (e.g., 512 * 0.8 = 409 tokens)
            safe_token_limit = int(model_max_tokens * 0.8)
            
            safe_texts = []
            
            for i, text in enumerate(texts):
                # Use the base class method to ensure token limit with safety margin
                safe_text = self.ensure_token_limit(text, safe_token_limit)
                safe_texts.append(safe_text)
                
                # Log if truncation occurred
                if len(safe_text) < len(text):
                    logger.warning(f"Document {i} truncated from {len(text)} to {len(safe_text)} characters (limit: {safe_token_limit} tokens)")
            
            # Call the embedding API with safe texts
            vectors = self._embedding_instance.embed_documents(safe_texts)
            
            return vectors
            
        except Exception as e:
            logger.exception(f"Failed to embed documents: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query text using Watsonx AI.
        Handles token limits by truncating text that exceeds the model's capacity.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
        """
        try:
            if not self._embedding_instance:
                raise RuntimeError("Embedding model not initialized")
            
            logger.debug("Embedding query with Watsonx AI")
            
            # Get model token limit and apply aggressive safety margin
            model_max_tokens = self._model_config.get("max_tokens", 512)
            # Use 80% of the limit to be extra safe
            safe_token_limit = int(model_max_tokens * 0.8)
            
            # Ensure text is within token limits
            safe_text = self.ensure_token_limit(text, safe_token_limit)
            
            # Log if truncation occurred
            if len(safe_text) < len(text):
                logger.warning(f"Query truncated from {len(text)} to {len(safe_text)} characters (limit: {safe_token_limit} tokens)")
            
            # Use embed_documents for single query (returns list of vectors)
            vectors = self._embedding_instance.embed_documents([safe_text])
            
            return vectors[0]
            
        except Exception as e:
            logger.exception(f"Failed to embed query: {e}")
            raise
