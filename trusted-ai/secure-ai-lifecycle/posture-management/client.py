"""
Core client for LLM Penetration Testing API.

Handles authentication and provides access to specialized managers.
"""

import os
from typing import Dict, Any, Optional, Literal
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("api_url")
ORGANIZATION_ID = os.getenv("organization_id")
API_KEY = os.getenv("api_key")

class PostureManagementClient:

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        customer_id: Optional[str] = None
    ):
        """
        Initialize the LLM Pentest Client.

        Args:
            api_url: Base URL for the API. Defaults to API_URL environment variable.
            api_key: API key for authentication. Defaults to API_KEY environment variable.
            customer_id: Customer ID. Defaults to CUSTOMER_ID environment variable.

        Raises:
            ValueError: If required configuration is missing.
            ConnectionError: If authentication fails.
        """
        self.api_url = api_url or os.environ.get("API_URL")
        self.api_key = api_key or os.environ.get("API_KEY")
        self.customer_id = customer_id or os.environ.get("CUSTOMER_ID")

        if not all([self.api_url, self.api_key, self.customer_id]):
            raise ValueError(
                "API_URL, API_KEY, and CUSTOMER_ID must be provided either as "
                "arguments or environment variables"
            )

        self.jwt_token: Optional[str] = None
        self._authenticate()



    def _authenticate(self) -> None:
        endpoint = f"{API_URL}/v1/auth/issue-jwt-token"
        headers = {"X-API-Key": API_KEY}
        try:
            response = requests.post(endpoint, headers=headers)
            response.raise_for_status()
            self.jwt_token = response.json()["access_token"]
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to authenticate: {e}")

    def make_request(
            self,
            endpoint: str,
            method: Literal["GET", "POST", "PUT", "DELETE"] = "GET",
            data: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
        """
            Make an authenticated API request.

        Args:
            endpoint: API endpoint path (without base URL).
            method: HTTP method to use.
            data: Request body data for POST/PUT requests.

        Returns:
            Response JSON as dictionary.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
        url = f"{self.api_url}{endpoint}"

        response = requests.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

test_client = PostureManagementClient()
test_client.make_request("", method="GET")