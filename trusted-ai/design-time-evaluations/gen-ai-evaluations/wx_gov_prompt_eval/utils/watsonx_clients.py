"""
Client creation utilities for IBM watsonx services.

This module provides functions to create and configure clients for
Watson OpenScale, Watson Machine Learning, and AI Governance Facts.
"""

from typing import Dict, Optional
from ibm_watson_openscale import APIClient
from ibm_cloud_sdk_core.authenticators import CloudPakForDataAuthenticator
from ibm_watson_machine_learning import APIClient as WMLAPIClient
from ibm_aigov_facts_client import AIGovFactsClient, CloudPakforDataConfig


def create_wos_client(wos_credentials: Dict[str, str]) -> APIClient:
    """
    Create and configure a Watson OpenScale API client.

    Args:
        wos_credentials: Dictionary containing 'url', 'username', and 'password'

    Returns:
        Configured Watson OpenScale APIClient instance

    Example:
        >>> credentials = {
        ...     "url": "https://cpd-instance.example.com",
        ...     "username": "user@example.com",
        ...     "password": "password123"
        ... }
        >>> wos_client = create_wos_client(credentials)
    """
    authenticator = CloudPakForDataAuthenticator(
        url=wos_credentials['url'],
        username=wos_credentials['username'],
        password=wos_credentials['password'],
        disable_ssl_verification=True
    )

    wos_client = APIClient(
        service_url=wos_credentials['url'],
        authenticator=authenticator
    )

    return wos_client


def create_wml_client(wml_credentials: Dict[str, str]) -> WMLAPIClient:
    """
    Create and configure a Watson Machine Learning API client.

    Args:
        wml_credentials: Dictionary containing 'url', 'username', 'password',
                        'instance_id', and 'version'

    Returns:
        Configured Watson Machine Learning APIClient instance

    Example:
        >>> credentials = {
        ...     "url": "https://cpd-instance.example.com",
        ...     "username": "user@example.com",
        ...     "password": "password123",
        ...     "instance_id": "wml_local",
        ...     "version": "5.0"
        ... }
        >>> wml_client = create_wml_client(credentials)
    """
    wml_client = WMLAPIClient(wml_credentials)
    return wml_client


def create_facts_client(
    wos_credentials: Dict[str, str],
    container_id: str,
    container_type: str = "project"
) -> AIGovFactsClient:
    """
    Create and configure an AI Governance Facts client.

    This client is used for creating and managing prompt template assets
    with factsheet tracking.

    Args:
        wos_credentials: Dictionary containing 'url', 'username', and 'password'
        container_id: ID of the container (project or space)
        container_type: Type of container ("project" or "space")

    Returns:
        Configured AIGovFactsClient instance

    Example:
        >>> credentials = {
        ...     "url": "https://cpd-instance.example.com",
        ...     "username": "user@example.com",
        ...     "password": "password123"
        ... }
        >>> facts_client = create_facts_client(
        ...     credentials,
        ...     container_id="project-123",
        ...     container_type="project"
        ... )
    """
    creds = CloudPakforDataConfig(
        service_url=wos_credentials["url"],
        username=wos_credentials["username"],
        password=wos_credentials["password"]
    )

    facts_client = AIGovFactsClient(
        cloud_pak_for_data_configs=creds,
        container_id=container_id,
        container_type=container_type,
        disable_tracing=True
    )

    return facts_client


def create_generative_ai_evaluator(
    wos_client: APIClient,
    wos_url: str,
    access_token: str,
    model_id: str = "meta-llama/llama-3-1-8b-instruct",
    evaluator_name: str = "LLM as a Judge",
    evaluator_description: str = "Evaluation through LLM as a judge"
) -> str:
    """
    Create a generative AI evaluator integrated system in OpenScale.

    This function creates an evaluator that uses an LLM to judge the quality
    of generated responses.

    Args:
        wos_client: Watson OpenScale API client
        wos_url: Watson OpenScale service URL
        access_token: IAM access token
        model_id: Model ID for the judge LLM
        evaluator_name: Name for the evaluator
        evaluator_description: Description for the evaluator

    Returns:
        Evaluator integrated system ID

    Example:
        >>> evaluator_id = create_generative_ai_evaluator(
        ...     wos_client=wos_client,
        ...     wos_url="https://cpd-instance.example.com",
        ...     access_token=token,
        ...     model_id="meta-llama/llama-3-1-8b-instruct"
        ... )
    """
    from ibm_watson_openscale.utils.client_utils import get_cpd_decoded_token

    uid = get_cpd_decoded_token(wos_url, access_token).get("uid")

    gen_ai_evaluator = wos_client.integrated_systems.add(
        name=evaluator_name,
        description=evaluator_description,
        type="generative_ai_evaluator",
        parameters={
            "evaluator_type": "watsonx.ai",
            "model_id": model_id
        },
        credentials={
            "wml_location": "cpd_local",
            "uid": uid,
            "url": wos_url,
        }
    )

    result = gen_ai_evaluator.result._to_dict()
    evaluator_id = result["metadata"]["id"]

    return evaluator_id
