"""
Credit Risk Prediction — Interactive Dashboard

A Dash-based web application for credit risk scoring using a watsonx ML
deployed model. Provides an interactive UI for entering credit application
data and viewing real-time predictions with confidence scores.

Based on the IBM watsonx ML credit risk prediction example.

Prerequisites:
  pip install -r requirements.txt
  export WATSONX_APIKEY="your-ibm-cloud-api-key"
  export WATSONX_API_ENDPOINT="your-model-deployment-url"

Usage:
  python 01_credit_risk_prediction.py
  # Open http://localhost:8066 in your browser
"""

import os
import sys

import dash
import dash_bootstrap_components as dbc
import requests
from dash import Input, Output, State, html
from dotenv import load_dotenv

load_dotenv()

WATSONX_APIKEY = os.environ.get("WATSONX_APIKEY")
WATSONX_API_ENDPOINT = os.environ.get("WATSONX_API_ENDPOINT")

if not WATSONX_APIKEY or not WATSONX_API_ENDPOINT:
    print("ERROR: Set WATSONX_APIKEY and WATSONX_API_ENDPOINT in your environment.")
    sys.exit(1)


# ── Authentication ────────────────────────────────────────────────────

def get_iam_token() -> str:
    """Obtain an IAM bearer token from IBM Cloud."""
    response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={
            "apikey": WATSONX_APIKEY,
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


def score_credit_risk(values: list) -> dict:
    """Send credit data to the deployed ML model and return prediction."""
    token = get_iam_token()
    payload = {"input_data": [{"fields": MODEL_FIELDS, "values": [values]}]}

    response = requests.post(
        WATSONX_API_ENDPOINT,
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()
    result = response.json()

    prediction = result["predictions"][0]["values"][0][0]
    probability = result["predictions"][0]["values"][0][1][0]
    return {"prediction": prediction, "confidence": round(probability, 2)}


# ── Dash App ──────────────────────────────────────────────────────────

app = dash.Dash(
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.BOOTSTRAP,
        "https://fonts.googleapis.com/css?family=IBM+Plex+Sans:400,600&display=swap",
    ],
    suppress_callback_exceptions=True,
)
app.title = "Credit Risk Prediction"


def make_input(label: str, input_id: str, default: str, input_type: str = "text") -> dbc.Col:
    """Create a labeled input column."""
    return dbc.Col([
        dbc.Label(label),
        dbc.Input(id=input_id, value=default, type=input_type, className="mb-3"),
    ], md=4)


# Layout
app.layout = dbc.Container([
    dbc.Navbar(
        dbc.Col("Credit Risk Prediction — watsonx ML",
                style={"fontSize": "0.875rem", "fontWeight": "600"}),
        style={"paddingLeft": "1rem", "height": "3rem",
               "borderBottom": "1px solid #393939", "color": "#fff"},
        class_name="bg-dark",
    ),

    html.Br(),
    html.H4("Enter Credit Application Data"),

    dbc.Accordion([
        dbc.AccordionItem([
            dbc.Row([
                make_input("Checking Status", "checking", "0_to_200"),
                make_input("Loan Duration (months)", "duration", "24", "number"),
                make_input("Credit History", "history", "credits_paid_to_date"),
            ]),
            dbc.Row([
                make_input("Loan Purpose", "purpose", "car_new"),
                make_input("Loan Amount", "amount", "5000", "number"),
                make_input("Existing Savings", "savings", "500_to_1000"),
            ]),
        ], title="Loan Details"),

        dbc.AccordionItem([
            dbc.Row([
                make_input("Employment Duration", "employment", "4_to_7"),
                make_input("Installment %", "installment", "2", "number"),
                make_input("Sex", "sex", "male"),
            ]),
            dbc.Row([
                make_input("Others on Loan", "others", "none"),
                make_input("Residence Duration (years)", "residence", "4", "number"),
                make_input("Property", "property", "real_estate"),
            ]),
            dbc.Row([
                make_input("Age", "age", "35", "number"),
                make_input("Installment Plans", "plans", "none"),
                make_input("Housing", "housing", "own"),
            ]),
            dbc.Row([
                make_input("Existing Credits", "credits", "1", "number"),
                make_input("Job", "job", "skilled"),
                make_input("Dependents", "dependents", "1", "number"),
            ]),
            dbc.Row([
                make_input("Telephone", "telephone", "yes"),
                make_input("Foreign Worker", "foreign", "yes"),
            ]),
        ], title="Personal Details"),
    ], start_collapsed=False),

    html.Br(),
    dbc.Button("Predict Credit Risk", id="predict-btn", color="primary", n_clicks=0),
    html.Br(), html.Br(),

    dbc.Card([
        dbc.CardBody([
            html.H5("Prediction Result", className="card-title"),
            html.Div(id="prediction-output", children="Submit the form to see results."),
        ])
    ]),
], fluid=True)


@app.callback(
    Output("prediction-output", "children"),
    Input("predict-btn", "n_clicks"),
    [State("checking", "value"), State("duration", "value"),
     State("history", "value"), State("purpose", "value"),
     State("amount", "value"), State("savings", "value"),
     State("employment", "value"), State("installment", "value"),
     State("sex", "value"), State("others", "value"),
     State("residence", "value"), State("property", "value"),
     State("age", "value"), State("plans", "value"),
     State("housing", "value"), State("credits", "value"),
     State("job", "value"), State("dependents", "value"),
     State("telephone", "value"), State("foreign", "value")],
)
def handle_predict(n_clicks, checking, duration, history, purpose, amount,
                   savings, employment, installment, sex, others, residence,
                   prop, age, plans, housing, credits, job, dependents,
                   telephone, foreign):
    if n_clicks == 0:
        return "Submit the form to see results."

    values = [
        checking, float(duration), history, purpose, float(amount),
        savings, employment, float(installment), sex, others,
        float(residence), prop, float(age), plans, housing,
        float(credits), job, float(dependents), telephone, foreign,
    ]

    try:
        result = score_credit_risk(values)
        color = "success" if result["prediction"] == "No Risk" else "danger"
        return html.Div([
            html.Span("Credit Risk: "),
            html.B(result["prediction"], style={"color": color}),
            html.Br(),
            html.Span("Confidence: "),
            html.B(f"{result['confidence']:.0%}"),
        ])
    except Exception as e:
        return html.Div(f"Error: {e}", style={"color": "red"})


if __name__ == "__main__":
    port = int(os.environ.get("SERVICE_PORT", "8066"))
    print(f"Starting Credit Risk Prediction app on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
