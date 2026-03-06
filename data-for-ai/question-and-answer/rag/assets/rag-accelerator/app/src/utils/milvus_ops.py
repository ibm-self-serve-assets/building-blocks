import logging
from pymilvus import (
    MilvusClient,
    FieldSchema,
    CollectionSchema,
    DataType,
)

logger = logging.getLogger(__name__)


class MilvusOperations:
    """
    Milvus collection operations handler using MilvusClient API.
    """

    def __init__(self, client: MilvusClient, parameters: dict):
        self.client = client
        self.parameters = parameters

    def drop_collection(self, index_name: str) -> None:
        try:
            if self.client.has_collection(index_name):
                self.client.drop_collection(index_name)
                logger.info(f"Dropped existing Milvus collection: {index_name}")
            else:
                logger.info(f"Milvus collection '{index_name}' does not exist. No need to drop.")
        except Exception as e:
            logger.exception(f"Error while dropping collection '{index_name}': {e}")
            raise

    def create_collection(self, embedding_dim: int, index_name: str, drop_if_exists: bool = False) -> str:

        try:
            existing = self.client.list_collections()

            if index_name in existing:
                if drop_if_exists:
                    logger.info(f"Dropping existing collection: {index_name}")
                    self.client.drop_collection(index_name)
                else:
                    logger.info(
                        f"Milvus collection '{index_name}' already exists."
                    )
                    return index_name

            logger.info(f"Creating Milvus collection: {index_name}")

            hybrid_search = (self.parameters.get("milvus_hybrid_search", "false").lower()== "true")

            if hybrid_search:
                schema = self._build_hybrid_schema(embedding_dim)
            else:
                schema = self._build_dense_schema(embedding_dim)

            self.client.create_collection(
                collection_name=index_name,
                schema=schema,
                consistency_level="Strong",
            )

            index_params = self.client.prepare_index_params()

            if hybrid_search:
                # Dense vector index
                index_params.add_index(
                    field_name="dense",
                    index_type="IVF_FLAT",
                    metric_type="L2",
                    params={"nlist": 1024},
                )

                # Sparse vector index (REQUIRED)
                index_params.add_index(
                    field_name="sparse",
                    index_type="SPARSE_INVERTED_INDEX",
                    metric_type="IP",
                    params={},
                )
            else:
                # Dense-only index
                index_params.add_index(
                    field_name="vector",
                    index_type="IVF_FLAT",
                    metric_type="L2",
                    params={"nlist": 1024},
                )

            self.client.create_index(
                collection_name=index_name,
                index_params=index_params,
            )

            self.client.load_collection(index_name)

            logger.info(
                f"Milvus collection '{index_name}' created and loaded."
            )

            return index_name

        except Exception as e:
            logger.exception(
                f"Error while creating or retrieving collection '{index_name}': {e}"
            )
            raise


    def _build_dense_schema(self, embedding_dim: int):

        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.VARCHAR,
                is_primary=True,
                max_length=128,
            ),
            FieldSchema(
                name="vector",
                dtype=DataType.FLOAT_VECTOR,
                dim=embedding_dim,
            ),
            FieldSchema(
                name="title",
                dtype=DataType.VARCHAR,
                max_length=65535,
                nullable=True,
            ),
            FieldSchema(
                name="source",
                dtype=DataType.VARCHAR,
                max_length=65535,
                nullable=True,
            ),
            FieldSchema(
                name="document_url",
                dtype=DataType.VARCHAR,
                max_length=65535,
                nullable=True,
            ),
            FieldSchema(
                name="page_number",
                dtype=DataType.VARCHAR,
                max_length=64,
                nullable=True,
            ),
            FieldSchema(
                name="chunk_seq",
                dtype=DataType.INT32,
                nullable=True,
            ),
            FieldSchema(
                name="text",
                dtype=DataType.VARCHAR,
                max_length=65535,
                nullable=True, 
            ),
        ]

        return CollectionSchema(
            fields=fields,
            description="Dense vector collection",
        )

    def _build_hybrid_schema(self, embedding_dim: int):

        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.VARCHAR,
                is_primary=True,
                max_length=128,
            ),
            FieldSchema(
                name="dense",
                dtype=DataType.FLOAT_VECTOR,
                dim=embedding_dim,
            ),
            FieldSchema(
                name="sparse",
                dtype=DataType.SPARSE_FLOAT_VECTOR,
            ),
            FieldSchema(
                name="title",
                dtype=DataType.VARCHAR,
                max_length=65535,
            ),
            FieldSchema(
                name="source",
                dtype=DataType.VARCHAR,
                max_length=65535,
            ),
            FieldSchema(
                name="document_url",
                dtype=DataType.VARCHAR,
                max_length=65535,
            ),
            FieldSchema(
                name="page_number",
                dtype=DataType.VARCHAR,
                max_length=64,
            ),
            FieldSchema(
                name="chunk_seq",
                dtype=DataType.INT32,
            ),
            FieldSchema(
                name="text",
                dtype=DataType.VARCHAR,
                max_length=65535,
            ),
        ]

        return CollectionSchema(
            fields=fields,
            description="Hybrid dense + sparse collection",
        )
    
    