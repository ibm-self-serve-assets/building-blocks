# Agent Evaluations for IBM watsonx.governance

A production-ready Python package for evaluating AI agents and RAG (Retrieval-Augmented Generation) applications using IBM watsonx.governance metrics.

## Overview

`wx_gov_agent_eval` provides a comprehensive evaluation framework for AI agents built with LangChain and IBM watsonx. It enables you to measure and track key quality metrics for your AI applications including:

- **Context relevance** - How relevant retrieved context is to the query
- **Faithfulness** - Whether generated answers are grounded in the provided context
- **Answer similarity** - How closely answers match ground truth
- **Tool call accuracy** - Correctness of agent tool/function calls
- **Content safety** - Detection of PII, harmful content, and other safety concerns
- **Performance metrics** - Latency and token cost tracking

## Prerequisites

Before using this package, you'll need:

- **Python 3.9-3.12** (Python 3.11 recommended, 3.13+ not yet supported)
- **IBM watsonx account** with access to:
  - IBM watsonx.ai (for LLM models)
  - IBM watsonx.governance (for evaluation metrics)
- **API credentials**:
  - `WATSONX_APIKEY` - Your IBM Cloud API key
  - `WXG_PROJECT_ID` - Your watsonx project ID

Don't have access? [Sign up for IBM watsonx](https://www.ibm.com/watsonx)

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd agents-evaluations

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
export WATSONX_APIKEY="your-api-key"
export WXG_PROJECT_ID="your-project-id"
```

Or create a `.env` file in the project root:

```
WATSONX_APIKEY=your-api-key
WXG_PROJECT_ID=your-project-id
```

### 3. Run Example

```bash
python example_usage.py
```

### 4. Verify Installation

```bash
# Quick verification
python -c "from wx_gov_agent_eval import BasicRAGEvaluator; print('✅ Installation successful!')"

# Run integration tests
python test_integration.py
```

## Key Features

### Three Evaluation Modes

1. **BasicRAGEvaluator** - Evaluate simple RAG agents with local vector stores
2. **AdvancedRAGEvaluator** - Evaluate multi-source RAG with intelligent routing (local documents + web search)
3. **ToolCallingEvaluator** - Evaluate agents with custom tool/function calling capabilities

### Comprehensive Metrics

- **Quality Metrics**: Context relevance, faithfulness, answer similarity
- **Safety Metrics**: PII detection, harmful content detection (HAP/HARM)
- **Performance Metrics**: Latency tracking, token usage, cost estimation
- **Tool Metrics**: Tool call accuracy for function-calling agents

### Flexible Evaluation

- Single-query evaluation
- Batch evaluation with parallel processing
- Real-time or post-processing metric computation
- Integration with IBM watsonx.governance experiment tracking

## Basic Usage

```python
from wx_gov_agent_eval import BasicRAGEvaluator

# Initialize evaluator
evaluator = BasicRAGEvaluator()

# Prepare your documents
documents = [
    {"id": "1", "document": "Python is a high-level programming language..."},
    {"id": "2", "document": "Machine learning enables systems to learn from data..."}
]

# Build the agent
evaluator.build_agent(documents=documents)

# Evaluate a single query
result = evaluator.evaluate_single(
    input_text="What is Python?",
    ground_truth="Python is a high-level programming language known for simplicity.",
    interaction_id="query-1"
)

# View metrics
print(f"Generated Answer: {result['generated_text']}")
print(f"Metrics: {result.get('metrics', {})}")

# Display all results
evaluator.display_results()
```

See [example_usage.py](example_usage.py) for more complete examples including batch evaluation and advanced RAG.

## Installation Options

### Option 1: Simple Installation (Recommended)

Most users can install all dependencies with a single command:

```bash
pip install -r requirements.txt
```

### Option 2: Step-by-Step Installation

If you encounter dependency conflicts, install in this specific order:

```bash
# Step 1: Install core IBM packages first
pip install ibm-watsonx-gov==1.2.2 \
            ibm-watsonx-ai>=1.3.0 \
            ibm-agent-analytics>=0.5.0 \
            pandas>=2.1.0,<2.2.0 \
            python-dotenv

# Step 2: Install LangChain packages
pip install langchain>=0.3.0,<0.4.0 \
            langchain-core>=0.3.0,<0.4.0 \
            langchain-community>=0.3.0,<0.4.0 \
            langchain-ibm>=0.3.0,<0.4.0 \
            langgraph>=0.3.0,<0.4.0

# Step 3: Install vector store and utilities
pip install chromadb>=0.4.22 \
            unitxt \
            scikit-learn \
            textstat \
            nltk \
            jsonpath-ng \
            pypdf

# Step 4: (Optional) Install Jupyter for notebooks
pip install jupyter ipykernel ipython nbformat
```

**Why this order?** Installing IBM packages first ensures opentelemetry and analytics dependencies are resolved correctly.

## Documentation

- **[Package Documentation](wx_gov_agent_eval/README.md)** - Detailed API documentation
- **[Example Code](example_usage.py)** - Complete working examples
- **[Integration Tests](test_integration.py)** - Test suite for verification

## Troubleshooting

### Common Issues

#### Missing ibm-agent-analytics

**Symptom**: `No module named 'ibm_agent_analytics'`

**Solution**:
```bash
pip install ibm-agent-analytics ibm-agent-analytics-common ibm-agent-analytics-core
```

These packages are required for evaluation metrics but not automatically installed by IBM SDK. They are included in `requirements.txt`.

#### Evaluation NameError

**Symptom**: `NameError: name 'AIEventRecorder' is not defined` or similar

**Solution**: Install `ibm-agent-analytics` packages (see above)

#### ChromaDB Rust Bindings Error

**Symptom**: `pyo3_runtime.PanicException: range start index 10 out of range`

**Solution**: Upgrade ChromaDB to version >= 0.4.22
```bash
pip install --upgrade "chromadb>=0.4.22"
```

#### Python Version Issues

**Symptom**: Installation fails or packages incompatible

**Solution**: Use Python 3.11 (recommended) or 3.9-3.12. Python 3.13+ is not yet fully supported.

#### Dependency Conflicts

**Solution**: Use Option 2 (step-by-step installation) which resolves conflicts by installing packages in the correct order.

## Package Structure

```
wx_gov_agent_eval/
├── README.md               # Package documentation
├── __init__.py             # Package exports
├── config.py               # Configuration classes
├── base_evaluator.py       # Abstract base evaluator
├── basic_rag.py           # Basic RAG evaluator
├── advanced_rag.py        # Advanced RAG with routing
├── tool_calling.py        # Tool calling evaluator
└── utils/
    ├── auth.py            # Authentication helpers
    ├── vector_store.py    # Vector store utilities
    ├── metrics.py         # Metrics computation
    └── batch_processing.py # Batch evaluation
```

## Requirements

- **Python**: 3.9-3.12 (3.11 recommended)
- **IBM watsonx.governance**: 1.2.2
- **IBM watsonx.ai**: >= 1.3.0
- **IBM agent analytics**: >= 0.5.0 (critical for metrics)
- **LangChain**: >= 0.3.0, < 0.4.0
- **ChromaDB**: >= 0.4.22

See [requirements.txt](requirements.txt) for the complete list.

## Contributing

Contributions are welcome! Please contact shima@ibm.com if you would like to discuss ideas and contribute.

## Support

For issues, questions, or feedback:
- Open an issue in this repository

## License

[Specify your license - Apache 2.0, MIT, etc.]

---

**Built by IBM Build Engineering**

For detailed API documentation, see [wx_gov_agent_eval/README.md](wx_gov_agent_eval/README.md)
