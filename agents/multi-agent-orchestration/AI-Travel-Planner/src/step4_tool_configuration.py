import os
import json
from typing import Any, Dict, Optional, Union

import requests
from dotenv import load_dotenv
from wxo_token import clsAuth  # assumes you already have this implemented


class MCPToolkitError(Exception):
    """
    Custom exception for MCP Toolkit related errors.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[Union[str, Dict[str, Any]]] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class MCPToolkitClient:
    """
    Client for creating / managing MCP toolkits in Watsonx Orchestrate.

    This wraps the `/v1/orchestrate/toolkits` API and provides:
    - Configurable base URL
    - Pluggable access token
    - Structured responses
    - Error handling with useful debug information
    """

    def __init__(
        self,
        instance_base_url: str,
        access_token: str,
        *,
        timeout: int = 30,
        verify_ssl: bool = True,
    ):
        """
        Initialize the MCPToolkitClient.

        :param instance_base_url: Base URL of the Watsonx Orchestrate instance,
            e.g. "https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/<INSTANCE_ID>"
        :param access_token: IAM access token (Bearer token) for authorization.
        :param timeout: Request timeout in seconds for all HTTP calls.
        :param verify_ssl: Whether to verify SSL certificates.
        """
        # Strip any trailing slash to avoid double slashes in URLs
        self.instance_base_url = instance_base_url.rstrip("/")
        self.access_token = access_token
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    @classmethod
    def from_env(
        cls,
        *,
        token: Optional[str] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
    ) -> "MCPToolkitClient":
        """
        Convenience constructor that reads the base URL (and optionally token)
        from environment variables.

        Expected env vars:
        - WXO_SERVICE_URL  -> instance base URL

        :param token: Optional pre-fetched token. If not provided, this method
                      will call clsAuth().get_ibm_token().
        :param timeout: Request timeout in seconds.
        :param verify_ssl: Whether to verify SSL certificates.
        :return: MCPToolkitClient instance.
        """
        # Load .env if present (no-op if already loaded)
        load_dotenv()

        # Base URL of your Watsonx Orchestrate instance
        base_url = os.getenv("WXO_SERVICE_URL")
        if not base_url:
            raise ValueError(
                "Environment variable 'WXO_SERVICE_URL' is not set. "
                "Please set it to your Watsonx Orchestrate instance URL."
            )

        # If token not provided, get it via your existing auth helper
        if token is None:
            auth_object = clsAuth()
            token = auth_object.get_ibm_token()

        return cls(
            instance_base_url=base_url,
            access_token=token,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )

    def _build_headers(self) -> Dict[str, str]:
        """
        Build the default HTTP headers for API calls.

        :return: Dictionary of headers.
        """
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _handle_response(self, resp: requests.Response) -> Dict[str, Any]:
        """
        Common response handler. Returns JSON on success,
        raises MCPToolkitError on failure.

        :param resp: requests.Response object.
        :return: Parsed JSON response as a dict.
        :raises MCPToolkitError: if response status is not 2xx.
        """
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            # Try to parse JSON error, fallback to raw text
            try:
                body = resp.json()
            except ValueError:
                body = resp.text

            # Helpful debug print (optional, can be replaced with logging)
            print("Request failed:")
            print("Status:", resp.status_code)
            print("Response body:", json.dumps(body, indent=2) if isinstance(body, dict) else body)

            raise MCPToolkitError(
                message=f"HTTP {resp.status_code} error while calling MCP toolkit API.",
                status_code=resp.status_code,
                response_body=body,
            ) from e

        # Successful response: parse JSON payload
        try:
            return resp.json()
        except ValueError as e:
            # Non-JSON body is unexpected for this API
            raise MCPToolkitError(
                message="Response from MCP toolkit API is not valid JSON.",
                status_code=resp.status_code,
                response_body=resp.text,
            ) from e

    def create_mcp_toolkit(
        self,
        *,
        name: str,
        description: str,
        mcp_url: str,
        connection_appid: str,
        tools: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Create a remote MCP toolkit (e.g. Tavily) using the toolkits API.

        :param name: Toolkit name (must follow API rules: letters, digits,
                     hyphen, underscore; cannot start with a digit).
        :param description: Human-readable description of the toolkit.
        :param mcp_url: MCP server URL (e.g. Tavily MCP endpoint).
        :param connection_appid: Identifier of the connection app (must match
                                 the connection created in Watsonx Orchestrate).
        :param tools: List of tool names to expose. Use ['*'] to expose all.
                      Default: ['*'].
        :return: Parsed JSON response from the API as a dict.
                 Typically includes toolkit ID and metadata.
        :raises MCPToolkitError: on HTTP or JSON parsing errors.
        """
        # Endpoint URL for creating toolkits
        url = f"{self.instance_base_url}/v1/orchestrate/toolkits"

        # Use '*' (all tools) if not specified
        if tools is None:
            tools = ["*"]

        # Build the JSON payload. You can extend this easily with
        # more fields if needed (e.g., command, args, env, source).
        payload = {
            "name": name,
            "description": description,
            "mcp": {
                # If you use public registry instead of direct server, uncomment and adjust:
                # "source": "public-registry",
                "server_url": mcp_url,
                "tools": tools,
                "connections": {
                    "id": connection_appid
                },
            },
        }

        headers = self._build_headers()

        # Perform the HTTP POST request with timeout and SSL options
        resp = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )

        # Let the common handler validate and parse the response
        return self._handle_response(resp)

    def get_toolkit_by_id(self, toolkit_id: str) -> Dict[str, Any]:
        url = f"{self.instance_base_url}/v1/orchestrate/toolkits/{toolkit_id}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "accept": "application/json"
        }

        resp = requests.get(url, headers=headers, timeout=self.timeout, verify=self.verify_ssl)
        return self._handle_response(resp)
    
    def list_agents(
        self,
        *,
        include_hidden: bool = False,
        ids: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single agent that matches the given filters.
        """

        base_url = f"{self.instance_base_url}/v1/orchestrate/agents"

        params = {
            "include_hidden": str(include_hidden).lower(),
        }
        if ids:
            params["ids"] = ids

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "accept": "application/json",
        }

        response = requests.get(
            base_url,
            headers=headers,
            params=params,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )

        agents = self._handle_response(response)
        return agents

    def filter_agent_by_name(self, agent_list, name):
        for agent in agent_list:
            if agent["display_name"] == name:
                return agent
        return None
    
    def update_agent_tools(self, agent_id, new_tools):
        url = f"{self.instance_base_url}/v1/orchestrate/agents/{agent_id}"
        #print(url)
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        
        payload = json.dumps({
            "tools": new_tools
        })
        
        response = requests.patch(url, data=payload, headers=headers)
        print(response)
        return response

if __name__ == "__main__":
    """
    Example usage:
    - Reads config from .env
    - Creates the client
    - Calls create_mcp_toolkit and prints the server result
    """

    try:
        # Load environment variables once
        load_dotenv()

        # Build client from environment variables and clsAuth()
        client = MCPToolkitClient.from_env()

        # Load other toolkit-specific env variables
        toolkit_name = os.getenv("TOOLKIT_NAME", "my_mcp_toolkit")
        toolkit_description = os.getenv("TOOLKIT_DESCRIPTION", "My MCP toolkit description")
        mcp_url = os.getenv("MCP_URL")
        connection_app_id = os.getenv("CONNECTION_APP_ID")
        agent_name = os.getenv("AGENT_NAME")

        # Validate required environment variables
        missing_vars = [var for var, val in {
            "MCP_URL": mcp_url,
            "CONNECTION_APP_ID": connection_app_id,
            "AGENT_NAME": agent_name
        }.items() if not val]

        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        print("Using instance base URL:", client.instance_base_url)

        # Create the MCP toolkit
        result = client.create_mcp_toolkit(
            name=toolkit_name,
            description=toolkit_description,
            mcp_url=mcp_url,
            connection_appid=connection_app_id,
            tools=['*']
        )
        toolkit_id = result.get("id")
        print("Created toolkit successfully, with id:", toolkit_id)

        # Fetch toolkit details
        toolkit_details = client.get_toolkit_by_id(toolkit_id)
        print("Toolkit fetched by ID:")
        print(json.dumps(toolkit_details, indent=2))

        tools = toolkit_details.get("tools", [])
        print("Toolkit tools:", tools)

        # List all agents
        agents = client.list_agents()
        agent = client.filter_agent_by_name(agents, agent_name)

        if agent:
            agent_id = agent.get("id")
            print("Required agent found with id:", agent_id)
            # Update agent tools safely
            client.update_agent_tools(agent_id, tools)
            print("Agent tools updated successfully.")
        else:
            print(f"Agent '{agent_name}' not found. Skipping tool update.")

    except MCPToolkitError as e:
        print("MCPToolkitError occurred:")
        print("Message:", str(e))
        if e.status_code is not None:
            print("Status code:", e.status_code)
        if e.response_body is not None:
            print("Response body:", e.response_body)

    except Exception as e:
        print("Unexpected error occurred:", str(e))
