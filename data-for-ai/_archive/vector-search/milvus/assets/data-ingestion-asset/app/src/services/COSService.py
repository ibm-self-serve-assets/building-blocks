from dotenv import load_dotenv
import ibm_boto3
from ibm_botocore.client import Config
import pandas as pd
import io
import os
import json
import logging

import tempfile
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class COSService:
    """
    A class to encapsulate all IBM Cloud Object Storage (COS) functionality.
    """

    def __init__(self, bucket_name):
        """
        Initializes the COSService class by loading environment variables
        and setting up the COS client.
        """
        load_dotenv()
        self.api_key = os.getenv("IBM_CLOUD_API_KEY")
        self.instance_id = os.getenv("COS_SERVICE_INSTANCE_ID")
        self.endpoint = os.getenv("COS_ENDPOINT")
        self.bucket_name = bucket_name

        # Validate environment variables
        self._validate_environment()
        
        # Initialize COS client
        self.cos_client = self._initialize_cos_client()

    def _validate_environment(self):
        """
        Validates required environment variables and logs warnings for missing variables.
        """
        required_vars = {
            "IBM_CLOUD_API_KEY": self.api_key,
            "COS_SERVICE_INSTANCE_ID": self.instance_id,
            "COS_ENDPOINT": self.endpoint,
            "COS_BUCKET_NAME": self.bucket_name
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        
        if missing_vars:
            error_msg = f"Required environment variables are missing: {', '.join(missing_vars)}"
            logging.error(error_msg)
            raise EnvironmentError(error_msg)
            
        logging.info(f"COS Endpoint: {self.endpoint}")
        logging.info(f"COS Bucket: {self.bucket_name}")

    def _initialize_cos_client(self):
        """
        Initializes and returns the COS client.
        """
        try:
            return ibm_boto3.client(
                's3',
                ibm_api_key_id=self.api_key,
                ibm_service_instance_id=self.instance_id,
                config=Config(signature_version='oauth'),
                endpoint_url=self.endpoint
            )
        except Exception as e:
            logging.exception(f"Error initializing COS client: {e}")
            raise

    def _validate_file_type(self, file_key: str) -> str: 
        """
        Validates the file type and returns the extension if supported.
        """
        file_ext = file_key.lower().split('.')[-1]
        if file_ext not in ['csv', 'json', 'pdf', 'html']:
            error_msg = f"Unsupported file type: {file_ext}. Only CSV and JSON files are supported."
            logging.error(error_msg)
            raise ValueError(error_msg)
        return file_ext

    def read_file(self, file_key: str, bucket_name: str = None):
        """
        Reads a file from COS and returns its contents.
        """
        bucket_name = bucket_name or self.bucket_name
        file_ext = self._validate_file_type(file_key)
        
        try:
            logging.info(f"Reading {file_ext.upper()} file from COS: {file_key}")
            response = self.cos_client.get_object(
                Bucket=bucket_name,
                Key=file_key
            )
            file_data = response['Body'].read()
            
            if file_ext == 'csv':
                data = pd.read_csv(io.BytesIO(file_data))
            else:
                data = json.loads(file_data.decode('utf-8'))
                
            logging.info(f"Successfully read {file_ext.upper()} file from COS: {file_key}")
            return data
            
        except Exception as e:
            logging.exception(f"Error reading {file_ext.upper()} file from COS: {e}")
            raise

    def write_file(self, data, file_key: str, bucket_name: str = None):
        """
        Writes data to a file in COS.
        """
        bucket_name = bucket_name or self.bucket_name
        file_ext = self._validate_file_type(file_key)
        
        try:
            if file_ext == 'csv' and not isinstance(data, pd.DataFrame):
                error_msg = "CSV files require a pandas DataFrame as input"
                logging.error(error_msg)
                raise ValueError(error_msg)
            elif file_ext == 'json' and not isinstance(data, (dict, list)):
                error_msg = "JSON files require a dict or list as input"
                logging.error(error_msg)
                raise ValueError(error_msg)

            logging.info(f"Writing {file_ext.upper()} file to COS: {file_key}")
            
            if file_ext == 'csv':
                buffer = io.StringIO()
                data.to_csv(buffer, index=False)
                file_bytes = buffer.getvalue().encode('utf-8')
            else:
                file_bytes = json.dumps(data, indent=2, sort_keys=False).encode('utf-8')
            
            self.cos_client.put_object(
                Bucket=bucket_name,
                Key=file_key,
                Body=file_bytes
            )
            
            logging.info(f"Successfully wrote {file_ext.upper()} file to COS: {file_key}")
            
        except Exception as e:
            logging.exception(f"Error writing {file_ext.upper()} file to COS: {e}")
            raise

    def get_all_objects_from_cos(self, download_files=True, temp_dir=None):
        bucket_name = self.bucket_name
        
        # Default supported file extensions for Docling
        valid_extensions = ['.pdf', '.docx', '.xlsx', '.pptx', '.md', '.adoc', '.html', '.xhtml', '.csv', 
                            '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.json']
        
        try:
            logging.info(f"Getting objects for ingestion from bucket: {bucket_name}")
            logging.info(f"Filtering for file extensions: {valid_extensions}")
            
            # Get all objects in the bucket
            response = self.cos_client.list_objects_v2(Bucket=bucket_name)
            
            # Check if there are any objects in the bucket
            if 'Contents' not in response:
                logging.info(f"No objects found in bucket: {bucket_name}")
                return [] if download_files else []
            
            # Extract just the keys (file paths) for valid file types
            object_keys = []
            for obj in response['Contents']:
                key = obj['Key']
                
                # Check if the file has a valid extension
                file_extension = os.path.splitext(key.lower())[1]
                if file_extension in valid_extensions:
                    object_keys.append(key)
                
            # Handle pagination if there are more objects
            while response.get('IsTruncated', False):
                continuation_token = response.get('NextContinuationToken')
                response = self.cos_client.list_objects_v2(
                    Bucket=bucket_name,
                    ContinuationToken=continuation_token
                )
                
                for obj in response['Contents']:
                    key = obj['Key']
                    
                    # Check if the file has a valid extension
                    file_extension = os.path.splitext(key.lower())[1]
                    if file_extension in valid_extensions:
                        object_keys.append(key)
            
            logging.info(f"Found {len(object_keys)} valid objects in bucket: {bucket_name}")
            
            # Return just the keys if download_files is False
            if not download_files:
                return []
                
            # Create a temporary directory if not provided
            temp_dir_obj = None
            if temp_dir is None:
                temp_dir_obj = tempfile.TemporaryDirectory()
                temp_dir = temp_dir_obj.name
                logging.info(f"Created temporary directory: {temp_dir}")
                
            files_list = []
            
            for file_key in object_keys:
                try:
                    # Get filename from the key
                    filename = os.path.basename(file_key)
                    
                    # Create local temp file path
                    local_file_path = os.path.join(temp_dir, filename)
                    
                    # Download file directly to the temp location
                    self.cos_client.download_file(
                        Bucket=bucket_name,
                        Key=file_key,
                        Filename=local_file_path
                    )
                    
                    # Add to list of files in the same format as local code
                    files_list.append({
                        'full_path': local_file_path,
                        'filename': filename
                    })
                    
                    logging.info(f"Downloaded {file_key} to {local_file_path}")
                    
                except Exception as e:
                    logging.error(f"Error downloading file {file_key}: {str(e)}")
                    continue
            
            # Return the temp_dir_obj for later cleanup if we created it
            if temp_dir_obj:
                # Store the temp directory object somewhere accessible for cleanup
                self._temp_dir_obj = temp_dir_obj
                
            return files_list
            
        except Exception as e:
            logging.exception(f"Error getting objects for ingestion: {e}")
            raise