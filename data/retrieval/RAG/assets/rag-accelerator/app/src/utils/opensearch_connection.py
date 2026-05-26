# opensearch_connection.py

import logging
from opensearchpy import OpenSearch, RequestsHttpConnection
from app.src.utils.connection import BaseConnection
from app.src.utils import config
from app.src.utils import rag_helper_functions

logger = logging.getLogger(__name__)

# Load parameters
parameter_sets = config.PARAMETERS
parameter_sets_list = list(parameter_sets.keys())
parameters = rag_helper_functions.get_parameter_sets(parameter_sets_list)


class OpenSearchConnection(BaseConnection):
    """
    OpenSearch connection using the new connection_setup logic.
    Only supports 'opensearch_connect'.
    """

    def connect(self):
        if self.parameters.get("connection_name") != "opensearch_connect":
            raise ValueError(f"Unsupported connection: {self.parameters.get('connection_name')}")

        logger.info("Connecting to OpenSearch")

        # Extract OpenSearch parameters from config
        opensearch_host = parameters.get("opensearch_host")
        opensearch_port = int(parameters.get("opensearch_port", 9200))
        opensearch_user = parameters.get("opensearch_user", "admin")
        opensearch_password = parameters.get("opensearch_password")
        opensearch_use_ssl = parameters.get("opensearch_use_ssl", "true").lower() == "true"
        opensearch_verify_certs = parameters.get("opensearch_verify_certs", "false").lower() == "true"
        opensearch_ca_certs = parameters.get("opensearch_ca_certs")

        if not opensearch_host:
            raise ValueError("OpenSearch host is required")
        if not opensearch_password:
            raise ValueError("OpenSearch password is required")

        db_connection = {
            "hosts": [{"host": opensearch_host, "port": opensearch_port}],
            "http_auth": (opensearch_user, opensearch_password),
            "use_ssl": opensearch_use_ssl,
            "verify_certs": opensearch_verify_certs,
            "connection_class": RequestsHttpConnection,
            "timeout": 30,
            "max_retries": 3,
            "retry_on_timeout": True,
        }

        # Add CA certs if provided
        if opensearch_ca_certs:
            db_connection["ca_certs"] = opensearch_ca_certs

        client = OpenSearch(**db_connection)

        # Verify connection
        if not client.ping():
            raise ConnectionError(f"OpenSearch ping failed at {opensearch_host}:{opensearch_port}")

        logger.info("OpenSearch connection established")
        
        # Return client and connection args for compatibility
        connection_args = {
            "host": opensearch_host,
            "port": opensearch_port,
            "user": opensearch_user,
            "use_ssl": opensearch_use_ssl,
        }
        
        return client, connection_args
