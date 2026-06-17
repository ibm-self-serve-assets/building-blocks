"""IBM COS operations — shared utility."""
from __future__ import annotations
import logging
import os
from pathlib import Path
import ibm_boto3
from ibm_botocore.client import Config

logger = logging.getLogger(__name__)


def _c():
    return ibm_boto3.client("s3",
        ibm_api_key_id=os.environ["COS_API_KEY"],
        ibm_service_instance_id=os.environ["COS_INSTANCE_CRN"],
        config=Config(signature_version="oauth"),
        endpoint_url=os.getenv("COS_ENDPOINT", "https://s3.us-south.cloud-object-storage.appdomain.cloud"))


def list_objects(bucket: str, prefix: str) -> list[str]:
    resp = _c().list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [o["Key"] for o in resp.get("Contents", []) if not o["Key"].endswith("/")]


def download_objects(bucket: str, keys: list[str], local_dir: str) -> list[str]:
    Path(local_dir).mkdir(parents=True, exist_ok=True)
    c, paths = _c(), []
    for k in keys:
        lp = os.path.join(local_dir, os.path.basename(k))
        c.download_file(bucket, k, lp)
        paths.append(lp)
    return paths
