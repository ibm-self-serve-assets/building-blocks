from typing import Dict, Any
from app.src.utils.milvus_connection import MilvusConnection
from app.src.utils.opensearch_connection import OpenSearchConnection
from app.src.utils.connection import BaseConnection


class ConnectionFactory:

    @staticmethod
    def create_connection(connection_name: str, parameters: Dict[str, Any]) -> BaseConnection:
        if connection_name == "milvus_connect":
            return MilvusConnection(parameters)
        elif connection_name == "opensearch_connect":
            return OpenSearchConnection(parameters)

        raise ValueError(f"Unsupported connection type: {connection_name}")