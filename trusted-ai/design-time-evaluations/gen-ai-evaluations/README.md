# Design Time Evaluations & Guardrails

An advanced AI guardrails framework leveraging **IBM watsonx.governance SDK** to deliver robust, enterprise-grade **AI safety evaluation**, compliance validation, and real-time monitoring capabilities.

---

## 📘 Table of Contents
- [Overview](#overview)  
- [Architecture](#architecture)  
- [Features](#features)  
- [Technology Stack](#technology-stack)  
- [Prerequisites](#prerequisites)  
- [Project Structure](#project-structure)  
- [Developer Guide](#developer-guide)  
- [Configuration](#configuration)  
- [Usage](#usage)  
- [Examples](#examples)  
- [Coming Soon](#coming-soon)  
- [Contributing](#contributing)  
- [License](#license)  

---

## Overview

This project provides comprehensive **AI guardrails** for both **design-time evaluations** and **runtime monitoring** using the **IBM watsonx.governance** platform. It integrates a broad range of evaluation metrics for assessing AI-generated content against multiple risk categories — including **hate speech**, **bias**, **jailbreak attempts**, **harmful content**, and **ethical violations**.

The framework empowers developers to test, validate, and continuously monitor **LLM-based systems** to ensure compliance, fairness, and safety across their AI lifecycle. By combining **pre-deployment validation** with **real-time governance**, it enables organizations to operationalize **trustworthy AI** effectively.

---

## Architecture

The architecture integrates modular components for both design-time and runtime AI evaluation workflows:

1. **Design-Time Evaluation Engine** – Executes batch-based safety, bias, and relevance assessments before model deployment.  
2. **Real-Time Monitoring Layer** – Provides continuous inference-time evaluations, logging, and drift detection.  
3. **Granite Guardian Integration** – Utilizes IBM’s **Granite Guardian LLM** for PII detection, harm classification, and ethical risk scoring.  
4. **Governance Orchestrator (watsonx.governance SDK)** – Manages metric definitions, data lineage, and evaluation storage.  
5. **Visualization Layer (Streamlit UI + Jupyter)** – Offers both developer and analyst-friendly interfaces for interactive testing and auditability.

---

## Features

### Content Safety Detection
- **Hate, Abuse, Profanity (HAP)** detection for text moderation  
- **PII Detection** for identifying and redacting sensitive user data  
- **Bias and Harm Evaluation** leveraging reference-based scoring models  
- **Prompt Injection / Jailbreak Detection** to secure LLM endpoints  
- **Violence, Profanity, and Ethical Risk Metrics** for compliance-driven domains  

### Advanced Evaluation Metrics
- **Topic Relevance** – Ensures contextual alignment with the prompt  
- **Faithfulness & Groundedness** – Verifies factual accuracy against reference data  
- **Prompt Safety Risk** – Detects off-topic or manipulative input content  
- **Context Relevance** – Evaluates semantic linkage between query and response  

### Dual Evaluation Modes
- **Design-Time Evaluation** – Batch testing with ground truth datasets  
- **Real-Time Monitoring** – Continuous runtime scoring with latency-aware evaluation  

---

## Technology Stack

- **Programming Language:** Python 3.10+  
- **Core SDK:** IBM watsonx.governance SDK  
- **LLM Engine:** Granite Guardian Models  
- **Frontend Interface:** Streamlit (interactive UI)  
- **Backend Framework:** Jupyter Notebooks for prototyping  
- **Environment Configuration:** python-dotenv  
- **Cloud Services:** IBM Cloud SDK for authentication & API integration  

---

## Prerequisites

1. IBM watsonx.governance Service Instance — [Create on IBM Cloud](https://cloud.ibm.com/catalog/services/watsonxgovernance)  
2. IBM Cloud API Key — [Generate here](https://cloud.ibm.com/iam/apikeys)  
3. Python 3.10+ and `pip` installed  
4. Access to Granite Guardian Models (Beta)  
5. Git installed locally  

---

## Project Structure

```
guardrails_v2/
├── .env                           # Environment variables (not in git)
├── .gitignore                     # Git ignore rules
├── CLAUDE.md                      # AI assistant instructions
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── app.py                         # Streamlit web application
├── api_config.ipynb               # API configuration and testing notebook
├── assets/                        # Visual assets and branding
│   ├── design_time_logo.png       # IBM Building Blocks AI Guardrails logo
│   └── README.md                  # Assets documentation
├── lab_exercises/                 # Educational materials and exercises
│   ├── health_test.py             # Health check script for watsonx services
│   ├── watsonx-guardrails-lab.md  # Lab exercise instructions
│   ├── watsonx-instructor-guide.md # Teaching guide for instructors
│   └── watsonx-supplementary-materials.md # Additional learning resources
└── Real Time Detections_v1.ipynb # Main demonstration notebook
```

---

## Developer Guide

### Installation
```bash
git clone <repository-url>
cd guardrails_v2
python -m venv guardrails-env
source guardrails-env/bin/activate
pip install -r requirements.txt
pip install 'ibm-watsonx-gov[metrics]'
```

### Verification
```bash
streamlit run app.py
# or
jupyter notebook "Real Time Detections_v1.ipynb"
```

---

## Configuration

Create a `.env` file in the project root:

```bash
WATSONX_APIKEY=your_ibm_cloud_api_key
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WXG_SERVICE_INSTANCE_ID=your_service_instance_id
WATSONX_REGION=us-south
```

Ensure `.env` is excluded via `.gitignore` for security.

---

## Usage

The system supports **two primary modes of operation**:  
1. **Design-Time Evaluation** – Pre-deployment guardrail testing  
2. **Real-Time Monitoring** – Live evaluation and compliance tracking

### Launch Options
- **Web App (Recommended):** `streamlit run app.py`  
- **Notebook Mode:** Run `Real Time Detections_v1.ipynb`

### Example Use Cases
- Prompt robustness and jailbreak testing  
- Bias and harm evaluation in chatbot responses  
- Compliance validation for sensitive data (PII filtering)  
- Relevance assessment in RAG-based systems  

---

## Examples

```python
from ibm_watsonx_gov.evaluators import MetricsEvaluator
from ibm_watsonx_gov.metrics import HAPMetric, PIIMetric

evaluator = MetricsEvaluator()
text = "This is a sample input for evaluation."

result = evaluator.evaluate(
    data={"input_text": text},
    metrics=[HAPMetric(), PIIMetric()]
)

print(result.to_df())
```

---

## Usage

The guardrails system supports two primary use cases:

### Design Time Evaluations
Perfect for testing prompts, agents, and chatbots before deployment:
- **Prompt Testing**: Validate system prompts for robustness
- **Agent Validation**: Test AI agents against various scenarios
- **Chatbot QA**: Ensure chatbots handle edge cases safely
- **Pre-deployment Audits**: Comprehensive safety assessment before go-live

### Real-Time Monitoring
Continuous evaluation during production:
- **Live Content Screening**: Real-time safety assessment
- **Response Filtering**: Block or flag problematic outputs
- **Compliance Monitoring**: Ongoing regulatory compliance
- **Performance Tracking**: Monitor safety metrics over time

### Option 1: Streamlit Web App (Recommended)
The easiest way to use the guardrails for both design time and real-time evaluation:

```bash
streamlit run app.py
```

**Features:**
- **Interactive UI**: User-friendly web interface
- **Instant Evaluation**: Enter text and get immediate results for design time testing
- **Customizable Guardrails**: Select which metrics to run using checkboxes
- **Configurable Threshold**: Adjust risk threshold with a slider (default: 0.7)
- **Color-coded Results**: Red highlighting for high-risk content
- **Advanced Options**: Support for RAG metrics and system prompts
- **Export Results**: Download results as CSV for design time analysis
- **Reset Functionality**: Clear inputs and start fresh

### Option 2: Jupyter Notebook
Ideal for design time evaluations, development, and experimentation:

1. **Launch Jupyter**: `jupyter notebook` or `jupyter lab`
2. **Open Main Notebook**: `Real Time Detections_v1.ipynb`
3. **Run Setup Cells**: Execute the first few cells to load environment and initialize the evaluator
4. **Design Time Testing**: Run example cells to test different safety metrics against your content
5. **Batch Evaluation**: Test multiple prompts or responses simultaneously for comprehensive design time analysis

### Basic Example
```python
from ibm_watsonx_gov.evaluators import MetricsEvaluator
from ibm_watsonx_gov.metrics import HAPMetric, PIIMetric

# Initialize evaluator (credentials loaded from .env)
evaluator = MetricsEvaluator()

# Test content
text = "This is a sample text to evaluate"

# Run multiple guardrails
result = evaluator.evaluate(
    data={"input_text": text}, 
    metrics=[HAPMetric(), PIIMetric()]
)

# View results
print(result.to_df())
```

### Available Applications

#### `app.py` - Streamlit Web Application
Interactive web interface for both design time and real-time guardrails evaluation:
- User-friendly dashboard with text input and metric selection
- Instant guardrail evaluation with color-coded results for design time testing
- Configurable risk thresholds and advanced options
- Export functionality for design time analysis and compliance reporting
- Can be integrated into production workflows for real-time monitoring

#### `Real Time Detections_v1.ipynb` - Jupyter Notebook
Comprehensive demonstration of all available guardrail metrics, ideal for design time evaluations:
- Content safety detection examples for pre-deployment testing
- RAG (Retrieval-Augmented Generation) evaluation metrics
- Batch evaluation using metric groups for systematic design time analysis
- Real-world content analysis examples for prompt and agent validation

## Hands-On Lab Materials

This repository includes comprehensive educational materials for learning AI guardrails:

### 📚 Lab Exercises (`lab_exercises/`)

#### **For Students/Practitioners:**
- **`watsonx-guardrails-lab.md`** - Step-by-step lab exercise with practical scenarios
- **`health_test.py`** - additional examples for healthcare use cases

#### **For Instructors/Trainers:**
- **`watsonx-instructor-guide.md`** - Complete teaching guide with timing, objectives, and solutions
- **`watsonx-supplementary-materials.md`** - Additional resources, troubleshooting tips, and extended exercises

### 🎯 Lab Features
- **Hands-on Experience**: Practical exercises with real AI guardrail scenarios
- **Progressive Learning**: Structured from basic concepts to advanced implementations
- **Self-Paced**: Complete exercises at your own speed with detailed explanations
- **Instructor Ready**: Full teaching materials for workshops and training sessions
- **Industry Scenarios**: Real-world use cases including chatbot safety, content moderation, and compliance

### 🚀 Getting Started with Labs
1. **Prerequisites**: Complete the main setup (Environment Setup section above)
2. **Health Check**: Run `python lab_exercises/health_test.py` to verify connectivity
3. **Start Learning**: Open `lab_exercises/watsonx-guardrails-lab.md` for guided exercises
4. **Interactive Practice**: Create and run your own notebooks during the lab exercises

Perfect for individual learning, team training, or educational workshops on AI safety and governance.

## Design Time Evaluation Workflows

### Pre-Deployment Testing
Use the guardrails system to validate your AI components before production:

#### 1. Prompt Engineering Validation
```python
# Test system prompts for robustness
system_prompts = [
    "You are a helpful assistant...",
    "Act as a professional advisor...",
    "You are a customer service bot..."
]

for prompt in system_prompts:
    result = evaluator.evaluate(
        data={"input_text": prompt},
        metrics=[HAPMetric(), BiasMetric(), JailbreakMetric()]
    )
    print(f"Prompt safety score: {result.to_df()}")
```

#### 2. Agent Stress Testing
```python
# Test AI agents against challenging scenarios
test_scenarios = [
    "Try to get the agent to reveal sensitive information",
    "Attempt to make the agent ignore its instructions",
    "Test bias in controversial topics"
]

for scenario in test_scenarios:
    # Test your agent's response to each scenario
    agent_response = your_agent.process(scenario)
    
    # Evaluate the response
    result = evaluator.evaluate(
        data={"input_text": agent_response},
        metrics=[HarmMetric(), BiasMetric(), ProfanityMetric()]
    )
```

#### 3. Batch Content Analysis
```python
# Evaluate multiple content samples simultaneously
content_samples = ["sample1", "sample2", "sample3"]
results = []

for content in content_samples:
    result = evaluator.evaluate(
        data={"input_text": content},
        metric_groups=[MetricGroup.CONTENT_SAFETY]
    )
    results.append(result.to_df())

# Analyze patterns and thresholds across all samples
```

## Configuration

### Regional Settings
By default, the project uses the US South region. To use other regions:

```python
import os
os.environ["WATSONX_REGION"] = "eu-de"  # Frankfurt
# Supported: us-south, eu-de, au-syd, ca-tor, jp-tok
```

### Metric Groups
Use predefined metric groups for batch evaluation:
```python
from ibm_watsonx_gov.entities.enums import MetricGroup

# Run all content safety metrics at once
result = evaluator.evaluate(
    data={"input_text": text}, 
    metric_groups=[MetricGroup.CONTENT_SAFETY]
)
```

## Language Support

**Important**: AI guardrails in IBM watsonx.governance currently support **English-language text only**.

## Regional Availability

- **Topic Relevance**: Available in Dallas (us-south) and Frankfurt (eu-de) regions only
- **Prompt Safety Risk**: Available in Dallas (us-south) and Frankfurt (eu-de) regions only
- **Other Metrics**: Available in all supported regions

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify your API key is correct and has watsonx.governance access
   - Check that WXG_SERVICE_INSTANCE_ID is set if you have multiple instances

2. **Module Import Errors**
   - Ensure you're using the correct Python environment
   - Reinstall requirements: `pip install -r requirements.txt`

3. **Regional Errors**
   - Some metrics require specific regions (Dallas/Frankfurt)
   - Set WATSONX_REGION environment variable appropriately

---

## Contributing

Contributions are welcome! Developers can submit PRs or open issues following IBM open-source contribution policies.  
Ensure unit tests and code review standards are met before submitting.

---

## License

Licensed under the **Apache 2.0 License**.  
Refer to the [LICENSE](LICENSE) file for details.

---

## Support

For assistance or technical support, visit [IBM Support Portal](https://cloud.ibm.com/docs/watsonxgovernance).

