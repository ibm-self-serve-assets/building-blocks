"""
IBM COS operations — download documents for ingestion.
Uses ibm-cos-sdk (boto3-compatible) with IAM OAuth.
"""
from __future__ import annotations
import logging
import os
from pathlib import Path
import ibm_boto3
from ibm_botocore.client import Config

logger = logging.getLogger(__name__)


def _client():
    return ibm_boto3.client(
        "s3",
        ibm_api_key_id=os.environ["COS_API_KEY"],
        ibm_service_instance_id=os.environ["COS_INSTANCE_CRN"],
        config=Config(signature_version="oauth"),
        endpoint_url=os.getenv("COS_ENDPOINT", "https://s3.us-south.cloud-object-storage.appdomain.cloud"),
    )


def list_objects(bucket: str, prefix: str) -> list[str]:
    resp = _client().list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [obj["Key"] for obj in resp.get("Contents", []) if not obj["Key"].endswith("/")]


def download_objects(bucket: str, keys: list[str], local_dir: str) -> list[str]:
    Path(local_dir).mkdir(parents=True, exist_ok=True)
    local_paths: list[str] = []
    cos = _client()
    for key in keys:
        local_path = os.path.join(local_dir, os.path.basename(key))
        cos.download_file(bucket, key, local_path)
        local_paths.append(local_path)
        logger.debug("Downloaded: %s → %s", key, local_path)
    logger.info("Downloaded %d files from COS prefix: %s", len(local_paths), keys[0] if keys else "")
    return local_paths
