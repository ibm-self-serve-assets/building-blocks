
# wx_gov_prompt_eval - Package Documentation

Detailed API documentation for the `wx_gov_prompt_eval` package.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Core Classes](#core-classes)
- [Configuration](#configuration)
- [Utilities](#utilities)
- [Evaluation Workflow](#evaluation-workflow)
- [Metrics](#metrics)
- [Best Practices](#best-practices)

## Overview

The `wx_gov_prompt_eval` package provides a production-ready framework for evaluating prompt template assets in IBM watsonx.governance. It supports two evaluation approaches:

1. **SLM (Small Language Model)**: Uses OpenScale's built-in smaller models for efficient evaluation
2. **LLM-as-Judge**: Uses external large language models (e.g., Llama 3.1) for sophisticated evaluation

## Architecture

```
wx_gov_prompt_eval/
├── __init__.py              # Package exports
├── config.py                # Configuration dataclasses
├── prompt_evaluator.py      # Main evaluator class
├── utils/
│   ├── __init__.py          # Utils exports
│   ├── auth.py              # Authentication helpers
│   ├── watsonx_clients.py   # Client creation utilities
│   └── metrics.py           # Metrics extraction and visualization
└── README.md                # This file
```

## Core Classes

### PromptTemplateEvaluator

The main class for evaluating prompt templates.

```python
from wx_gov_prompt_eval import PromptTemplateEvaluator, WatsonxConfig

watsonx_config = WatsonxConfig(
    wos_url="https://your-cpd-instance.com",
    wos_username="user@example.com",
    wos_password="password",
    wml_url="https://your-cpd-instance.com",
    wml_username="user@example.com",
    wml_password="password"
)

evaluator = PromptTemplateEvaluator(
    watsonx_config=watsonx_config,
    project_id="your-project-id"
)
```

**Key Methods:**

- `create_prompt_template()`: Create a new prompt template asset
- `setup_monitoring()`: Configure OpenScale monitoring
- `evaluate()`: Run evaluation with test data
- `display_metrics()`: Display evaluation results
- `get_record_level_metrics()`: Get detailed record-level metrics
- `plot_metrics()`: Visualize metrics
- `get_factsheets_url()`: Get URL to view factsheets

## Configuration

### WatsonxConfig

Manages authentication credentials for IBM watsonx services.

```python
from wx_gov_prompt_eval import WatsonxConfig

# Option 1: Explicit credentials
config = WatsonxConfig(
    wos_url="https://cpd-instance.com",
    wos_username="user@example.com",
    wos_password="password123",
    wml_url="https://cpd-instance.com",
    wml_username="user@example.com",
    wml_password="password123"
)

# Option 2: From environment variables
# Set WOS_URL, WOS_USERNAME, WOS_PASSWORD, WML_URL, WML_USERNAME, WML_PASSWORD
config = WatsonxConfig()
```

**Attributes:**
- `wos_url`: Watson OpenScale service URL
- `wos_username`: Watson OpenScale username
- `wos_password`: Watson OpenScale password
- `wml_url`: Watson Machine Learning service URL
- `wml_username`: Watson Machine Learning username
- `wml_password`: Watson Machine Learning password
- `wml_instance_id`: WML instance ID (default: "wml_local")
- `wml_version`: WML API version (default: "5.0")

### EvaluatorConfig

Configures the evaluation approach (SLM vs LLM-as-Judge).

```python
from wx_gov_prompt_eval import EvaluatorConfig

# For SLM (built-in models)
slm_config = EvaluatorConfig(evaluator_type="slm")

# For LLM-as-Judge
llm_config = EvaluatorConfig(
    evaluator_type="llm",
    model_id="meta-llama/llama-3-1-8b-instruct",
    evaluator_name="Llama 3.1 Judge",
    evaluator_description="Evaluation using Llama 3.1"
)
```

**Attributes:**
- `evaluator_type`: "slm" or "llm"
- `enabled`: Whether to use the evaluator (default: True)
- `evaluator_id`: ID of evaluator integrated system (auto-created for LLM)
- `model_id`: Model ID for LLM-as-judge (default: "meta-llama/llama-3-1-8b-instruct")
- `evaluator_name`: Name for the evaluator
- `evaluator_description`: Description for the evaluator

**Key Methods:**
- `is_llm_as_judge()`: Returns True if configured for LLM-as-judge
- `is_slm()`: Returns True if configured for SLM

### MonitorConfig

Configures OpenScale monitoring parameters and metrics.

```python
from wx_gov_prompt_eval import MonitorConfig

config = MonitorConfig(
    # Core settings
    min_sample_size=1,

    # Faithfulness
    faithfulness_enabled=True,
    faithfulness_attributions_count=3,  # SLM only
    faithfulness_ngrams=2,  # SLM only

    # Answer relevance
    answer_relevance_enabled=True,

    # Answer similarity (LLM-as-judge only)
    answer_similarity_enabled=True,

    # ROUGE score
    rouge_score_enabled=True,

    # Context relevance
    context_relevance_enabled=True,
    context_relevance_ngrams=2,  # SLM only

    # Retrieval quality
    retrieval_quality_enabled=True,

    # Safety metrics
    pii_enabled=False,
    hap_enabled=False
)
```

**Attributes:**
- `min_sample_size`: Minimum sample size for metrics (default: 1)
- `faithfulness_enabled`: Enable faithfulness metric
- `faithfulness_attributions_count`: Number of source attributions (SLM only, default: 3)
- `faithfulness_ngrams`: N-gram grouping for faithfulness (SLM only, default: 2)
- `answer_relevance_enabled`: Enable answer relevance metric
- `answer_similarity_enabled`: Enable answer similarity (LLM-as-judge only)
- `rouge_score_enabled`: Enable ROUGE score metric
- `context_relevance_enabled`: Enable context relevance metric
- `context_relevance_ngrams`: N-gram grouping for context relevance (SLM only, default: 2)
- `retrieval_quality_enabled`: Enable retrieval quality metrics
- `unsuccessful_requests_enabled`: Enable unsuccessful requests detection
- `pii_enabled`: Enable PII detection
- `hap_enabled`: Enable HAP (Hate, Abuse, Profanity) detection

**Key Methods:**
- `to_openscale_config()`: Convert to OpenScale monitor configuration format

## Utilities

### Authentication

```python
from wx_gov_prompt_eval.utils import generate_access_token

credentials = {
    "url": "https://cpd-instance.com",
    "username": "user@example.com",
    "password": "password123"
}

token = generate_access_token(credentials)
```

### Client Creation

```python
from wx_gov_prompt_eval.utils import (
    create_wos_client,
    create_wml_client,
    create_facts_client
)

wos_client = create_wos_client(wos_credentials)
wml_client = create_wml_client(wml_credentials)
facts_client = create_facts_client(wos_credentials, container_id="project-123")
```

### Metrics Extraction

```python
from wx_gov_prompt_eval.utils import (
    extract_metrics,
    extract_record_level_metrics,
    plot_metrics
)

# Extract metrics
metrics = extract_metrics(wos_client, monitor_instance_id, project_id=project_id)

# Get record-level metrics
df = extract_record_level_metrics(wos_client, dataset_id)

# Plot metrics
plot_metrics(df, metric_columns=["faithfulness", "answer_relevance"])
```

## Evaluation Workflow

### Complete Example: SLM Evaluation

```python
from wx_gov_prompt_eval import (
    PromptTemplateEvaluator,
    WatsonxConfig,
    EvaluatorConfig,
    MonitorConfig
)

# 1. Configure
watsonx_config = WatsonxConfig()  # From environment variables
evaluator_config = EvaluatorConfig(evaluator_type="slm")
monitor_config = MonitorConfig(
    faithfulness_enabled=True,
    answer_relevance_enabled=True,
    rouge_score_enabled=True
)

# 2. Create evaluator
evaluator = PromptTemplateEvaluator(
    watsonx_config=watsonx_config,
    evaluator_config=evaluator_config,
    monitor_config=monitor_config,
    project_id="your-project-id"
)

# 3. Create prompt template
prompt_id = evaluator.create_prompt_template(
    name="RAG Q&A Prompt",
    prompt_text="Answer: {context}\n\nQuestion: {question}",
    prompt_variables={"context": "", "question": ""},
    model_id="ibm/granite-3-8b-instruct"
)

# 4. Setup monitoring
subscription_id = evaluator.setup_monitoring(
    context_fields=["context"],
    question_field="question",
    label_column="ground_truth"
)

# 5. Evaluate
results = evaluator.evaluate("test_data.csv")

# 6. View results
evaluator.display_metrics()
evaluator.plot_metrics()
```

### Complete Example: LLM-as-Judge Evaluation

```python
from wx_gov_prompt_eval import (
    PromptTemplateEvaluator,
    WatsonxConfig,
    EvaluatorConfig,
    MonitorConfig
)

# 1. Configure for LLM-as-Judge
watsonx_config = WatsonxConfig()
evaluator_config = EvaluatorConfig(
    evaluator_type="llm",
    model_id="meta-llama/llama-3-1-8b-instruct"
)
monitor_config = MonitorConfig(
    faithfulness_enabled=True,
    answer_relevance_enabled=True,
    answer_similarity_enabled=True,  # LLM-as-judge only
    rouge_score_enabled=True
)

# 2. Create evaluator (creates LLM evaluator automatically)
evaluator = PromptTemplateEvaluator(
    watsonx_config=watsonx_config,
    evaluator_config=evaluator_config,
    monitor_config=monitor_config,
    project_id="your-project-id"
)

# 3-6. Same as SLM example above
```

## Metrics

### Supported Metrics

| Metric | Description | SLM | LLM-as-Judge |
|--------|-------------|-----|--------------|
| **Faithfulness** | Whether generated answers are grounded in context | ✓ | ✓ |
| **Answer Relevance** | How relevant answers are to questions | ✓ | ✓ |
| **Answer Similarity** | Similarity to ground truth answers | ✗ | ✓ |
| **ROUGE Score** | N-gram overlap with ground truth | ✓ | ✓ |
| **Context Relevance** | How relevant retrieved context is to question | ✓ | ✓ |
| **Retrieval Precision** | Precision of retrieved contexts | ✓ | ✓ |
| **Hit Rate** | Percentage of queries with relevant results | ✓ | ✓ |
| **NDCG** | Normalized Discounted Cumulative Gain | ✓ | ✓ |
| **PII Detection** | Detection of personally identifiable information | ✓ | ✓ |
| **HAP Detection** | Detection of hate, abuse, profanity | ✓ | ✓ |

### SLM-Specific Parameters

When using SLM evaluation, you can configure:

- `faithfulness_attributions_count`: Number of source attributions to identify
- `faithfulness_ngrams`: N-gram grouping for faithfulness scoring
- `context_relevance_ngrams`: N-gram grouping for context relevance scoring

These parameters are not used with LLM-as-judge, which handles attribution internally.

## Best Practices

### 1. Choosing Between SLM and LLM-as-Judge

**Use SLM when:**
- You need faster evaluation
- You have limited compute resources
- You want source attributions
- Cost is a primary concern

**Use LLM-as-Judge when:**
- You need more sophisticated evaluation
- You want answer similarity metrics
- Evaluation quality is more important than speed
- You have access to larger compute resources

### 2. Test Data Format

Your test data CSV should include:

```csv
user_input,retrieved_contexts,generated_text,ground_truths
"What is Python?","[""Python is a programming language...""]","Python is a high-level language.","Python is a programming language."
```

Required columns:
- Question field (e.g., `user_input`)
- Context field(s) (e.g., `retrieved_contexts`)
- Generated text (e.g., `generated_text`)
- Ground truth (e.g., `ground_truths`)

### 3. Environment Variables

Set up a `.env` file:

```bash
WOS_URL=https://your-cpd-instance.com
WOS_USERNAME=user@example.com
WOS_PASSWORD=your-password

WML_URL=https://your-cpd-instance.com
WML_USERNAME=user@example.com
WML_PASSWORD=your-password

PROJECT_ID=your-project-id
```

### 4. Error Handling

```python
try:
    evaluator = PromptTemplateEvaluator(
        watsonx_config=watsonx_config,
        project_id=project_id
    )
    evaluator.create_prompt_template(...)
    evaluator.setup_monitoring(...)
    evaluator.evaluate("test_data.csv")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Evaluation error: {e}")
```

### 5. Monitor Instance Management

The evaluator automatically manages monitor instances:

```python
# These are automatically populated during setup_monitoring()
print(f"Subscription ID: {evaluator.subscription_id}")
print(f"MRM Monitor ID: {evaluator.mrm_monitor_id}")
print(f"GenAI Quality Monitor ID: {evaluator.genaiq_monitor_id}")
```

### 6. Viewing Results in UI

```python
# Get factsheets URL
url = evaluator.get_factsheets_url()
print(f"View factsheets at: {url}")

# Or manually construct:
# https://<cpd-url>/wx/prompt-details/<prompt-id>/factsheet?context=wx&project_id=<project-id>
```

## Advanced Usage

### Custom Monitor Configuration

```python
from wx_gov_prompt_eval.config import MonitorConfig

# Create custom configuration
custom_config = MonitorConfig(
    min_sample_size=5,
    faithfulness_enabled=True,
    faithfulness_attributions_count=5,  # More attributions
    faithfulness_ngrams=3,  # Larger n-grams
    answer_relevance_enabled=True,
    rouge_score_enabled=True,
    pii_enabled=True,  # Enable PII detection
    hap_enabled=True   # Enable HAP detection
)

evaluator = PromptTemplateEvaluator(
    watsonx_config=watsonx_config,
    monitor_config=custom_config,
    project_id=project_id
)
```

### Batch Evaluation

```python
# Evaluate multiple test sets
test_files = ["test_set_1.csv", "test_set_2.csv", "test_set_3.csv"]

results = []
for test_file in test_files:
    result = evaluator.evaluate(test_file)
    results.append(result)
    print(f"Evaluated {test_file}: {result['total_records']} records")
```

### Extracting Specific Metrics

```python
# Get record-level metrics
df = evaluator.get_record_level_metrics()

# Filter for high-performing records
high_faithfulness = df[df['faithfulness'] > 0.8]
print(f"Records with faithfulness > 0.8: {len(high_faithfulness)}")

# Analyze metric distributions
print(df[['faithfulness', 'answer_relevance', 'rouge_score']].describe())
```

## Troubleshooting

### Common Issues

**Issue**: "No prompt template ID provided or stored"
**Solution**: Call `create_prompt_template()` before `setup_monitoring()`

**Issue**: "No subscription ID available"
**Solution**: Call `setup_monitoring()` before `evaluate()` or `display_metrics()`

**Issue**: Authentication errors
**Solution**: Verify credentials in `.env` file or WatsonxConfig

**Issue**: Missing environment variables
**Solution**: Ensure all required variables are set (WOS_URL, WOS_USERNAME, etc.)

## Support

For issues or questions:
- Open an issue in the repository
- Contact: shima@ibm.com

---

**Built by IBM Build Engineering**
