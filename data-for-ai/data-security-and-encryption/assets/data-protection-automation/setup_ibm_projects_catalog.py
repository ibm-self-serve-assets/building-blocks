import os
import json
import time
import requests

CONFIG_FILE = "input.json"

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

IBM_API_KEY = config["ibm_api_key"]
REGION = config.get("region", "eu-de")
BASE_URL = f"https://api.{REGION}.dataplatform.cloud.ibm.com"

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
        os.environ["TOKEN"] = self.token
        print("Refreshed IAM token.")

def build_headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

def create_project(headers, project_cfg):
    url = f"{BASE_URL}/transactional/v2/projects"
    resp = requests.post(url, headers=headers, json=project_cfg)
    print("Project Creation:", resp.status_code, resp.text)
    return resp

def create_catalog(headers, catalog_cfg):
    url = f"{BASE_URL}/v2/catalogs"
    resp = requests.post(url, headers=headers, json=catalog_cfg)
    print("Catalog Creation:", resp.status_code, resp.text)
    return resp

if __name__ == "__main__":
    if not IBM_API_KEY:
        raise SystemExit("Please provide ibm_api_key in input.json")

    token_mgr = IAMTokenManager(IBM_API_KEY)
    token = token_mgr.get_token()
    headers = build_headers(token)

    project_payload = config["project"]
    create_project(headers, project_payload)

    catalog_payload = config["catalog"]
    create_catalog(headers, catalog_payload)

    print("Setup Complete: Project + Catalog created.")
