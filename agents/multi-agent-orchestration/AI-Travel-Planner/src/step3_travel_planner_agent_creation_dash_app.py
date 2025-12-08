# ================================================================
# ================ ORIGINAL AGENT CREATOR LOGIC ==================
# ================ (DO NOT MODIFY THIS BLOCK) ====================
# ================================================================

import os
import requests
from dotenv import load_dotenv
from wxo_token import *

# Load environment variables
load_dotenv()

# Extract default values from .env
DEFAULT_NAME = os.getenv("AGENT_NAME", "")
DEFAULT_DESC = os.getenv("AGENT_DESCRIPTION", "")
DEFAULT_INSTR = os.getenv("AGENT_INSTRUCTIONS", "")
DEFAULT_LLM = os.getenv("AGENT_LLM", "")
DEFAULT_WXO_URL = os.getenv("WXO_SERVICE_URL", "")


class AIAgentCreator:
    """Create a new AI agent using environment variables."""

    def __init__(self, name=None, description=None, instructions=None, llm=None):
        self.wxo_url = DEFAULT_WXO_URL
        self.api_url = f"{self.wxo_url}/v1/orchestrate/agents"

        self.payload = {
            "display_name": name or DEFAULT_NAME,
            "description": description or DEFAULT_DESC,
            "instructions": instructions or DEFAULT_INSTR,
            "tools": [],
            "collaborators": [],
            "llm": llm or DEFAULT_LLM,
            "agent_type": "default",
            "style": "default",
            "hidden": False,
            "glossary": [],
            "guidelines": [],
            "knowledge_base": [],
            "agent_config": {},
            "agent_mapping": {},
            "supported_apps": [],
            "voice_configuration_id": None,
            "chat_with_docs": {},
            "toolsSelected": [],
            "environments": []
        }

    def create(self):
        """Send request to create a new AI agent."""

        auth_object = clsAuth()
        token = auth_object.get_ibm_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = requests.post(self.api_url, json=self.payload, headers=headers)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            if 'response' in locals() and response is not None:
                return {"error": str(e), "details": response.text}
            return {"error": str(e)}


# ================================================================
# ========================== DASH UI ==============================
# ================================================================

import dash
from dash import Dash, html, dcc, Input, Output, State

app = Dash(__name__)

app.layout = html.Div(style={"maxWidth": "700px", "margin": "40px auto"}, children=[

    html.H2("AI Agent Creator UI"),

    html.Label("Agent Name"),
    dcc.Input(
        id="input-name",
        type="text",
        value=DEFAULT_NAME,
        placeholder="Agent name...",
        style={"width": "100%", "marginBottom": "12px"}
    ),

    html.Label("Description"),
    dcc.Textarea(
        id="input-desc",
        value=DEFAULT_DESC,
        placeholder="Agent description...",
        style={"width": "100%", "marginBottom": "12px", "height": "100px"}
    ),

    html.Label("Instructions"),
    dcc.Textarea(
        id="input-instr",
        value=DEFAULT_INSTR,
        placeholder="System instructions...",
        style={"width": "100%", "marginBottom": "12px", "height": "120px"}
    ),

    html.Label("LLM Model"),
    dcc.Input(
        id="input-llm",
        type="text",
        value=DEFAULT_LLM,
        placeholder="watsonx/model-name",
        style={"width": "100%", "marginBottom": "12px"}
    ),

    html.Button(
        "Create Agent",
        id="btn-create",
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
    Input("btn-create", "n_clicks"),
    State("input-name", "value"),
    State("input-desc", "value"),
    State("input-instr", "value"),
    State("input-llm", "value"),
    prevent_initial_call=True
)
def create_agent(n_clicks, name, desc, instr, llm):

    creator = AIAgentCreator(
        name=name,
        description=desc,
        instructions=instr,
        llm=llm
    )

    result = creator.create()

    if "error" in result:
        return html.Div([
            html.H3("❌ Error Creating Agent", style={"color": "red"}),
            html.Pre(str(result))
        ])

    return html.Div([
        html.H3("✅ Agent Created Successfully!", style={"color": "green"}),
        html.Pre(str(result))
    ])


# ================================================================
# =========================== RUN ================================
# ================================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
