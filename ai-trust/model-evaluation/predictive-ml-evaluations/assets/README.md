# Predictive ML Model Evaluation — Technical Assets

Code samples for scoring and evaluating predictive ML models deployed on IBM watsonx ML.

## What's Inside

| Script | What It Does |
|--------|-------------|
| `01_credit_risk_prediction.py` | Interactive Dash web app for credit risk scoring — enter applicant data, get real-time predictions with confidence scores |
| `02_model_scoring_api.py` | Direct model scoring via REST API — lightweight, no UI, suitable for batch scoring and pipeline integration |

## Prerequisites

- Python >= 3.11
- IBM Cloud API key
- A deployed predictive ML model on watsonx ML (the credit risk model endpoint URL)
- `pip install -r requirements.txt`

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set credentials
export WATSONX_API_KEY="your-ibm-cloud-api-key"
export WATSONX_API_ENDPOINT="https://us-south.ml.cloud.ibm.com/ml/v4/deployments/<id>/predictions?version=2024-01-01"

# 3a. Run the Dash app (interactive UI)
python 01_credit_risk_prediction.py
# Open http://localhost:8066

# 3b. OR run direct API scoring (no UI)
python 02_model_scoring_api.py
```

## How It Works

### Authentication
Both scripts authenticate via IBM Cloud IAM token exchange:
```
API Key → POST https://iam.cloud.ibm.com/identity/token → Bearer Token
```

### Scoring
The deployed model accepts a structured payload with 20 credit risk fields and returns:
- **Prediction**: "Risk" or "No Risk"
- **Confidence**: Probability score (0.0 – 1.0)

### Credit Risk Fields
| Field | Example Values |
|-------|---------------|
| CheckingStatus | no_checking, less_0, 0_to_200, greater_200 |
| LoanDuration | 12, 24, 48 (months) |
| CreditHistory | credits_paid_to_date, no_credits, all_credits_paid_back |
| LoanPurpose | car_new, car_used, furniture, other |
| LoanAmount | 1000 – 50000 |
| ExistingSavings | less_100, 100_to_500, 500_to_1000, greater_1000 |
| EmploymentDuration | less_1, 1_to_4, 4_to_7, greater_7 |
| Age | 18 – 75 |
