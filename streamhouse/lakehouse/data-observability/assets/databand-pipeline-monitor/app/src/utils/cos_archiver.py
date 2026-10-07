"""
IBM COS archive helper — writes pipeline run reports to IBM Cloud Object Storage.
Uses ibm-cos-sdk (boto3-compatible) with IAM API key authentication.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone

import ibm_boto3
from ibm_botocore.client import Config

logger = logging.getLogger(__name__)


def _cos_client() -> ibm_boto3.client:
    return ibm_boto3.client(
        "s3",
        ibm_api_key_id=os.environ["COS_API_KEY"],
        ibm_service_instance_id=os.environ["COS_INSTANCE_CRN"],
        config=Config(signature_version="oauth"),
        endpoint_url=os.getenv(
            "COS_ENDPOINT",
            "https://s3.us-south.cloud-object-storage.appdomain.cloud",
        ),
    )


def archive_run_report(pipeline_name: str, run_uid: str, report: dict) -> str:
    """
    Serialise *report* to JSON and upload it to COS.

    Returns the COS object key.
    """
    bucket = os.environ["COS_BUCKET"]
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    key = f"pipeline-reports/{pipeline_name}/{run_uid}/{ts}.json"

    body = json.dumps(report, indent=2, default=str)

    client = _cos_client()
    client.put_object(Bucket=bucket, Key=key, Body=body, ContentType="application/json")
    logger.info("Report archived to COS: s3://%s/%s", bucket, key)
    return key


def list_archived_reports(pipeline_name: str) -> list[str]:
    """Return all COS object keys for the given pipeline."""
    bucket = os.environ["COS_BUCKET"]
    prefix = f"pipeline-reports/{pipeline_name}/"
    client = _cos_client()
    resp = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [obj["Key"] for obj in resp.get("Contents", [])]
