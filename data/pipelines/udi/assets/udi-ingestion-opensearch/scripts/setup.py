#!/usr/bin/env python3
"""
UDI Setup — Part 1 of 2

Registers COS and OpenSearch as named connections in watsonx.ai, then creates
(but does NOT run) the UDI ingestion flow. All IDs are saved to udi_config.json
so Part 2 (ingest.py) can run the flow repeatedly without re-registering anything.

Run this ONCE per environment. Re-run only if connections or flow parameters change.

Prerequisites:
  - IBM Cloud Object Storage instance + bucket + HMAC credentials
  - Watson Machine Learning instance linked to your watsonx.ai project
  - OpenSearch instance (IBM watsonx.data / Lakehouse, or self-managed)
  - Python >= 3.12  |  pip install -r requirements.txt

Usage:
  Linux / macOS:
      export IBM_CLOUD_API_KEY="<key>"
      export PROJECT_ID="<watsonx-project-id>"
      export COS_BUCKET="<bucket-name>"
      export COS_REGION="us-south"
      export COS_ACCESS_KEY="<hmac-access-key>"
      export COS_SECRET_KEY="<hmac-secret-key>"
      export OPENSEARCH_HOST="<hostname>"
      export OPENSEARCH_PORT="9200"
      export OPENSEARCH_USERNAME="<username>"
      export OPENSEARCH_PASSWORD="<password>"
      python3 scripts/setup.py

  Windows cmd:
      set IBM_CLOUD_API_KEY=<key>
      set PROJECT_ID=<watsonx-project-id>
      ... (same vars)
      python scripts\\setup.py

Optional env vars (defaults shown):
  WATSONX_URL          https://api.dataplatform.cloud.ibm.com
  WATSONX_ENV          cloud-prod  (cloud-prod | cloud-dev | cloud-test | cpd)
  COLLECTION_NAME      udi_documents        (folder path inside COS bucket)
  INDEX_NAME           udi_opensearch_index (OpenSearch index to write to)
  CHUNK_SIZE           4000
  CHUNK_OVERLAP        200
  EMBEDDINGS_MODEL_ID  ibm/slate-30m-english-rtrvr-v2
  FLOW_NAME            udi_opensearch_flow  (fixed name — no timestamp, so ingest.py can reuse it)

Output:
  udi_config.json — contains project_id, flow_id, job_id, and both connection IDs.
  Pass this file's location to ingest.py via UDI_CONFIG env var (default: udi_config.json).
"""

import json
import logging
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

try:
    import boto3
    import botocore
except ImportError:
    boto3 = None

