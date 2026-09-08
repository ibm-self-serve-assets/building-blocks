import os
import requests
from dotenv import load_dotenv
from logs.logging_config import setup_logging

# Load variables from .env file
load_dotenv()

AUTH_URL = os.getenv('AUTH_URL')
API_KEY = os.getenv('API_KEY')

# Inizialise logger
logger = setup_logging()

def access_token():
    """
    Get the bearer token required for api calls to watsonx.data Intelligence
    args: api_key(str) - IBM Cloud API Access key
    return: access_token (str)
    """
    try:
        auth_response = requests.post(
            AUTH_URL,
            data={"apikey": API_KEY, "grant_type": "urn:ibm:params:oauth:grant-type:apikey"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        # get access token
        access_token = auth_response.json()["access_token"]
        logger.info(f"Generated beared token")
        return access_token
    except Exception as ex:
        logger.info(f"ERROR: {ex}")