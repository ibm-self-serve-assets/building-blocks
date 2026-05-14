# milvus_connection.py

import logging
from pymilvus import MilvusClient
from app.src.utils.connection import BaseConnection
from app.src.utils import config
from app.src.utils import rag_helper_functions

logger = logging.getLogger(__name__)

# Load parameters
parameter_sets = config.PARAMETERS
parameter_sets_list = list(parameter_sets.keys())
parameters = rag_helper_functions.get_parameter_sets(parameter_sets_list)


class MilvusConnection(BaseConnection):
    """
    Milvus connection using the new connection_setup logic.
    Only supports 'milvus_connect'.
    """

    def connect(self):
        if self.parameters.get("connection_name") != "milvus_connect":
            raise ValueError(f"Unsupported connection: {self.parameters.get('connection_name')}")

        logger.info("Connecting to Milvus")

        db_connection = {
            "uri": f"https://{parameters['milvus_host']}:{parameters['milvus_port']}",
            "token": f"{parameters['milvus_user']}:{parameters['milvus_password']}",
            "database": parameters.get("milvus_database", "default"),
            "secure": parameters["milvus_ssl"].lower() == "true",
        }

        client = MilvusClient(**db_connection)

        logger.info("MilvusClient connection established")
        return client, db_connection