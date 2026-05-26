"""
Direct Model Scoring via watsonx ML API

Demonstrates how to call a deployed watsonx ML model for predictions
without a UI — suitable for batch scoring, API integration, and
automated testing pipelines.

Workflow:
  1. Authenticate with IBM Cloud IAM
  2. Build scoring payload
  3. Send to the deployed model endpoint
  4. Parse prediction and confidence scores

Prerequisites:
  pip install -r requirements.txt
  export WATSONX_APIKEY="your-ibm-cloud-api-key"
  export WATSONX_API_ENDPOINT="your-model-deployment-url"

Usage:
  python 02_model_scoring_api.py
"""

import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

# ── Validate credentials ──────────────────────────────────────────────
WATSONX_APIKEY = os.environ.get("WATSONX_APIKEY")
WATSONX_API_ENDPOINT = os.environ.get("WATSONX_API_ENDPOINT")

if not WATSONX_APIKEY:
    print("ERROR: WATSONX_APIKEY environment variable is not set.")
    sys.exit(1)
if not WATSONX_API_ENDPOINT:
    print("ERROR: WATSONX_API_ENDPOINT environment variable is not set.")
    print("  This should be the full URL to your deployed model's predictions endpoint.")
    sys.exit(1)


# ── Authentication ────────────────────────────────────────────────────

def get_iam_token(api_key: str) -> str:
    """Obtain an IAM bearer token from IBM Cloud.

    Args:
        api_key: IBM Cloud API key.

    Returns:
        Bearer token string.
    """
    response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={
            "apikey": api_key,
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        },
    )
    response.raise_for_status()
    return response.json()["access_token"]


# ── Model scoring ─────────────────────────────────────────────────────

MODEL_FIELDS = [
    "CheckingStatus", "LoanDuration", "CreditHistory", "LoanPurpose",
    "LoanAmount", "ExistingSavings", "EmploymentDuration", "InstallmentPercent",
    "Sex", "OthersOnLoan", "CurrentResidenceDuration", "OwnsProperty",
    "Age", "InstallmentPlans", "Housing", "ExistingCreditsCount",
    "Job", "Dependents", "Telephone", "ForeignWorker",
]


def score_model(token: str, values: dict) -> dict:
    """Send a scoring request to the deployed ML model.

    Args:
        token: IAM bearer token.
        values: dict mapping field names to values.

    Returns:
        dict with prediction and probability.
    """
    ordered_values = [values[field] for field in MODEL_FIELDS]

    payload = {
        "input_data": [{
            "fields": MODEL_FIELDS,
            "values": [ordered_values],
        }]
    }

    response = requests.post(
        WATSONX_API_ENDPOINT,
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()

    result = response.json()
    prediction = result["predictions"][0]["values"][0][0]
    probability = result["predictions"][0]["values"][0][1][0]

    return {
        "prediction": prediction,
        "confidence": round(probability, 4),
    }


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Predictive ML — Direct Model Scoring API")
    print(f"Endpoint: {WATSONX_API_ENDPOINT[:60]}...\n")

    # Load sample payloads
    with open("sample_data/credit_risk_payload.json") as f:
        sample = json.load(f)

    # Authenticate
    print("Authenticating with IBM Cloud IAM...")
    token = get_iam_token(WATSONX_APIKEY)
    print("  Token obtained.\n")

    # Score each payload
    print("=" * 60)
    print("MODEL SCORING RESULTS")
    print("=" * 60)

    for payload in sample["payloads"]:
        print(f"\n  Scenario: {payload['label']}")
        result = score_model(token, payload["values"])
        print(f"    Prediction: {result['prediction']}")
        print(f"    Confidence: {result['confidence']:.2%}")
