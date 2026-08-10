import os
import requests
from dotenv import load_dotenv
import json

# Load .env file variables
load_dotenv()

class clsAuth:

    def __init__(self):
        self.url = os.getenv("WXO_TOKEN_URL")
        self.apikey = os.getenv("WXO_API_KEY")

    def get_ibm_token(self):
        """
        Requests an IBM Cloud IAM token using an API key.
        Returns the access token string if successful, else raises an exception.
        """

        if not self.apikey:
            raise ValueError("WXO_API_KEY not set in environment")
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.apikey
        }
        
        response = requests.post(self.url, headers=headers, data=data)
        response.raise_for_status()  # Raises error for 4xx/5xx responses
        
        token_data = response.json()
        return token_data.get("access_token")
    
if __name__ == "__main__":
    agent_info = clsAuth()
    print(agent_info.get_ibm_token())
    
