# Real-Time AI Guardrails

This repository demonstrates how to use the Watsonx Governance SDK to implement real-time guardrails for generative AI models. These guardrails help detect and block undesired behavior instantly. These AI guardrails **can be applied to both AI inputs** (evaluating and filtering user queries before they reach the model) **and AI outputs** (ensuring generated responses are checked before being returned to end users).

To showcase these capabilities, we provide a Dash-based web application that performs real-time evaluations for content safety, bias detection, RAG quality metrics, and more.

## Features

- **Content Safety Metrics**: HAP, PII Detection, Harm Detection, Violence, Profanity, Social Bias, Jailbreak Detection, Unethical Behavior, Sexual Content, Evasiveness
- **RAG Evaluation Metrics**: Answer Relevance, Context Relevance, Faithfulness
- **Interactive Dashboard**: Select multiple guardrails, adjust risk thresholds, and view color-coded results
- **Export Results**: Download evaluation results as CSV files

## Prerequisites

- Python 3.11+ (recommended)
- IBM watsonx.ai account with API credentials
- IBM watsonx.governance access

## Setup Instructions

### 1. Create Virtual Environment

```bash
python3 -m venv venv
```

### 2. Activate Virtual Environment

**MacOS/Linux:**
```bash
source venv/bin/activate
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

The `.env` file should already be present with your credentials. Verify it contains:

```env
WATSONX_APIKEY=your_api_key_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WXG_SERVICE_INSTANCE_ID=your_service_instance_id_here
```

To get your credentials:
- **API Key**: [IBM Cloud Console](https://cloud.ibm.com/) > Manage > Access (IAM) > API keys
- **Service Instance ID**: Find in your watsonx.governance service details

### 5. Run the Application

```bash
python app.py
```

The app will start on `http://localhost:8050`

## Usage

1. **Select Guardrails**: Use the left sidebar to choose which metrics to evaluate
2. **Enter Text**: Type or paste text into the main input area
3. **Configure Threshold**: Adjust the risk threshold slider (default: 0.7)
4. **Advanced Options** (optional): Click "Show Advanced" for RAG-specific inputs
   - Context: Provide context for RAG evaluation
   - Generated Response: Enter AI-generated text to evaluate
5. **Run Evaluation**: Click "Run Guardrails" to analyze the text
6. **View Results**: Results display with color-coding:
   - 🔴 Red: High risk 
   - 🟢 Green: Low risk

## Application Structure

```
design-time-dash-app/
├── app.py                    # Main Dash application
├── app-config.properties     # UI configuration
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (credentials)
├── README.md                # This file
└── assets/
    ├── customStyles.css     # Custom styling
    ├── design_time_logo.png # Logo images
    └── logo.png
```

## Key Components

### Metrics Categories

**Content Safety**
- Detects harmful, biased, or inappropriate content
- Identifies security threats like jailbreak attempts
- Filters PII and sensitive information

**RAG Evaluation**
- Assesses quality of retrieval-augmented generation
- Measures relevance and faithfulness
- Validates context usage

### Configuration

Modify `app-config.properties` to customize:
- Application title
- Helper text
- Footer content

## Troubleshooting

**Issue: "Failed to initialize evaluator"**
- Check your `.env` file contains valid credentials
- Verify API key has necessary permissions
- Ensure service instance ID is correct

**Issue: Dependencies installation fails**
- Ensure you're using Python 3.11+
- Try upgrading pip: `pip install --upgrade pip`
- Install dependencies one at a time to identify issues

**Issue: Port 8050 already in use**
- Change the port in `.env`: `SERVICE_PORT=8051`
- Or stop other applications using port 8050

## API Documentation

- [IBM watsonx.governance SDK](https://ibm.github.io/ibm-watsonx-gov/index.html)
- [Dash Framework](https://dash.plotly.com/)

## Security Notes

- Never commit `.env` file to version control
- Rotate API keys regularly
- Do not input sensitive or confidential data into the app

---

**Built with Dash and IBM watsonx.governance**
