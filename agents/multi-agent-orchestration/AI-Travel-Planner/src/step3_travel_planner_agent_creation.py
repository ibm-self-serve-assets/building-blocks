import os
import requests
from dotenv import load_dotenv
from wxo_token import *


# Load .env file variables
load_dotenv()

class AIAgentCreator:
    """Create a new AI agent using environment variables."""

    def __init__(self):
        self.wxo_url = os.getenv("WXO_SERVICE_URL")
        self.api_url = f"{self.wxo_url}/v1/orchestrate/agents"

        self.payload = {
            "display_name": os.getenv("AGENT_NAME"),
            "description": os.getenv("AGENT_DESCRIPTION"),
            "instructions": os.getenv("AGENT_INSTRUCTIONS"),
            "tools": [
            ],
            "collaborators": [],
            "llm": os.getenv("AGENT_LLM"),
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
            print("Request failed:", e)
            if 'response' in locals() and response is not None:
                print("Response text:", response.text)
            return None

if __name__ == "__main__":
    # creating agent now
    agent_creator = AIAgentCreator()
    agent_info = agent_creator.create()
   
    if agent_info:
        agent_id = agent_info['id']
        print("Agent created successfully, with id:", agent_id)