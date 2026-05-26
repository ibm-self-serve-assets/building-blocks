"""
Factory class for creating embedding providers.
"""

from typing import Dict, Any
import logging

from .base import BaseEmbedding
from .watsonx_provider import WatsonxEmbedding
from .huggingface_provider import HuggingFaceEmbedding
from .local_provider import LocalEmbedding

logger = logging.getLogger(__name__)


class EmbeddingFactory:
    """
    Factory class for creating embedding provider instances.
    Similar to ConnectionFactory pattern used in the codebase.
    """
    
    # Registry of available embedding providers
    _providers = {
        "watsonx": WatsonxEmbedding,
        "huggingface": HuggingFaceEmbedding,
        "local": LocalEmbedding,
    }
    
    @classmethod
    def create_embedding(cls, provider: str, parameters: Dict[str, Any]) -> BaseEmbedding:
        """
        Create an embedding provider instance based on the provider type.
        
        Args:
            provider: The embedding provider type ('watsonx', 'huggingface', 'local')
            parameters: Configuration parameters for the embedding provider
            
        Returns:
            An instance of the requested embedding provider
            
        Raises:
            ValueError: If the provider type is not supported
        """
        provider_lower = provider.lower()
        
        if provider_lower not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unsupported embedding provider: {provider}. "
                f"Available providers: {available}"
            )
        
        logger.info(f"Creating embedding provider: {provider}")
        
        try:
            provider_class = cls._providers[provider_lower]
            embedding_instance = provider_class(parameters)
            
            logger.info(f"Successfully created {provider} embedding provider")
            return embedding_instance
            
        except Exception as e:
            logger.exception(f"Failed to create {provider} embedding provider: {e}")
            raise
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        """
        Register a new embedding provider.
        
        Args:
            name: Name of the provider
            provider_class: Class implementing BaseEmbedding
        """
        if not issubclass(provider_class, BaseEmbedding):
            raise TypeError(f"{provider_class} must inherit from BaseEmbedding")
        
        cls._providers[name.lower()] = provider_class
        logger.info(f"Registered new embedding provider: {name}")
    
    @classmethod
    def get_available_providers(cls) -> list:
        """
        Get list of available embedding providers.
        
        Returns:
            List of provider names
        """
        return list(cls._providers.keys())
