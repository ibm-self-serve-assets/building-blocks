# ================================================================
# ================ ORIGINAL CONNECTION LOGIC ====================
# ================ (DO NOT MODIFY THIS BLOCK) ====================
# ================================================================

import os
import requests
from dotenv import load_dotenv
from wxo_token import *

# Load environment variables
load_dotenv()

DEFAULT_CONNECTION_TYPE = os.getenv("WXO_CONNECTION_TYPE", "")
DEFAULT_CONNECTION_NAME = os.getenv("WXO_CONNECTION_NAME", "")
DEFAULT_CONNECTION_API_KEY = os.getenv("WXO_CONNECTION_API_KEY", "")
DEFAULT_WXO_URL = os.getenv("WXO_SERVICE_URL", "")


class clsConnection:
    """Create a new WXO connection using environment variables."""

    def __init__(self, connection_type=None, connection_name=None, api_key=None):
        self.WXO_URL = DEFAULT_WXO_URL
        self.CONNECTION_TYPE = connection_type or DEFAULT_CONNECTION_TYPE
        self.CONNECTION_NAME = connection_name or DEFAULT_CONNECTION_NAME
        self.CONNECTION_API_KEY = api_key or DEFAULT_CONNECTION_API_KEY

        auth_object = clsAuth()
        self.token = auth_object.get_ibm_token()

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def create_connection_id(self):
        self.API_URL = f"{self.WXO_URL}/v1/orchestrate/connections/applications"
        payload = {"app_id": self.CONNECTION_NAME}

        try:
            response = requests.post(self.API_URL, json=payload, headers=self.headers)
            response.raise_for_status()
            return {"success": True, "step": "create_connection_id", "response": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "step": "create_connection_id", "error": str(e), "details": getattr(response, "text", None)}

    def create_connection_configuration(self):
        self.API_URL = f"{self.WXO_URL}/v1/orchestrate/connections/applications/{self.CONNECTION_NAME}/configurations"
        payload = { 
            "app_id": self.CONNECTION_NAME,
            "environment": "draft",
            "preference": "team",
            "security_scheme": self.CONNECTION_TYPE,
            "auth_type": "",
            "server_url": ""
        }

        try:
            response = requests.post(self.API_URL, json=payload, headers=self.headers)
            response.raise_for_status()
            return {"success": True, "step": "create_connection_configuration", "response": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "step": "create_connection_configuration", "error": str(e), "details": getattr(response, "text", None)}

    def create_connection_credential(self):
        self.API_URL = f"{self.WXO_URL}/v1/orchestrate/connections/applications/{self.CONNECTION_NAME}/configs/draft/runtime_credentials"
        payload = { 
            "runtime_credentials": {"api_key": self.CONNECTION_API_KEY}
        }

        try:
            response = requests.post(self.API_URL, json=payload, headers=self.headers)
            response.raise_for_status()
            return {"success": True, "step": "create_connection_credential", "response": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "step": "create_connection_credential", "error": str(e), "details": getattr(response, "text", None)}

    def create_full_connection(self):
        """Run all three steps and return results as a list."""
        results = []
        results.append(self.create_connection_id())
        results.append(self.create_connection_configuration())
        results.append(self.create_connection_credential())
        return results


# ================================================================
# ========================== DASH UI ==============================
# ================================================================

import dash
from dash import Dash, html, dcc, Input, Output, State
import json

app = Dash(__name__)

app.layout = html.Div(style={"maxWidth": "700px", "margin": "40px auto"}, children=[

    html.H2("WXO Connection Creator UI"),

    html.Label("Connection Name"),
    dcc.Input(
        id="input-conn-name",
        type="text",
        value=DEFAULT_CONNECTION_NAME,
        placeholder="Connection name...",
        style={"width": "100%", "marginBottom": "12px"}
    ),

    html.Label("Connection Type"),
    dcc.Input(
        id="input-conn-type",
        type="text",
        value=DEFAULT_CONNECTION_TYPE,
        placeholder="Connection type...",
        style={"width": "100%", "marginBottom": "12px"}
    ),

    html.Label("Connection API Key"),
    dcc.Input(
        id="input-conn-key",
        type="text",
        value=DEFAULT_CONNECTION_API_KEY,
        placeholder="API Key...",
        style={"width": "100%", "marginBottom": "12px"}
    ),

    html.Button(
        "Create Connection",
        id="btn-create-conn",
        n_clicks=0,
        style={"marginTop": "20px", "padding": "10px 20px"}
    ),

    html.Hr(),

    html.Div(id="output-panel")
])


# ================================================================
# ====================== DASH CALLBACK ============================
# ================================================================

@app.callback(
    Output("output-panel", "children"),
    Input("btn-create-conn", "n_clicks"),
    State("input-conn-name", "value"),
    State("input-conn-type", "value"),
    State("input-conn-key", "value"),
    prevent_initial_call=True
)
def create_connection(n_clicks, name, conn_type, api_key):
    connection = clsConnection(
        connection_type=conn_type,
        connection_name=name,
        api_key=api_key
    )

    results = connection.create_full_connection()

    # Format output nicely
    output_divs = []
    for res in results:
        if res.get("success"):
            output_divs.append(html.Div([
                html.H3(f"✅ {res['step']} succeeded", style={"color": "green"}),
                html.Pre(json.dumps(res["response"], indent=2))
            ]))
        else:
            output_divs.append(html.Div([
                html.H3(f"❌ {res['step']} failed", style={"color": "red"}),
                html.Pre(json.dumps(res, indent=2))
            ]))
    return output_divs


# ================================================================
# =========================== RUN ================================
# ================================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)