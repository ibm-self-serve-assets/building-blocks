# ================================================================
# ================ BUSINESS LOGIC (ORIGINAL, UNMODIFIED) ==========
# ================================================================

import os
import json
from typing import Any, Dict, Optional, Union

import requests
from dotenv import load_dotenv
from wxo_token import clsAuth


class MCPToolkitError(Exception):
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
    def __init__(
        self,
        instance_base_url: str,
        access_token: str,
        *,
        timeout: int = 30,
        verify_ssl: bool = True,
    ):
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
        load_dotenv()
        base_url = os.getenv("WXO_SERVICE_URL")
        if not base_url:
            raise ValueError(
                "Environment variable 'WXO_SERVICE_URL' is not set."
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

    def _handle_response(self, resp: requests.Response) -> Dict[str, Any]:
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            try:
                body = resp.json()
            except ValueError:
                body = resp.text

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
        tools: Optional[list] = None,
    ) -> Dict[str, Any]:
        url = f"{self.instance_base_url}/v1/orchestrate/toolkits"
        if tools is None:
            tools = ["*"]

        payload = {
            "name": name,
            "description": description,
            "mcp": {
                "server_url": mcp_url,
                "tools": tools,
                "connections": {
                    "id": connection_appid
                },
            },
        }

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
            "accept": "application/json"
        }

        resp = requests.get(url, headers=headers, timeout=self.timeout, verify=self.verify_ssl)
        return self._handle_response(resp)

    def list_agents(self, *, include_hidden: bool = False, ids: Optional[str] = None):
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

        return self._handle_response(response)

    def filter_agent_by_name(self, agent_list, name):
        for agent in agent_list:
            if agent["display_name"] == name:
                return agent
        return None

    def update_agent_tools(self, agent_id, new_tools):
        url = f"{self.instance_base_url}/v1/orchestrate/agents/{agent_id}"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

        payload = json.dumps({"tools": new_tools})

        response = requests.patch(url, data=payload, headers=headers)
        return response


# ================================================================
# ========================== DASH UI ==============================
# ================================================================

import dash
from dash import Dash, html, dcc, Input, Output, State

load_dotenv()

DEFAULT_TOOLKIT_NAME = os.getenv("TOOLKIT_NAME", "")
DEFAULT_TOOLKIT_DESC = os.getenv("TOOLKIT_DESCRIPTION", "")
DEFAULT_MCP_URL = os.getenv("MCP_URL", "")
DEFAULT_CONN_ID = os.getenv("CONNECTION_APP_ID", "")
DEFAULT_AGENT_NAME = os.getenv("AGENT_NAME", "")

app = Dash(__name__)

app.layout = html.Div(style={"maxWidth": "800px", "margin": "40px auto"}, children=[

    html.H2("Watsonx Orchestrate – MCP Toolkit Automation"),

    html.Label("Toolkit Name"),
    dcc.Input(
        id="input-toolkit-name",
        type="text",
        value=DEFAULT_TOOLKIT_NAME,
        style={"width": "100%", "marginBottom": "12px"}
    ),

    html.Label("Toolkit Description"),
    dcc.Textarea(
        id="input-toolkit-desc",
        value=DEFAULT_TOOLKIT_DESC,
        style={"width": "100%", "marginBottom": "12px", "height": "80px"}
    ),

    html.Label("MCP Server URL"),
    dcc.Input(
        id="input-mcp-url",
        type="text",
        value=DEFAULT_MCP_URL,
        style={"width": "100%", "marginBottom": "12px"}
    ),

    html.Label("Connection App ID"),
    dcc.Input(
        id="input-connection-id",
        type="text",
        value=DEFAULT_CONN_ID,
        style={"width": "100%", "marginBottom": "12px"}
    ),

    html.Label("Agent Name (to update tools)"),
    dcc.Input(
        id="input-agent-name",
        type="text",
        value=DEFAULT_AGENT_NAME,
        style={"width": "100%", "marginBottom": "20px"}
    ),

    html.Button(
        "Run Full Workflow",
        id="btn-run",
        n_clicks=0,
        style={"padding": "10px 20px"}
    ),

    html.Hr(),

    html.Div(id="output-panel")
])


# ================================================================
# ========================== CALLBACK =============================
# ================================================================

@app.callback(
    Output("output-panel", "children"),
    Input("btn-run", "n_clicks"),
    State("input-toolkit-name", "value"),
    State("input-toolkit-desc", "value"),
    State("input-mcp-url", "value"),
    State("input-connection-id", "value"),
    State("input-agent-name", "value"),
    prevent_initial_call=True,
)
def run_full_workflow(n, toolkit_name, toolkit_desc, mcp_url, conn_id, agent_name):

    try:
        client = MCPToolkitClient.from_env()

        steps_output = {}

        # 1️⃣ Create toolkit
        create_res = client.create_mcp_toolkit(
            name=toolkit_name,
            description=toolkit_desc,
            mcp_url=mcp_url,
            connection_appid=conn_id,
            tools=["*"]
        )
        toolkit_id = create_res.get("id")
        steps_output["create_toolkit"] = create_res

        # 2️⃣ Fetch toolkit details
        details = client.get_toolkit_by_id(toolkit_id)
        steps_output["toolkit_details"] = details

        tools = details.get("tools", [])

        # 3️⃣ Locate agent
        agents = client.list_agents()
        agent = client.filter_agent_by_name(agents, agent_name)

        if not agent:
            return html.Div([
                html.H3("❌ Agent Not Found", style={"color": "red"}),
                html.Pre(f"Agent '{agent_name}' does not exist.")
            ])

        agent_id = agent.get("id")
        steps_output["agent_found"] = agent

        # 4️⃣ Update agent tools
        update_res = client.update_agent_tools(agent_id, tools)
        steps_output["update_agent_tools"] = {
            "status_code": update_res.status_code,
            "response": update_res.text
        }

        return html.Div([
            html.H3("✅ Workflow Completed Successfully!", style={"color": "green"}),
            html.Pre(json.dumps(steps_output, indent=2))
        ])

    except Exception as e:
        return html.Div([
            html.H3("❌ Error Occurred", style={"color": "red"}),
            html.Pre(str(e))
        ])


# ================================================================
# ============================== RUN ==============================
# ================================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)