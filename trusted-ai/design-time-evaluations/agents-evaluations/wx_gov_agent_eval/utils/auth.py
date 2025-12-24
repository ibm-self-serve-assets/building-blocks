"""
Authentication and environment setup utilities.

This module handles IBM Cloud API authentication and environment configuration.
"""

import os
import getpass
from typing import Tuple, Optional


def setup_environment(
    apikey: Optional[str] = None,
    project_id: Optional[str] = None,
    interactive: bool = False
) -> Tuple[str, str]:
    """Set up environment variables for watsonx.governance authentication.

    Args:
        apikey: IBM Cloud API key (optional, will use env var or prompt if not provided).
        project_id: Watsonx project ID (optional, will use env var or prompt if not provided).
        interactive: If True, prompt for missing credentials.

    Returns:
        Tuple of (apikey, project_id).

    Raises:
        ValueError: If credentials are not provided and not available in environment.

    Example:
        ```python
        # Interactive setup
        apikey, project_id = setup_environment(interactive=True)

        # From environment variables
        apikey, project_id = setup_environment()

        # Explicit credentials
        apikey, project_id = setup_environment(
            apikey="your-api-key",
            project_id="your-project-id"
        )
        ```
    """
    # Try provided values first
    final_apikey = apikey or os.getenv("WATSONX_APIKEY")
    final_project_id = project_id or os.getenv("WATSONX_PROJECT_ID")

    # If interactive and missing, prompt
    if interactive:
        if not final_apikey:
            final_apikey = getpass.getpass("WATSONX_APIKEY: ")
        if not final_project_id:
            final_project_id = getpass.getpass("WATSONX_PROJECT_ID: ")

    # Validate
    if not final_apikey or not final_project_id:
        raise ValueError(
            "WATSONX_APIKEY and WATSONX_PROJECT_ID must be provided via "
            "parameters, environment variables, or interactive input"
        )

    # Set environment variables
    os.environ["WATSONX_APIKEY"] = final_apikey
    os.environ["WATSONX_PROJECT_ID"] = final_project_id

    return final_apikey, final_project_id


def get_api_credentials() -> Tuple[str, str]:
    """Get API credentials from environment.

    Returns:
        Tuple of (apikey, project_id).

    Raises:
        ValueError: If credentials are not set in environment.

    Example:
        ```python
        apikey, project_id = get_api_credentials()
        ```
    """
    apikey = os.getenv("WATSONX_APIKEY")
    project_id = os.getenv("WATSONX_PROJECT_ID")

    if not apikey or not project_id:
        raise ValueError(
            "WATSONX_APIKEY and WATSONX_PROJECT_ID must be set in environment. "
            "Use setup_environment() to configure."
        )

    return apikey, project_id


def _set_env(var: str) -> None:
    """Internal helper to set environment variable with prompt.

    Args:
        var: Environment variable name.
    """
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")
