"""
IBM watsonx.data OpenSearch connection utility.
Uses opensearch-py with SSL/TLS for IBM watsonx.data managed OpenSearch.
"""
from __future__ import annotations
import logging
import os
from opensearchpy import OpenSearch, RequestsHttpConnection

logger = logging.getLogger(__name__)


def get_opensearch_client() -> OpenSearch:
    """Return a connected OpenSearch client using watsonx.data credentials."""
    host = os.environ["OPENSEARCH_HOST"]
    port = int(os.getenv("OPENSEARCH_PORT", "9200"))
    user = os.getenv("OPENSEARCH_USER", "admin")
    password = os.environ["OPENSEARCH_PASSWORD"]
    use_ssl = os.getenv("OPENSEARCH_USE_SSL", "true").lower() == "true"
    verify_certs = os.getenv("OPENSEARCH_VERIFY_CERTS", "false").lower() == "true"
    ca_certs = os.getenv("OPENSEARCH_CA_CERTS") or None

    client = OpenSearch(
        hosts=[{"host": host, "port": port}],
        http_auth=(user, password),
        use_ssl=use_ssl,
        verify_certs=verify_certs,
        ca_certs=ca_certs,
        connection_class=RequestsHttpConnection,
        timeout=30,
    )
    logger.info("OpenSearch client initialised: %s:%s", host, port)
    return client
