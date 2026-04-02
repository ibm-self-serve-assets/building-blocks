import os
import json
from typing import Any, Dict, Optional, Union, List

import requests
from dotenv import load_dotenv
from wxo_token import clsAuth 


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
        """
        load_dotenv()

        base_url = os.getenv("WXO_SERVICE_URL")
        if not base_url:
            raise ValueError(
                "Environment variable 'WXO_SERVICE_URL' is not set. "
                "Please set it to your Watsonx Orchestrate instance URL."
            )

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
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _payload_tavily(self, name, description, mcp_url, tools, connection_appid):
        return {
            "name": name,
            "description": description,
            "mcp": {
                "server_url": mcp_url,
                "tools": tools,
                "connections": {"id": connection_appid},
            },
        }

    def _payload_airbnb(self, name, description, tools):
        return {
            "name": name,
            "description": description,
            "mcp": {
                "source": "public-registry",
                "tools": tools,
                "command": "npx",
                "args": ["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
            },
        }

    def _handle_response(self, resp: requests.Response) -> Dict[str, Any]:
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            try:
                body = resp.json()
            except ValueError:
                body = resp.text

            print("Request failed:")
            print("Status:", resp.status_code)
            print(
                "Response body:",
                json.dumps(body, indent=2) if isinstance(body, dict) else body,
            )

            raise MCPToolkitError(
                message=f"HTTP {resp.status_code} error while calling MCP toolkit API.",
                status_code=resp.status_code,
                response_body=body,
            ) from e

        try:
            return resp.json()
        except ValueError as e:
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
        tool_name: str,
        tools: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Create a remote MCP toolkit (e.g. Tavily or Airbnb) using the toolkits API.
        """
        url = f"{self.instance_base_url}/v1/orchestrate/toolkits"

        if tools is None:
            tools = ["*"]

        builders = {
            "TAVILY": lambda: self._payload_tavily(
                name, description, mcp_url, tools, connection_appid
            ),
            "AIRBNB": lambda: self._payload_airbnb(name, description, tools),
        }

        key = tool_name.upper()
        if key not in builders:
            raise ValueError(f"Unsupported tool_name: {tool_name}")

        payload = builders[key]()
        headers = self._build_headers()

        resp = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )

        return self._handle_response(resp)

    def get_toolkit_by_id(self, toolkit_id: str) -> Dict[str, Any]:
        url = f"{self.instance_base_url}/v1/orchestrate/toolkits/{toolkit_id}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "accept": "application/json",
        }

        resp = requests.get(
            url, headers=headers, timeout=self.timeout, verify=self.verify_ssl
        )
        return self._handle_response(resp)

    def list_agents(
        self,
        *,
        include_hidden: bool = False,
        ids: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
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
            if agent.get("display_name") == name:
                return agent
        return None

    def update_agent_tools(self, agent_id, new_tools):
        url = f"{self.instance_base_url}/v1/orchestrate/agents/{agent_id}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

        payload = json.dumps({"tools": new_tools})

        response = requests.patch(url, data=payload, headers=headers)
        print(response)
        return response


def merge_tools(*tool_lists: List[Any]) -> List[Any]:
    """
    Merge multiple tool lists (from different toolkits) into one,
    avoiding duplicates. Works whether tools are dicts or strings.
    """
    merged = []
    seen = set()

    for tool_list in tool_lists:
        if not tool_list:
            continue
        for t in tool_list:
            if isinstance(t, dict):
                key = t.get("id") or t.get("name") or json.dumps(t, sort_keys=True)
            else:
                key = str(t)

            if key in seen:
                continue
            seen.add(key)
            merged.append(t)

    return merged


if __name__ == "__main__":
    """
    Example usage:
    - Reads config from .env
    - Creates Tavily toolkit (2 tools)
    - Creates Airbnb toolkit (2 tools)
    - Merges toolkit tool IDs
    - Updates agent with exactly 4 tools
    """

    try:
        load_dotenv()

        client = MCPToolkitClient.from_env()

        agent_name = os.getenv("AGENT_NAME")
        if not agent_name:
            raise ValueError("Environment variable 'AGENT_NAME' is required.")

        print("Using instance base URL:", client.instance_base_url)

        # TAVILY TOOLKIT
        toolkit_name = os.getenv("TAVILY_TOOLKIT_NAME", "my_mcp_toolkit_1")
        toolkit_description = os.getenv(
            "TAVILY_TOOLKIT_DESCRIPTION", "my_mcp_toolkit description"
        )

        tavily_tool_name_search = os.getenv(
            "TAVILY_TOOL_NAME_SEARCH", "tavily_search"
        )
        tavily_tool_name_extract = os.getenv(
            "TAVILY_TOOL_NAME_EXTRACT", "tavily_extract"
        )
        tavily_tools_requested = [
            tavily_tool_name_search,
            tavily_tool_name_extract,
        ]

        mcp_url = os.getenv("TAVILY_MCP_URL")
        connection_app_id = os.getenv("TAVILY_CONNECTION_APP_ID")

        missing_vars = [
            var
            for var, val in {
                "TAVILY_MCP_URL": mcp_url,
                "TAVILY_CONNECTION_APP_ID": connection_app_id,
            }.items()
            if not val
        ]
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        print(f"\n=== Creating Tavily toolkit: {toolkit_name} ===")
        tavily_result = client.create_mcp_toolkit(
            name=toolkit_name,
            description=toolkit_description,
            mcp_url=mcp_url,
            connection_appid=connection_app_id,
            tool_name="TAVILY",
            tools=tavily_tools_requested,
        )
        tavily_toolkit_id = tavily_result.get("id")
        print("Created Tavily toolkit successfully, with id:", tavily_toolkit_id)

        tavily_toolkit_details = client.get_toolkit_by_id(tavily_toolkit_id)
        print("Tavily toolkit fetched by ID:")
        print(json.dumps(tavily_toolkit_details, indent=2))

        # These are IDs for tavily_search + tavily_extract
        tavily_tools = tavily_toolkit_details.get("tools", [])
        print("Tavily toolkit tools (GUIDs):", tavily_tools)

        # AIRBNB TOOLKIT
        airbnb_toolkit_name = os.getenv("AIRBNB_TOOLKIT_NAME")
        airbnb_toolkit_description = os.getenv(
            "AIRBNB_TOOLKIT_DESCRIPTION", "This is travel planner Airbnb server"
        )
        airbnb_tool_name_search = os.getenv(
            "AIRBNB_TOOL_NAME_SEARCH", "airbnb_search"
        )
        airbnb_tool_name_listing = os.getenv(
            "AIRBNB_TOOL_NAME_LISTING_DETAILS", "airbnb_listing_details"
        )
        airbnb_tools_requested = [
            airbnb_tool_name_search,
            airbnb_tool_name_listing,
        ]

        airbnb_tools = []

        if airbnb_toolkit_name:
            print(f"\n=== Creating Airbnb toolkit: {airbnb_toolkit_name} ===")
            airbnb_result = client.create_mcp_toolkit(
                name=airbnb_toolkit_name,
                description=airbnb_toolkit_description,
                mcp_url="",          # Not used for Airbnb
                connection_appid="", # Not used for Airbnb
                tool_name="AIRBNB",
                tools=airbnb_tools_requested,
            )
            airbnb_toolkit_id = airbnb_result.get("id")
            print("Created Airbnb toolkit successfully, with id:", airbnb_toolkit_id)

            airbnb_toolkit_details = client.get_toolkit_by_id(airbnb_toolkit_id)
            print("Airbnb toolkit fetched by ID:")
            print(json.dumps(airbnb_toolkit_details, indent=2))

            # These are  IDs for airbnb_search + airbnb_listing_details
            airbnb_tools = airbnb_toolkit_details.get("tools", [])
            print("Airbnb toolkit tools (GUIDs):", airbnb_tools)
        else:
            print("AIRBNB_TOOLKIT_NAME not set. Skipping Airbnb toolkit creation.")

        # MERGE TOOLS (Tavily + Airbnb)
        merged_tools = merge_tools(tavily_tools, airbnb_tools)
        print("Merged tools count (should be 2–4):", len(merged_tools))
        print("Merged tools:", merged_tools)

        # UPDATE AGENT
        agents = client.list_agents()
        agent = client.filter_agent_by_name(agents, agent_name)

        if agent:
            agent_id = agent.get("id")
            print("Required agent found with id:", agent_id)
            client.update_agent_tools(agent_id, merged_tools)
            print("Agent tools updated successfully with Tavily + Airbnb.")
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