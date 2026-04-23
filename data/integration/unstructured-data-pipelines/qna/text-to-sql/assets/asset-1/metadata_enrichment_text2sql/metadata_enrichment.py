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

class MetaDataEnrichment:

    def __init__(self):
        self.wxdi_url = os.getenv('WXDI_URL')
        self.project_id = os.getenv('PROJECT_ID')
        self.connection_id = os.getenv('CONNECTION_ID')
        self.category_id = os.getenv('CATEGORY_ID')
        self.token = access_token()
        self.logger = logger

    def import_data_to_wxdi_project(self, file_name : str,path_to_asset : str):

        """
            Import the data from watsonx.data(presto) to watsonx.data intelligence project and 
            start the metadata enrichment process.
            args: file_name(str), path_to_asset(str)
            return: enrichment_job_id (str)
        """

        try:
            # Get access token
            self.token = access_token()
            # url to register the asset
            register_url = f"{self.wxdi_url}/v2/data_assets"
            params = {
                "project_id": self.project_id
            }
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            # payload with file attachment
            payload = {
                    
                    "metadata": {
                        "name": file_name,
                        "description": "data table",
                        "tags": [
                            "public"
                        ],
                        "asset_type": "data_asset",
                        "origin_country": "us",
                        "rov": {
                            "mode": 0
                        }
                    },
                    "entity": {
                        "data_asset": {
                            "mime_type": "text/csv",
                            "dataset": False,
                            "properties": [
                                {
                                    "name": "bucket",
                                    "value": ""
                                },
                                {
                                    "name": "file_name",
                                    "value": ""
                                },
                                {
                                    "name": "first_line_header",
                                    "value": "true"
                                },
                                {
                                    "name": "encoding",
                                    "value": "UTF-8"
                                },
                                {
                                    "name": "invalid_data_handling",
                                    "value": "fail"
                                },
                                {
                                    "name": "file_format",
                                    "value": "csv"
                                }
                            ]
                        }
                    },
                    "attachments": [
                        {
                            "asset_type": "data_asset",
                            "name": "remote",
                            "description": "remote",
                            "mime": "text/csv",
                            "connection_id": self.connection_id,
                            "connection_path": f"{path_to_asset}",
                            "is_partitioned": False
                        }
                    ]
                
            }
            # logger.info(f"Posting file to IKC")
            response = requests.post(register_url, headers=headers, params=params, data=json.dumps(payload))
            logger.info(f"File successfully registered to IKC project {response}")

            response_data = response.json()
            return response_data['metadata']['asset_id']
        
        except Exception as e:
            print(f"ERROR: {e}")

    def execute_metadata_enrichment_job(self, asset_id, file_name):
        """
        Get the bearer token required for api calls to IKC
        args: 
            asset_id(str) - Dataset ID from watsonx.data intelligence
            file_name(str) - Name of the file
        return: response (JSON) (JSON response with metadata enrichment job ID)
        """
        try:
            url = f"{self.wxdi_url}/v2/metadata_enrichment/metadata_enrichment_area?project_id={self.project_id}&enrichmentImmediate=true"
            
            headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            uu_id = str(uuid.uuid4())[:4]
            prefix = f"{uu_id}_{timestamp}"
            unique_id = f"{prefix}_{file_name}"
            
            payload = {
                "name": f"MDE_{unique_id}",
                "description": "Enrichment Job",
                "job": {"name": f"MDE_JOB_{unique_id}"},
                "data_scope": {"enrichment_assets": [asset_id]},
                "objective": {
                    "enrichment_options": {
                        "structured": {
                            "semantic_expansion": True,
                            "analyze_quality": True,
                            "assign_terms": True,
                            "profile": True,
                            "data_search": True,
                            "analyze_relationships": True
                        }
                    },
                    "governance_scope": [{
                        "id": self.category_id,
                        "type": "CATEGORY"
                    }],
                    "datascope_of_reruns": "ALL",
                    "sampling": {
                        "structured": {
                            "method": "RANDOM",
                            "analysis_method": "PERCENTAGE",
                            "sample_size": {
                                "name": "CUSTOM", 
                                "percentage_options": {"decimal_value": 1}
                            }
                        }
                    }
                },
                "tags": ["test"]
            } 
            # Get the response
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            self.logger.info(f"Get the metadata enrichment job response")
            response.raise_for_status()
            return response
        except Exception as ex:
            return { "ERROR": f"Metadata fnrichment failed {ex}"}


    def check_job_status(self,job_id):
        """
        Check the status of the MDE Job
        args: job_id(str) - Metadata Enrichment job ID
        return: state (str) ("Running","Completed", "Failed", "Canceled", "Paused", "CompletedWithErrors")
        """
        try:
            status_url = f"{self.wxdi_url}/v2/jobs/{job_id}/runs?project_id={self.project_id}"
            MDE_STATES = {"Running", "Completed", "Failed", "Canceled", "Paused", "CompletedWithErrors"}
            headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
            response = requests.get(status_url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            job_run_data = response.json()
            state = job_run_data['results'][0]['entity']['job_run']['state']
            self.logger.info(f"Job Status: {state}")

            if state in MDE_STATES:
                self.logger.info(f"Job has reached terminal state: {state}")
                return state
        except Exception as ex:
            return { "ERROR": f"MDE job status check failed {ex}"}