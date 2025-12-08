import os
import json
import logging
from dotenv import load_dotenv
from app.src.utils import config
from app.src.utils import rag_helper_functions


# load .env
load_dotenv()

# Logging configuration controlled via .env
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("rag_service")

# IBM client import (lazy)
try:
    from ibm_watsonx_ai import APIClient
except Exception as e:
    logger.exception("Failed to import ibm_watson_studio_lib: %s", e)

# Environment variables
#ENVIRONMENT = os.getenv("ENVIRONMENT", "cloud")
#RUNTIME_ENV_APSX_URL = os.getenv("RUNTIME_ENV_APSX_URL")
#RUNTIME_ENV_REGION = os.getenv("RUNTIME_ENV_REGION")
#USER_ACCESS_TOKEN = os.getenv("USER_ACCESS_TOKEN")
#WATSONX_DEPLOYMENT_ID = os.getenv("WATSONX_DEPLOYMENT_ID")
#WATSONX_SPACE_ID = os.getenv("WATSONX_SPACE_ID")
#WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")

# Get parameters from config
parameter_sets = config.PARAMETERS
parameter_sets_list = list(parameter_sets.keys())
parameters=rag_helper_functions.get_parameter_sets(parameter_sets_list)


def init_api_client():
    global client
    client = None

    # init API client
    try:
        if parameters['watsonx_ai_api_key']:
            if parameters['runtime_env_apsx_url'] and parameters['runtime_env_apsx_url'].endswith("cloud.ibm.com"):
                runtime_region = parameters['runtime_env_region']
                wml_credentials = {
                        "apikey": parameters['watsonx_ai_api_key'], 
                        "url": f"https://{runtime_region}.ml.cloud.ibm.com"
                        }
            else:
                wml_credentials = {
                    "token": parameters['user_access_token'], 
                    "instance_id" : "openshift", 
                    "url": parameters['runtime_env_apsx_url']
                }

            client = APIClient(wml_credentials)

            if parameters['watsonx_space_id']:
                client.set.default_space(parameters['watsonx_space_id'])
            logger.info("Initialized IBM watsonx.ai APIClient")
        else:
            logger.warning("WATSONX_API_KEY not set; IBM client not initialized")
        
    except Exception as e:
        logger.exception("Failed to initialize IBM client: %s", e)

    return client