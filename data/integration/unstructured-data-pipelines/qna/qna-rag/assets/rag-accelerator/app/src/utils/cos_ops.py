import os
import logging
from typing import List, Dict
from app.src.utils.cos_connector import COSService

logger = logging.getLogger(__name__)


class COSOperations:
    """
    Wrapper class for COS-related ingestion operations.
    Responsible for:
    - Fetching object keys
    - Filtering by prefix
    - Downloading filtered files
    """

    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.cos_service = COSService(bucket_name=bucket_name)

    def get_filtered_keys(self, prefix: str) -> List[str]:
        """
        Fetch all keys and filter by prefix.
        """

        logger.info(f"Fetching object keys from bucket: {self.bucket_name}")

        all_keys = self.cos_service.get_all_objects_from_cos(download_files=False)

        logger.info(f"Total objects in bucket: {len(all_keys)}")

        prefix = prefix.rstrip("/") + "/"

        filtered_keys = [
            key for key in all_keys
            if key.startswith(prefix)
        ]

        logger.info(f"Objects under prefix '{prefix}': {len(filtered_keys)}")

        return filtered_keys

    def download_files(
        self,
        keys: List[str],
        local_directory: str
    ) -> List[Dict[str, str]]:
        """
        Download selected keys to local directory.
        """

        if not keys:
            logger.warning("No keys provided for download.")
            return []

        os.makedirs(local_directory, exist_ok=True)

        downloaded_files = []

        for key in keys:
            filename = os.path.basename(key)
            local_path = os.path.join(local_directory, filename)

            self.cos_service.cos_client.download_file(
                Bucket=self.bucket_name,
                Key=key,
                Filename=local_path
            )

            downloaded_files.append({
                "full_path": local_path,
                "filename": filename
            })

        logger.info(f"Downloaded {len(downloaded_files)} files")

        return downloaded_files