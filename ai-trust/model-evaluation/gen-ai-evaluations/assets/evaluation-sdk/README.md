# Prompt Evaluation with IBM watsonx.governance

A production-ready Python package for evaluating prompt template assets using IBM watsonx.governance metrics. Supports both SLM (built-in models) and LLM-as-Judge evaluation approaches.

## Overview

`wx_gov_prompt_eval` provides a comprehensive evaluation framework for prompt templates used in RAG (Retrieval-Augmented Generation) and other generative AI applications. It enables you to measure and track key quality metrics including:

- **Faithfulness** - Whether generated answers are grounded in the provided context
- **Answer relevance** - How relevant answers are to the input questions
- **Answer similarity** - How closely answers match ground truth (LLM-as-judge only)
- **Context relevance** - How relevant retrieved context is to the query
- **Retrieval quality** - Comprehensive retrieval metrics (precision, hit rate, NDCG)
- **ROUGE score** - N-gram overlap with ground truth
- **Content safety** - Detection of PII, harmful content (HAP)
- **Model health** - System performance monitoring

## Prerequisites

Before using this package, you'll need:

- **Python 3.10-3.12** (Python 3.11 recommended)
- **IBM watsonx account** with access to:
  - IBM watsonx.ai (for LLM models)
  - IBM watsonx.governance (for evaluation metrics)
  - Watson OpenScale (for monitoring)
  - Watson Machine Learning (for model deployment)
- **API credentials**:
  - `WOS_URL`, `WOS_USERNAME`, `WOS_PASSWORD` - Watson OpenScale credentials
  - `WML_URL`, `WML_USERNAME`, `WML_PASSWORD` - Watson Machine Learning credentials
  - `PROJECT_ID` - Your watsonx project ID

Don't have access? [Sign up for IBM watsonx](https://www.ibm.com/watsonx)

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd gen-ai-evaluations

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure Credentials

Set your IBM watsonx credentials as environment variables:

```bash
export WOS_URL="https://your-cpd-instance.com"
export WOS_USERNAME="your-username"
export WOS_PASSWORD="your-password"
export WML_URL="https://your-cpd-instance.com"
export WML_USERNAME="your-username"
export WML_PASSWORD="your-password"
export PROJECT_ID="your-project-id"
```

Or create a `.env` file in the project root:

```
WOS_URL=https://your-cpd-instance.com
WOS_USERNAME=your-username
WOS_PASSWORD=your-password
WML_URL=https://your-cpd-instance.com
WML_USERNAME=your-username
WML_PASSWORD=your-password
PROJECT_ID=your-project-id
```

### 3. Run Example

```bash
python example_usage.py
```

### 4. Verify Installation

```bash
# Quick verification
python -c "from wx_gov_prompt_eval import PromptTemplateEvaluator; print('✅ Installation successful!')"
```

## Key Features

### Two Evaluation Modes

1. **SLM (Small Language Model)** - Uses OpenScale's built-in smaller models for efficient evaluation
   - Faster evaluation
   - Lower compute requirements
   - Provides source attributions
   - Cost-effective

2. **LLM-as-Judge** - Uses external LLMs (e.g., Llama 3.1) for sophisticated evaluation
   - More sophisticated analysis
   - Includes answer similarity metric
   - Higher quality judgments
   - Requires more compute resources

### Comprehensive Metrics

- **Quality Metrics**: Faithfulness, answer relevance, answer similarity, ROUGE score
- **Retrieval Metrics**: Context relevance, retrieval precision, hit rate, NDCG, average precision
- **Safety Metrics**: PII detection, harmful content detection (HAP)
- **Performance Metrics**: Model health monitoring

### Flexible Evaluation

- Single prompt template evaluation
- Batch evaluation with multiple test sets
- Real-time or post-processing metric computation
- Integration with IBM watsonx.governance factsheet tracking
- Automated visualization of results

## Basic Usage

### Example 1: SLM Evaluation

```python
from wx_gov_prompt_eval import (
    PromptTemplateEvaluator,
    WatsonxConfig,
    EvaluatorConfig,
    MonitorConfig
)

# Configure for SLM evaluation
watsonx_config = WatsonxConfig()  # Reads from environment variables
evaluator_config = EvaluatorConfig(evaluator_type="slm")

# Create evaluator
evaluator = PromptTemplateEvaluator(
    watsonx_config=watsonx_config,
    evaluator_config=evaluator_config,
    project_id="your-project-id"
)

# Create prompt template
prompt_id = evaluator.create_prompt_template(
    name="RAG Q&A Prompt",
    prompt_text="Answer: {context}\n\nQuestion: {question}",
    prompt_variables={"context": "", "question": ""}
)

# Setup monitoring
subscription_id = evaluator.setup_monitoring(
    context_fields=["context"],
    question_field="question",
    label_column="ground_truth"
)

# Evaluate with test data
evaluator.evaluate("test_data.csv")

# View results
evaluator.display_metrics()
evaluator.plot_metrics()
```

### Example 2: LLM-as-Judge Evaluation