# ---------------------------------------------------------------------------
# Logging — force UTF-8 so checkmark chars don't crash on Windows cp1252
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    handlers=[
        logging.StreamHandler(open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False)),
        logging.FileHandler("udi_setup.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration — all values from environment variables
# ---------------------------------------------------------------------------

def _require(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        log.error(f"Required environment variable not set: {name}")
        log.error("See the usage instructions at the top of this script.")
        sys.exit(1)
    return val


API_KEY    = _require("IBM_CLOUD_API_KEY")
PROJECT_ID = _require("PROJECT_ID")

COS_BUCKET   = _require("COS_BUCKET")
COS_ENDPOINT = os.environ.get("COS_ENDPOINT", "").strip()
COS_REGION   = os.environ.get("COS_REGION",   "us-south").strip()

# COS auth — two supported modes (auto-detected, HMAC is strongly recommended):
#
#   HMAC (recommended):
#     Set COS_ACCESS_KEY + COS_SECRET_KEY.
#     Obtain from: COS instance -> Service credentials -> Create credential
#     (enable the HMAC toggle) -> cos_hmac_keys.access_key_id / secret_access_key
#
#   IAM api_key (alternative — use only if HMAC keys are unavailable):
#     Set COS_API_KEY + COS_INSTANCE_CRN.
#     WARNING: IAM mode registers the connection successfully but is known to
#     fail at UDI flow runtime with CDICO2034E.  Prefer HMAC.
COS_ACCESS_KEY   = os.environ.get("COS_ACCESS_KEY",   "").strip()
COS_SECRET_KEY   = os.environ.get("COS_SECRET_KEY",   "").strip()
COS_API_KEY      = os.environ.get("COS_API_KEY",      "").strip()

# Watson Data API requires the SERVICE INSTANCE CRN (ends with "::"), not a
# bucket-level CRN (ends with ":bucket:<name>").  Strip the bucket suffix
# automatically so both forms are accepted.
_raw_crn = os.environ.get("COS_INSTANCE_CRN", "").strip()
if ":bucket:" in _raw_crn:
    _raw_crn = _raw_crn.rsplit(":bucket:", 1)[0] + "::"
COS_INSTANCE_CRN = _raw_crn

# Resolve effective endpoint
def _cos_endpoint() -> str:
    if COS_ENDPOINT:
        return COS_ENDPOINT
    return f"https://s3.{COS_REGION}.cloud-object-storage.appdomain.cloud"

# Validate: at least one auth mode must be fully provided
_hmac_ok   = bool(COS_ACCESS_KEY and COS_SECRET_KEY)
_apikey_ok = bool(COS_API_KEY and COS_INSTANCE_CRN)
if not _hmac_ok and not _apikey_ok:
    log.error("COS authentication not configured. Provide either:")
    log.error("  HMAC (recommended): COS_ACCESS_KEY + COS_SECRET_KEY")
    log.error("  IAM (alternative):  COS_API_KEY + COS_INSTANCE_CRN")
    sys.exit(1)

OPENSEARCH_HOST     = _require("OPENSEARCH_HOST")
OPENSEARCH_PORT     = os.environ.get("OPENSEARCH_PORT", "9200").strip()
OPENSEARCH_USERNAME = _require("OPENSEARCH_USERNAME")
OPENSEARCH_PASSWORD = _require("OPENSEARCH_PASSWORD")

WATSONX_URL = os.environ.get("WATSONX_URL", "https://api.dataplatform.cloud.ibm.com").strip()
WATSONX_ENV = os.environ.get("WATSONX_ENV", "cloud-prod").strip()

COLLECTION_NAME     = os.environ.get("COLLECTION_NAME",     "udi_documents")
INDEX_NAME          = os.environ.get("INDEX_NAME",          "udi_opensearch_index")
CHUNK_SIZE          = int(os.environ.get("CHUNK_SIZE",      "4000"))
CHUNK_OVERLAP       = int(os.environ.get("CHUNK_OVERLAP",   "200"))
EMBEDDINGS_MODEL_ID = os.environ.get("EMBEDDINGS_MODEL_ID", "ibm/slate-30m-english-rtrvr-v2")
# Append timestamp to ensure uniqueness across runs — ingest.py reads the actual
# name back from udi_config.json, so repeatable ingestion still works fine.
_flow_name_base = os.environ.get("FLOW_NAME", "udi_opensearch_flow")
FLOW_NAME = f"{_flow_name_base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Default: write udi_config.json next to setup.py (inside scripts/)
CONFIG_FILE = os.environ.get("UDI_CONFIG", str(Path(__file__).parent / "udi_config.json"))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_iam_token() -> str:
    """Exchange API key for a short-lived IAM bearer token."""
    log.info("Obtaining IAM bearer token...")
    data = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={API_KEY}".encode()
    req = urllib.request.Request(
        "https://iam.cloud.ibm.com/identity/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        token = json.loads(r.read())["access_token"]
    log.info("✓ IAM token obtained")
    return token


def register_connection(token: str, payload: dict, label: str) -> str:
    """Register a connection in watsonx.ai and return its asset_id."""
    log.info(f"Registering {label} connection...")
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{WATSONX_URL}/v2/connections?project_id={PROJECT_ID}",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type":  "application/json",
            "User-Agent":    "ibm-udi-client/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            conn_id = json.loads(r.read())["metadata"]["asset_id"]
        log.info(f"✓ {label} connection registered: {conn_id}")
        return conn_id
    except urllib.error.HTTPError as e:
        log.error(f"✗ Failed to register {label} connection: HTTP {e.code}")
        log.error(f"  Response: {e.read().decode()}")
        raise


def list_cos_files(cos_conn_id: str) -> list[dict]:
    """Enumerate all supported files in the COS folder and return as input_assets."""
    if boto3 is None:
        log.error("boto3 is required to enumerate COS files. Run: pip install boto3")
        sys.exit(1)

    SUPPORTED = {".pdf", ".docx", ".pptx", ".doc", ".ppt", ".md", ".txt", ".xlsx", ".html"}
    endpoint = _cos_endpoint()

    log.info(f"Enumerating files in COS: {endpoint}/{COS_BUCKET}/{COLLECTION_NAME}/")
    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=COS_ACCESS_KEY,
        aws_secret_access_key=COS_SECRET_KEY,
    )

    assets = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=COS_BUCKET, Prefix=COLLECTION_NAME):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            ext = ("." + key.rsplit(".", 1)[-1].lower()) if "." in key.split("/")[-1] else ""
            if ext in SUPPORTED:
                # source must include the bucket name: /<bucket>/<key>
                assets.append({
                    "asset_id":      f"{COS_BUCKET}/{key}",
                    "asset_name":    key.split("/")[-1],
                    "connection_id": cos_conn_id,
                    "source":        f"/{COS_BUCKET}/{key}",
                })

    log.info(f"✓ Found {len(assets)} files to ingest")
    if not assets:
        log.error("No supported files found. Check COS_BUCKET and COLLECTION_NAME.")
        sys.exit(1)
    return assets


def create_flow(cos_conn_id: str, opensearch_conn_id: str) -> tuple[str, str]:
    """Create the UDI flow in watsonx and return (flow_id, job_id)."""
    try:
        from udi import UDIClient
        from udi.flows import Flow
    except ImportError:
        log.error("ibm-udi package not installed. Run: pip install -r requirements.txt")
        sys.exit(1)

    # Enumerate COS files to build explicit input_assets list
    input_assets = list_cos_files(cos_conn_id)

    log.info(f"Creating UDI flow: {FLOW_NAME}...")
    uc = UDIClient(config={
        "base_url":   WATSONX_URL,
        "project_id": PROJECT_ID,
        "api_key":    API_KEY,
        "env":        WATSONX_ENV,
    })

    pipeline = {
        "flow_name":    FLOW_NAME,
        "project_id":  PROJECT_ID,
        "orchestrator": "python",
        "global_config": {
            "data_local_config":     {"output_folder": "./udi_output"},
            "data_storage_type":     "local",
            "enable_micro_batching": True,
            "micro_batch_size":      100,
        },
        "flow": [
            {
                "type": "ingest_cpd_connections",
                "parameters": {
                    "cp4d_connection_id": cos_conn_id,
                    "input_folder":       COLLECTION_NAME,
                    "paths":              [f"/{COS_BUCKET}/{COLLECTION_NAME}"],
                    "include_filter": [".pdf", ".docx", ".pptx", ".doc", ".ppt",
                                       ".md", ".txt", ".xlsx", ".html"],
                    "max_files": 5000,
                    "max_file_size": 200,
                },
            },
            {
                "type": "extract_cpd",
                "parameters": {
                    "ocr_mode": "enabled",
                    "extract_entity": False,
                    "custom_schema": "disabled",
                    "mode": "high_quality",
                },
            },
            {
                "type": "chunker",
                "parameters": {
                    "chunk_type":    "watsonx",
                    "chunk_size":    CHUNK_SIZE,
                    "chunk_overlap": CHUNK_OVERLAP,
                },
            },
            {
                "type": "embeddings",
                "parameters": {
                    "embeddings_type":     "watsonx",
                    "embeddings_model_id": EMBEDDINGS_MODEL_ID,
                },
            },
            {
                "type": "opensearch",
                "parameters": {
                    "connection_id": opensearch_conn_id,
                    "index_name":    INDEX_NAME,
                    "engine":        "lucene",
                    "opensearch_feature_mappings": [
                        ["name",        "document_name", ""],
                        ["doc_id_hash", "pk",            ""],
                        ["id",          "document_id",   ""],
                        ["embeddings",  "vector_index",  ""],
                        ["content",     "text",          ""],
                    ],
                },
            },
        ],
    }

    flow = Flow(uc)
    flow.create(pipeline=pipeline)
    flow_id = flow.flow_id
    job_id  = flow.job_id
    log.info(f"✓ Flow created — flow_id: {flow_id} | job_id: {job_id}")
    return flow_id, job_id


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    log.info("=" * 70)
    log.info("UDI Setup — Part 1 of 2")
    log.info("=" * 70)

    try:
        token = get_iam_token()

        os_conn_id = register_connection(token, {
            "name":            "udi-opensearch-connection",
            "datasource_type": "opensearch-ibmcloud",
            "origin_country":  "us",
            "properties": {
                "url":      f"https://{OPENSEARCH_HOST}:{OPENSEARCH_PORT}",
                "username": OPENSEARCH_USERNAME,
                "password": OPENSEARCH_PASSWORD,
            },
        }, label="OpenSearch")

        # Build COS connection properties based on detected auth mode
        if _hmac_ok:
            log.info("COS auth mode: HMAC")
            cos_props = {
                "url":        _cos_endpoint(),
                "bucket":     COS_BUCKET,
                "access_key": COS_ACCESS_KEY,
                "secret_key": COS_SECRET_KEY,
            }
        else:
            log.info("COS auth mode: IAM (api_key + resource_instance_id)")
            # WARNING: IAM mode is known to fail at UDI runtime (CDICO2034E).
            # Use HMAC credentials if at all possible.
            cos_props = {
                "url":                  _cos_endpoint(),
                "bucket":               COS_BUCKET,
                "api_key":              COS_API_KEY,
                "resource_instance_id": COS_INSTANCE_CRN,
            }

        cos_conn_id = register_connection(token, {
            "name":            "udi-cos-connection",
            "datasource_type": "cloudobjectstorage",
            "origin_country":  "us",
            "properties":      cos_props,
        }, label="COS")

        flow_id, job_id = create_flow(cos_conn_id, os_conn_id)

        config = {
            "project_id":              PROJECT_ID,
            "flow_id":                 flow_id,
            "job_id":                  job_id,
            "flow_name":               FLOW_NAME,
            "cos_connection_id":       cos_conn_id,
            "opensearch_connection_id": os_conn_id,
            "watsonx_url":             WATSONX_URL,
            "watsonx_env":             WATSONX_ENV,
            "setup_timestamp":         datetime.now().isoformat(),
        }

        Path(CONFIG_FILE).write_text(json.dumps(config, indent=2), encoding="utf-8")

        log.info("")
        log.info("=" * 70)
        log.info("✓ Setup complete")
        log.info("=" * 70)
        log.info(f"  Config saved to : {CONFIG_FILE}")
        log.info(f"  Flow ID         : {flow_id}")
        log.info(f"  Job ID          : {job_id}")
        log.info("")
        log.info("Next step — run the ingestion:")
        log.info("  python3 scripts/ingest.py")
        log.info("=" * 70)
        return 0

    except Exception as e:
        log.error(f"Setup failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
