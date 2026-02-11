import os
import requests
from dotenv import load_dotenv
from wxo_token import *

class clsConnection:
    def __init__(self):
        """Create a new connection using environment variables"""
        self.WXO_URL = os.getenv("WXO_SERVICE_URL")
        self.API_URL = ""
        self.CONNECTION_TYPE=os.getenv("WXO_CONNECTION_TYPE")
        self.CONNECTION_NAME=os.getenv("WXO_CONNECTION_NAME")
        self.CONNECTION_API_KEY=os.getenv("WXO_CONNECTION_API_KEY")
        auth_object=clsAuth()
        self.token = auth_object.get_ibm_token()
        
        self.headers = {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        

    def create_connection_id(self):
        self.API_URL = str(self.WXO_URL) + "/v1/orchestrate/connections/applications"

        payload = {
            "app_id": self.CONNECTION_NAME
        }

        #print("token:", token)
        
        try:
            response = requests.post(self.API_URL, json=payload, headers=self.headers)
            print("Response text:", response.text)
            response.raise_for_status()
            #return response.json()
        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
            if response is not None:
                print("Response text:", response.text)
            
        return None
    
    def create_connection_configuration(self):
        self.API_URL = str(self.WXO_URL) + "/v1/orchestrate/connections/applications/"+self.CONNECTION_NAME+"/configurations"

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
            print("Response text:", response.text)
            response.raise_for_status()
            #return response.json()
        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
            if response is not None:
                print("Response text:", response.text)
        return None
    
    def create_connection_credential(self):
        self.API_URL = str(self.WXO_URL) + "/v1/orchestrate/connections/applications/"+self.CONNECTION_NAME+"/configs/draft/runtime_credentials"

        payload = { 
            "runtime_credentials": {
                "api_key": self.CONNECTION_API_KEY
                }
        }

        try:
            response = requests.post(self.API_URL, json=payload, headers=self.headers)
            print("Response text:", response.text)
            response.raise_for_status()
            #return response.json()
        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
            if response is not None:
                print("Response text:", response.text)
        return None
    
if __name__ == "__main__":
    connection_info=clsConnection()
    connection_info.create_connection_id()
    connection_info.create_connection_configuration()
    connection_info.create_connection_credential()