```python
from wx_gov_prompt_eval import (
    PromptTemplateEvaluator,
    WatsonxConfig,
    EvaluatorConfig
)

# Configure for LLM-as-Judge
evaluator_config = EvaluatorConfig(
    evaluator_type="llm",
    model_id="meta-llama/llama-3-1-8b-instruct"
)

# Create evaluator (automatically creates LLM evaluator)
evaluator = PromptTemplateEvaluator(
    watsonx_config=WatsonxConfig(),
    evaluator_config=evaluator_config,
    project_id="your-project-id"
)

# Rest is the same as SLM example
# The evaluation will use LLM-as-judge instead of built-in models
```

See [example_usage.py](example_usage.py) for complete examples.

## Installation Options

### Simple Installation (Recommended)

```bash
pip install -r requirements.txt
```

### Verify Dependencies

```bash
pip list | grep ibm
```

You should see:
- `ibm-watson-openscale`
- `ibm-watson-machine-learning`
- `ibm-aigov-facts-client`

## Documentation

- **[Package Documentation](wx_gov_prompt_eval/README.md)** - Detailed API documentation
- **[Example Code](example_usage.py)** - Complete working examples

## Test Data Format

Your test data CSV should include the following columns:

```csv
user_input,retrieved_contexts,generated_text,ground_truths
"What is Python?","Python is a programming language...","Python is a high-level language.","Python is a programming language."
"What is AI?","AI stands for Artificial Intelligence...","AI is machine intelligence.","AI is the simulation of human intelligence."
```

**Required columns:**
- **Question field** (e.g., `user_input`) - The input question
- **Context field(s)** (e.g., `retrieved_contexts`) - The retrieved context
- **Generated text** (e.g., `generated_text`) - The model's generated answer
- **Ground truth** (e.g., `ground_truths`) - The reference answer

## Troubleshooting

### Common Issues

#### Missing Dependencies

**Symptom**: `ModuleNotFoundError: No module named 'ibm_watson_openscale'`

**Solution**:
```bash
pip install ibm-watson-openscale ibm-watson-machine-learning ibm-aigov-facts-client
```

#### Authentication Errors

**Symptom**: `ValueError: Watson OpenScale credentials are required`

**Solution**: Verify your environment variables or `.env` file contains all required credentials

#### Python Version Issues

**Symptom**: Installation fails or packages incompatible

**Solution**: Use Python 3.11 (recommended) or 3.10-3.12. Python 3.13+ is not yet fully supported.

## Package Structure

```
wx_gov_prompt_eval/
├── README.md                  # Package documentation
├── __init__.py                # Package exports
├── config.py                  # Configuration classes
├── prompt_evaluator.py        # Main evaluator class
└── utils/
    ├── __init__.py            # Utils exports
    ├── auth.py                # Authentication helpers
    ├── watsonx_clients.py     # Client creation utilities
    └── metrics.py             # Metrics extraction and visualization
```

## Requirements

- **Python**: 3.10-3.12 (3.11 recommended)
- **IBM Watson OpenScale**: >= 3.0.0
- **IBM Watson Machine Learning**: >= 1.0.0
- **IBM AI Governance Facts Client**: >= 0.1.0
- **matplotlib**: >= 3.8.0 (for visualization)
- **pandas**: >= 2.1.0, < 2.2.0

See [requirements.txt](requirements.txt) for the complete list.

## Key Differences from Agent Evaluation

This package (`wx_gov_prompt_eval`) focuses on **prompt template evaluation**, while the companion package (`wx_gov_agent_eval`) focuses on **agent evaluation**:

| Feature | Prompt Template Eval | Agent Eval |
|---------|---------------------|------------|
| **Use Case** | Evaluate prompt templates | Evaluate AI agents |
| **Primary Metrics** | Faithfulness, answer relevance | Tool accuracy, answer quality |
| **Evaluation Target** | Prompt effectiveness | Agent behavior |
| **Setup** | Prompt template asset | Agent workflows |
| **Data Source** | RAG pipelines | Agent interactions |

Both packages can be used together for comprehensive evaluation of RAG-based agent systems.

## SLM vs LLM-as-Judge: Choosing the Right Approach

### When to Use SLM (Built-in Models)

✅ **Choose SLM if:**
- You need faster evaluation
- You have limited compute resources
- You want source attributions showing which context contributed to answers
- Cost is a primary concern
- You're doing frequent evaluations during development

### When to Use LLM-as-Judge

✅ **Choose LLM-as-Judge if:**
- You need more sophisticated evaluation
- You want answer similarity metrics
- Evaluation quality is more important than speed
- You have access to larger compute resources
- You're doing final validation before production

### Feature Comparison

| Feature | SLM | LLM-as-Judge |
|---------|-----|--------------|
| **Speed** | ⚡ Fast | 🐢 Slower |
| **Cost** | 💰 Lower | 💰💰 Higher |
| **Source Attributions** | ✓ | ✗ |
| **Answer Similarity** | ✗ | ✓ |
| **Evaluation Quality** | Good | Excellent |
| **N-gram Configuration** | ✓ | ✗ (automatic) |

## Contributing

Contributions are welcome! Please contact shima@ibm.com if you would like to discuss ideas and contribute.

## Support

For issues, questions, or feedback:
- Open an issue in this repository
- Contact: shima@ibm.com

## License

Apache 2.0

---

**Built by IBM Build Engineering**

For detailed API documentation, see [wx_gov_prompt_eval/README.md](wx_gov_prompt_eval/README.md)
