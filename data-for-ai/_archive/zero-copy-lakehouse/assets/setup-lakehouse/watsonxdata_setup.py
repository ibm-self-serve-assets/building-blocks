import os
import time
import json
import requests
import sys

with open("config.json", "r") as f:
    config = json.load(f)

REGION = config["region"]
BASE_URL = f"https://{REGION}.lakehouse.cloud.ibm.com/lakehouse/api/v2"

IBM_API_KEY = os.getenv("IBM_API_KEY")
AUTH_INSTANCE_ID = config["auth_instance_id"]

COS_CONFIG = config["cos_config"]
S3_CONFIG = config["s3_config"]
DB2_OLTP_CONFIG = config["db2_oltp"]

class IAMTokenManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.token = None
        self.expiry = 0

    def get_token(self) -> str:
        if not self.token or time.time() >= self.expiry:
            self._refresh_token()
        return self.token

    def _refresh_token(self):
        url = "https://iam.cloud.ibm.com/identity/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key,
        }
        resp = requests.post(url, headers=headers, data=data)
        resp.raise_for_status()
        result = resp.json()
        self.token = result["access_token"]
        self.expiry = time.time() + int(result.get("expires_in", 3600)) - 300
        print("Refreshed IAM token.")

def build_headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
        "AuthInstanceId": AUTH_INSTANCE_ID,
        "Content-Type": "application/json",
    }

def wait_with_progress(seconds, message="Waiting"):
    """Show countdown progress instead of silent sleep."""
    for i in range(seconds, 0, -1):
        sys.stdout.write(f"\r{message}... {i} seconds remaining")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\rDone!                          \n")

def register_bucket(headers, config, label):
    url = f"{BASE_URL}/bucket_registrations"
    resp = requests.post(url, headers=headers, json=config)
    print(f"{label} Bucket Registration:", resp.status_code, resp.text)
    return resp

def create_db2_oltp_connection(headers, cfg):
    url = f"{BASE_URL}/database_registrations"
    payload = {
        "database_details": {
            "database_name": cfg["database_name"],
            "hostname": cfg["hostname"],
            "password": cfg["password"],
            "port": cfg["port"],
            "ssl": True,
            "username": cfg["username"],
        },
        "database_display_name": cfg["display_name"],
        "database_type": "db2",
        "description": "db2 external database description",
        "associated_catalog": {
            "catalog_name": cfg["catalog_name"],
            "catalog_type": "iceberg",
        },
    }
    resp = requests.post(url, headers=headers, json=payload)
    print("DB2 OLTP Connection:", resp.status_code, resp.text)
    return resp

def get_engine_id(headers):
    url = f"{BASE_URL}/presto_engines"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    engine_id = data["presto_engines"][0]["engine_id"]
    print("Engine ID:", engine_id)
    return engine_id

def associate_catalog_to_engine(headers, engine_id, catalog_name):
    url = f"{BASE_URL}/presto_engines/{engine_id}/catalogs"
    payload = {"catalog_names": catalog_name}
    resp = requests.post(url, headers=headers, json=payload)
    print(f"Catalog Association ({catalog_name}):", resp.status_code, resp.text)
    return resp

def create_schema(headers, engine_id, catalog_name, bucket_name, schema_name, custom_path):
    url = f"{BASE_URL}/catalogs/{catalog_name}/schemas?engine_id={engine_id}"
    payload = {
        "bucket_name": bucket_name,
        "custom_path": custom_path,
        "schema_name": schema_name,
    }
    resp = requests.post(url, headers=headers, json=payload)
    print(f"Schema Creation ({schema_name} in {catalog_name}):", resp.status_code, resp.text)
    return resp

if __name__ == "__main__":
    if not IBM_API_KEY:
        raise SystemExit("Please export IBM_API_KEY before running.")

    token_mgr = IAMTokenManager(IBM_API_KEY)
    headers = build_headers(token_mgr.get_token())

    register_bucket(headers, COS_CONFIG, "COS")
    register_bucket(headers, S3_CONFIG, "AWS S3")

    create_db2_oltp_connection(headers, DB2_OLTP_CONFIG)

    engine_id = get_engine_id(headers)

    associate_catalog_to_engine(headers, engine_id, COS_CONFIG["associated_catalog"]["catalog_name"])
    wait_with_progress(30, "Waiting before associating next catalog")

    associate_catalog_to_engine(headers, engine_id, S3_CONFIG["associated_catalog"]["catalog_name"])
    wait_with_progress(30, "Waiting before associating DB2")

    associate_catalog_to_engine(headers, engine_id, DB2_OLTP_CONFIG["catalog_name"])
    wait_with_progress(90, "Waiting before schema creation")

    create_schema(
        headers,
        engine_id,
        COS_CONFIG["associated_catalog"]["catalog_name"],
        COS_CONFIG["bucket_details"]["bucket_name"],
        schema_name="customer",
        custom_path="/customer"
    )

    wait_with_progress(40, "Waiting before creating S3 schema")

    create_schema(
        headers,
        engine_id,
        S3_CONFIG["associated_catalog"]["catalog_name"],
        S3_CONFIG["bucket_details"]["bucket_name"],
        schema_name="account",
        custom_path="/account"
    )

    print("COS + S3 + DB2 + Schemas setup complete.")
