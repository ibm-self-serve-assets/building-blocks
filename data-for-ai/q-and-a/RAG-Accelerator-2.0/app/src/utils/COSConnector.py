import os
import io
import json
import logging
import tempfile
import zipfile
import shutil
from dotenv import load_dotenv
from ibm_botocore.client import Config
import ibm_boto3
import pandas as pd
from typing import Union, List, Dict, Any


class COSService:
    """
    A class to encapsulate all IBM Cloud Object Storage (COS) functionality with support for:
    - Documents: PDF, DOCX, PPTX, HTML, MD, TXT
    - Archives: ZIP
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
        self._temp_dir_obj = None

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
        Supported formats: pdf, docx, pptx, html, md, txt, zip
        """
        file_ext = file_key.lower().split('.')[-1]
        supported_extensions = ['pdf', 'docx', 'pptx','html', 'md', 'txt', 'zip']

        if file_ext not in supported_extensions:
            error_msg = (f"Unsupported file type: {file_ext}. "
                        f"Supported formats are: {', '.join(supported_extensions)}")
            logging.error(error_msg)
            raise ValueError(error_msg)
        return file_ext

    def read_file(self, file_key: str, bucket_name: str = None) -> Union[pd.DataFrame, Dict, List, bytes, str]:
        """
        Reads a file from COS and returns its contents in appropriate format.
        - TXT, MD, HTML: returns string
        - PDF, DOCX, PPTX, ZIP: returns bytes
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

            if file_ext in ['txt', 'md', 'html']:
                data = file_data.decode('utf-8')
            else:  # pdf, docx, pptx, zip
                data = file_data

            logging.info(f"Successfully read {file_ext.upper()} file from COS: {file_key}")
            return data

        except Exception as e:
            logging.exception(f"Error reading {file_ext.upper()} file from COS: {e}")
            raise

    def write_file(self, data: Union[pd.DataFrame, Dict, List, bytes, str],
                  file_key: str, bucket_name: str = None) -> None:
        """
        Writes data to a file in COS.
        - TXT, MD, HTML: requires string
        - PDF, DOCX, PPTX, ZIP: requires bytes
        """
        bucket_name = bucket_name or self.bucket_name
        file_ext = self._validate_file_type(file_key)

        try:
            logging.info(f"Writing {file_ext.upper()} file to COS: {file_key}")

        
            if file_ext in ['txt', 'md', 'html']:
                if not isinstance(data, str):
                    error_msg = f"{file_ext.upper()} files require a string as input"
                    logging.error(error_msg)
                    raise ValueError(error_msg)
                file_bytes = data.encode('utf-8')
            else:  # pdf, docx, pptx, zip
                if not isinstance(data, bytes):
                    error_msg = f"{file_ext.upper()} files require bytes as input"
                    logging.error(error_msg)
                    raise ValueError(error_msg)
                file_bytes = data

            self.cos_client.put_object(
                Bucket=bucket_name,
                Key=file_key,
                Body=file_bytes
            )

            logging.info(f"Successfully wrote {file_ext.upper()} file to COS: {file_key}")

        except Exception as e:
            logging.exception(f"Error writing {file_ext.upper()} file to COS: {e}")
            raise

    def extract_zip_from_cos(self, zip_key: str, extract_to: str = None,
                         bucket_name: str = None) -> List[str]:
        """
        Extracts a ZIP file from COS while preserving folder structure.
        Returns a list of extracted file paths.
        """
        import os, zipfile, tempfile, shutil
        
        try:

            bucket_name = bucket_name or self.bucket_name

            if extract_to is None:
                temp_dir_obj = tempfile.TemporaryDirectory()
                extract_to = temp_dir_obj.name
                self._temp_dir_obj = temp_dir_obj  # save for cleanup

            zip_local_path = os.path.join(extract_to, os.path.basename(zip_key))
            self.cos_client.download_file(Bucket=bucket_name, Key=zip_key, Filename=zip_local_path)

            extracted_files = []

            with zipfile.ZipFile(zip_local_path, 'r') as z:
                for member in z.namelist():
                    member_path = member.replace("\\", "/").strip("/")
                    full_path = os.path.join(extract_to, member_path)

                    if member.endswith("/"):
                        os.makedirs(full_path, exist_ok=True)
                        continue

                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with z.open(member) as src, open(full_path, "wb") as dst:
                        shutil.copyfileobj(src, dst)

                    extracted_files.append(full_path)

            return extracted_files
        
        except Exception as e:
            logging.exception(f"Error extracting zip from cos : {e}")
            raise
    
        
    def get_all_objects_from_cos(self,download_files: bool = True,temp_dir: str = None) -> Union[List[Dict[str, str]], List[str]]:
        """
        Gets all objects from COS bucket, optionally downloading them to a temporary directory.
        Returns either:
        - If download_files=True: List of dicts with 'full_path' and 'filename' of downloaded files
        - If download_files=False: List of object keys (file paths) in COS

        Supports all these file extensions:
        .zip, .pdf, .docx, .pptx, .html, .md, .txt
        """

        bucket_name = self.bucket_name

        valid_extensions = [
            '.zip', '.pdf', '.docx', '.pptx', '.html', '.md', '.txt'
        ]

        try:
            logging.info(f"Getting objects for ingestion from bucket: {bucket_name}")
            logging.info(f"Filtering for file extensions: {valid_extensions}")

            all_keys = []
            response = self.cos_client.list_objects_v2(Bucket=bucket_name)

            # Collect first page
            if "Contents" in response:
                for obj in response["Contents"]:
                    key = obj["Key"]
                    ext = os.path.splitext(key.lower())[1]
                    if ext in valid_extensions:
                        all_keys.append(key)

            # Pagination loop
            while response.get("IsTruncated", False):
                token = response["NextContinuationToken"]
                response = self.cos_client.list_objects_v2(
                    Bucket=bucket_name,
                    ContinuationToken=token
                )
                for obj in response.get("Contents", []):
                    key = obj["Key"]
                    ext = os.path.splitext(key.lower())[1]
                    if ext in valid_extensions:
                        all_keys.append(key)

            logging.info(f"Found {len(all_keys)} valid objects.")

            if not download_files:
                return all_keys

            # Prepare temp directory
            temp_dir_obj = None
            if temp_dir is None:
                temp_dir_obj = tempfile.TemporaryDirectory()
                temp_dir = temp_dir_obj.name
                logging.info(f"Created temporary directory: {temp_dir}")

            downloaded_files = []

            # Download each object
            for file_key in all_keys:
                try:
                    ext = os.path.splitext(file_key.lower())[1]

                    # ZIP file → extract contents into same folder structure
                    if ext == ".zip":
                        logging.info(f"Extracting ZIP from COS: {file_key}")
                        extracted_files = self.extract_zip_from_cos(
                            zip_key=file_key,
                            extract_to=temp_dir,
                            bucket_name=bucket_name
                        )
                        # Add extracted file paths
                        downloaded_files.extend([
                            {
                                "full_path": f,
                                "filename": os.path.basename(f)
                            }
                            for f in extracted_files
                        ])
                        continue

                    # NON-ZIP: preserve folder structure as in COS
                    local_file_path = os.path.join(temp_dir, file_key)

                    # Create all necessary parent directories
                    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                    # Download file
                    self.cos_client.download_file(
                        Bucket=bucket_name,
                        Key=file_key,
                        Filename=local_file_path
                    )

                    downloaded_files.append({
                        "full_path": local_file_path,
                        "filename": os.path.basename(file_key)
                    })

                    logging.info(f"Downloaded {file_key} → {local_file_path}")

                except Exception as e:
                    logging.error(f"Error downloading {file_key}: {str(e)}")
                    continue

            # Save the temp dir object for later cleanup
            if temp_dir_obj:
                self._temp_dir_obj = temp_dir_obj

            return downloaded_files

        except Exception as e:
            logging.exception(f"Error getting objects for ingestion: {e}")
            raise

    # def cleanup_temp_files(self):
    #     """
    #     Cleans up any temporary files created during operations.
    #     """
    #     if hasattr(self, '_temp_dir_obj') and self._temp_dir_obj:
    #         try:
    #             self._temp_dir_obj.cleanup()
    #             logging.info("Temporary files cleaned up successfully")
    #         except Exception as e:
    #             logging.error(f"Error cleaning up temporary files: {e}")
    #         finally:
    #             self._temp_dir_obj = None

    # def __del__(self):
    #     """
    #     Destructor to ensure temporary files are cleaned up.
    #     """
    #     self.cleanup_temp_files()

