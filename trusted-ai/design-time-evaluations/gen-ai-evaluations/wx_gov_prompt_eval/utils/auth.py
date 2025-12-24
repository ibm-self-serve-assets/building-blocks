"""
Authentication utilities for IBM watsonx services.

This module provides functions for generating access tokens and managing
authentication with IBM Cloud Pak for Data.
"""

import json
import requests
from typing import Dict
import urllib3

# Disable SSL warnings for self-signed certificates (common in CPD environments)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def generate_access_token(wos_credentials: Dict[str, str]) -> str:
    """
    Generate an IAM access token for IBM Cloud Pak for Data.

    This function authenticates with the CPD platform and returns a token
    that can be used for subsequent API calls.

    Args:
        wos_credentials: Dictionary containing 'url', 'username', and 'password'

    Returns:
        IAM access token string

    Raises:
        requests.exceptions.RequestException: If authentication fails
        KeyError: If required credentials are missing

    Example:
        >>> credentials = {
        ...     "url": "https://cpd-instance.example.com",
        ...     "username": "user@example.com",
        ...     "password": "password123"
        ... }
        >>> token = generate_access_token(credentials)
    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    data = {
        "username": wos_credentials["username"],
        "password": wos_credentials["password"]
    }

    url = f"{wos_credentials['url']}/icp4d-api/v1/authorize"

    response = requests.post(
        url=url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        verify=False  # CPD often uses self-signed certificates
    )

    response.raise_for_status()  # Raise exception for bad status codes

    json_data = response.json()
    return json_data['token']


def get_user_id(wos_url: str, access_token: str) -> str:
    """
    Get the user ID (UID) from the access token.

    Args:
        wos_url: Watson OpenScale service URL
        access_token: IAM access token

    Returns:
        User ID string

    Example:
        >>> uid = get_user_id(wos_url, token)
    """
    from ibm_watson_openscale.utils.client_utils import get_cpd_decoded_token

    decoded_token = get_cpd_decoded_token(wos_url, access_token)
    return decoded_token.get("uid")
