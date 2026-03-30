import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class OpenSearchOperations:
    """
    OpenSearch index operations handler using OpenSearch client API.
    """

    def __init__(self, client: Any, parameters: dict):
        self.client = client
        self.parameters = parameters

    def drop_index(self, index_name: str) -> None:
        """
        Drop an OpenSearch index if it exists.
        
        Args:
            index_name: Name of the index to drop
        """
        try:
            if self.client.indices.exists(index=index_name):
                self.client.indices.delete(index=index_name)
                logger.info(f"Dropped existing OpenSearch index: {index_name}")
            else:
                logger.info(f"OpenSearch index '{index_name}' does not exist. No need to drop.")
        except Exception as e:
            logger.exception(f"Error while dropping index '{index_name}': {e}")
            raise

    def create_index(self, embedding_dim: int, index_name: str, drop_if_exists: bool = False) -> str:
        """
        Create an OpenSearch index with KNN vector mapping.
        
        Args:
            embedding_dim: Dimension of the embedding vectors
            index_name: Name of the index to create
            drop_if_exists: If True, drop existing index before creating
            
        Returns:
            The index name
        """
        try:
            # Check if index exists
            index_exists = self.client.indices.exists(index=index_name)

            if index_exists:
                if drop_if_exists:
                    logger.info(f"Dropping existing index: {index_name}")
                    self.client.indices.delete(index=index_name)
                else:
                    logger.info(f"OpenSearch index '{index_name}' already exists.")
                    return index_name

            logger.info(f"Creating OpenSearch index: {index_name}")

            # Build index settings and mappings
            index_body = self._build_index_body(embedding_dim)

            # Create the index
            self.client.indices.create(index=index_name, body=index_body)

            logger.info(f"OpenSearch index '{index_name}' created successfully.")

            return index_name

        except Exception as e:
            logger.exception(f"Error while creating or retrieving index '{index_name}': {e}")
            raise

    def _build_index_body(self, embedding_dim: int) -> Dict[str, Any]:
        """
        Build the index body with settings and mappings for OpenSearch.
        
        Args:
            embedding_dim: Dimension of the embedding vectors
            
        Returns:
            Dictionary containing index settings and mappings
        """
        index_body = {
            "settings": {
                "index": {
                    "knn": True,
                    "knn.algo_param.ef_search": 100,
                    "number_of_shards": int(self.parameters.get("es_number_of_shards", 1)),
                    "number_of_replicas": 1,
                }
            },
            "mappings": {
                "properties": {
                    "id": {
                        "type": "keyword"
                    },
                    "vector": {
                        "type": "knn_vector",
                        "dimension": embedding_dim,
                        "method": {
                            "name": "hnsw",
                            "space_type": "cosinesimil",
                            "engine": "lucene",
                            "parameters": {
                                "ef_construction": 128,
                                "m": 16
                            }
                        }
                    },
                    "title": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword"
                            }
                        }
                    },
                    "source": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword"
                            }
                        }
                    },
                    "document_url": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword"
                            }
                        }
                    },
                    "page_number": {
                        "type": "keyword"
                    },
                    "chunk_seq": {
                        "type": "integer"
                    },
                    "text": {
                        "type": "text",
                        "analyzer": "standard"
                    }
                }
            }
        }

        return index_body

    def index_exists(self, index_name: str) -> bool:
        """
        Check if an index exists.
        
        Args:
            index_name: Name of the index to check
            
        Returns:
            True if index exists, False otherwise
        """
        try:
            return self.client.indices.exists(index=index_name)
        except Exception as e:
            logger.exception(f"Error checking if index '{index_name}' exists: {e}")
            return False
    
    def list_indices(self) -> list:
        """
        List all indices in OpenSearch.
        
        Returns:
            List of index names
        """
        try:
            # Get all indices
            indices = self.client.indices.get_alias(index="*")
            index_names = list(indices.keys())
            logger.info(f"Found {len(index_names)} OpenSearch indices")
            return index_names
        except Exception as e:
            logger.exception(f"Error while listing indices: {e}")
            raise
    
    def delete_index(self, index_name: str) -> None:
        """
        Delete an OpenSearch index.
        
        Args:
            index_name: Name of the index to delete
        """
        try:
            if self.client.indices.exists(index=index_name):
                self.client.indices.delete(index=index_name)
                logger.info(f"Successfully deleted OpenSearch index: {index_name}")
            else:
                logger.warning(f"OpenSearch index '{index_name}' does not exist. Cannot delete.")
                raise ValueError(f"Index '{index_name}' does not exist")
        except Exception as e:
            logger.exception(f"Error while deleting index '{index_name}': {e}")
            raise
