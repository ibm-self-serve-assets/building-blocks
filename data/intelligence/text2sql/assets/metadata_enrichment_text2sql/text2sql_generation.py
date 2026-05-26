import os
import time
import json
import uuid
import requests
from datetime import datetime
from dotenv import load_dotenv
from config import access_token
from logs.logging_config import setup_logging


# Load variables from .env file
load_dotenv()

# Logger
logger = setup_logging()    

POLLING_INTERVAL = 10 # in seconds
REQUEST_TIMEOUT = 60 # in seconds

class Text2SQLGeneration:

    def __init__(self):
        self.project_id = os.getenv('PROJECT_ID')
        self.text2sql_ob_url = os.getenv('TEXT2SQL_ONBOARD_URL')
        self.text2sql_gen_url = os.getenv('TEXT2SQL_GENERATE_URL')
        # get access token
        self.token = access_token()
        self.logger = logger
        self.header = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }


    def onboard_text2sql_capabilities(self):
        """
            It is to onboard the text2sql capability to the watsonx.data intelligence project.
            return: container_details (JSON) (Returns container id(ie, project id) and container type)
        """

        try:
            payload = {
                "containers": [
                    {
                    "container_id": self.project_id,
                    "container_type": "project"
                    }
                ]
            }
            self.logger.info(f"Text2SQL onboarding initiated")
            response = requests.get(self.text2sql_ob_url, headers=self.header, json=payload)
            response = response.json()
            self.logger.info(f"Text2SQL onboarding completed")
            return response
        
        except Exception as ex:
            return {
                "ERROR" : f"Text2SQL onboarding failed{ex}"
            }
        
    def generate_text2sql_content(self, text2sql_data):
        """
            It checks the status of metadata enrichment job.
            args: query(str) (User's request to create a sql command)
            return: Text2SQL_Generation (JSON) (Returns a json response with generated_sql_queries in it)
        """
        try:
            
            payload = {
                "query": text2sql_data.query,
                "raw_output": True
                }
            text2sql_url = f"{self.text2sql_gen_url}?container_id={self.project_id}&container_type=project&dialect=presto&model_id=meta-llama%2Fllama-3-3-70b-instruct"
            self.logger.info(f"Text2SQL generation initiated")
            response = requests.post(text2sql_url, headers=self.header, json=payload)
            response = response.json()
            self.logger.info(f"Text2SQL generation completed")
            return response
        
        except Exception as ex:
            return {
                "ERROR" : f"Text2SQL generation failed{ex}"
            }