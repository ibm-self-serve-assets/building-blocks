# wx_gov_agent_eval

Production-ready Python package for evaluating LangGraph agents using IBM watsonx.governance.

## Overview

`wx_gov_agent_eval` provides a unified, developer-friendly interface for evaluating different types of AI agents with comprehensive metrics tracking, experiment management, and integration with IBM watsonx.governance.

### Key Features

- **Drop-in LangGraph Integration**: Seamlessly evaluate existing LangGraph agents
- **High-Performance Batch Evaluation**: Efficient processing of large test datasets with optional parallelization
- **Comprehensive Metrics Coverage**: Context relevance, faithfulness, answer similarity, tool call accuracy, content safety
- **Multiple Agent Types**: Support for RAG, tool-calling, and multi-source retrieval agents
- **Experiment Tracking**: Built-in integration with watsonx.governance for experiment management
- **Production-Ready**: Type hints, comprehensive error handling, Google-style docstrings

### Supported Agent Types

| Evaluator | Use Case | Key Metrics |
|-----------|----------|-------------|
| `BasicRAGEvaluator` | Simple RAG with local documents | Context relevance, faithfulness, answer similarity |
| `ToolCallingEvaluator` | Agents with custom tools/functions | Tool call accuracy, content safety (optional) |
| `AdvancedRAGEvaluator` | Multi-source RAG with routing | Context relevance, routing accuracy, faithfulness |

## Installation

### Prerequisites

- Python 3.9+
- IBM Cloud account with watsonx.ai access
- watsonx.ai API key and project ID

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Setup

Set required environment variables:

```bash
export WATSONX_APIKEY="your-api-key"
export WATSONX_PROJECT_ID="your-project-id"

# Optional: for web search in AdvancedRAGEvaluator
export TAVILY_API_KEY="your-tavily-key"
```

## Quick Start

### Basic RAG Evaluation

```python
from wx_gov_agent_eval import BasicRAGEvaluator

# Sample documents
documents = [
    {
        "id": "1",
        "document": "Python is a high-level programming language known for its simplicity."
    },
    {
        "id": "2",
        "document": "Machine Learning enables systems to learn from data automatically."
    }
]

# Initialize and build agent
evaluator = BasicRAGEvaluator()
evaluator.build_agent(documents=documents)

# Evaluate single query
result = evaluator.evaluate_single(
    input_text="What is Python?",
    ground_truth="Python is a simple, high-level programming language.",
    interaction_id="test-1"
)

# View results
print(result['generated_text'])
evaluator.display_results()
```

### Tool Calling Evaluation

```python
from wx_gov_agent_eval import ToolCallingEvaluator
from langchain_core.tools import tool

# Define tools
@tool
def get_weather(location: str) -> str:
    """Get current weather for a location."""
    return f"Weather in {location}: Sunny, 72°F"

# Build and evaluate
evaluator = ToolCallingEvaluator()
evaluator.build_agent(tools=[get_weather])

result = evaluator.evaluate_single(
    input_text="What's the weather in Boston?",
    ground_truth="Sunny and 72 degrees"
)

evaluator.display_results()
```

### Batch Evaluation

```python
import pandas as pd
from wx_gov_agent_eval import BasicRAGEvaluator, prepare_test_data

# Prepare test data
test_df = prepare_test_data(
    input_texts=["Question 1", "Question 2", "Question 3"],
    ground_truths=["Answer 1", "Answer 2", "Answer 3"]
)

# Batch evaluate
evaluator = BasicRAGEvaluator()
evaluator.build_agent(documents=documents)

results = evaluator.evaluate_batch(
    test_data=test_df,
    batch_size=10,
    parallel=False
)

# Get metrics DataFrame
metrics_df = evaluator.get_metrics_dataframe()
print(metrics_df)
```

## Package Structure

```
wx_gov_agent_eval/
├── __init__.py              # Package exports
├── config.py                # Configuration dataclasses
├── base_evaluator.py        # Abstract base evaluator class
├── basic_rag.py             # Basic RAG evaluator
├── tool_calling.py          # Tool calling evaluator
├── advanced_rag.py          # Advanced RAG evaluator
└── utils/
    ├── __init__.py          # Utility exports
    ├── auth.py              # Authentication helpers
    ├── vector_store.py      # Vector store management
    ├── metrics.py           # Metrics processing
    └── batch_processing.py  # Batch evaluation utilities
```

## API Reference

### Evaluators

#### BasicRAGEvaluator

Evaluator for simple RAG agents with local document retrieval.

**Methods:**

- `build_agent(documents, vector_store_path=None)`: Build the RAG agent
  - `documents`: List of dicts, PDF path, or URL
  - `vector_store_path`: Optional path to existing vector store

- `evaluate_single(input_text, ground_truth=None, interaction_id="1")`: Evaluate single query
- `evaluate_batch(test_data, batch_size=10, parallel=False)`: Batch evaluation
- `get_results()`: Get evaluation results object
- `get_metrics_dataframe()`: Get metrics as pandas DataFrame
- `display_results(node_name=None)`: Display metrics
- `track_experiment(experiment_name, use_existing=False)`: Enable experiment tracking

**Example:**

```python
evaluator = BasicRAGEvaluator()
evaluator.build_agent(documents=my_docs)
result = evaluator.evaluate_single(
    input_text="What is AI?",
    ground_truth="AI is artificial intelligence"
)
```

#### ToolCallingEvaluator

Evaluator for agents with custom tool/function calling.

**Methods:**

- `build_agent(tools, system_message=None)`: Build tool calling agent
  - `tools`: List of LangChain tools (decorated with @tool)
  - `system_message`: Optional custom system prompt

- Additional methods inherited from `BaseAgentEvaluator`

**Example:**

```python
from langchain_core.tools import tool

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    return str(eval(expression))

evaluator = ToolCallingEvaluator()
evaluator.build_agent(tools=[calculator])
```

#### AdvancedRAGEvaluator

Evaluator for multi-source RAG with intelligent routing.

**Methods:**

- `build_agent(documents, vector_store_path=None, enable_web_search=True, tavily_api_key=None)`: Build advanced RAG agent
  - `documents`: Local documents for vector store
  - `enable_web_search`: Enable web search capability
  - `tavily_api_key`: API key for Tavily (required if enable_web_search=True)

- Additional methods inherited from `BaseAgentEvaluator`

**Example:**

```python
evaluator = AdvancedRAGEvaluator()
evaluator.build_agent(
    documents=docs,
    enable_web_search=True,
    tavily_api_key="your-key"
)
```

### Configuration

#### WatsonxConfig

```python
from wx_gov_agent_eval import WatsonxConfig

# From environment variables
config = WatsonxConfig.from_env()

# Or explicit
config = WatsonxConfig(
    apikey="your-api-key",
    project_id="your-project-id",
    url="https://us-south.ml.cloud.ibm.com"
)
```

#### EvaluationConfig

```python
from wx_gov_agent_eval import EvaluationConfig

config = EvaluationConfig(
    compute_real_time=True,      # Compute metrics in real-time
    enable_tracing=True,          # Enable tracing in watsonx.governance
    batch_size=10,                # Default batch size
    enable_content_safety=True    # Enable PII/HAP/HARM checks
)
```

#### VectorStoreConfig

```python
from wx_gov_agent_eval import VectorStoreConfig

config = VectorStoreConfig(
    embedding_model_id="ibm/slate-30m-english-rtrvr",
    chunk_size=400,
    chunk_overlap=50,
    top_k=3,
    similarity_threshold=0.1,
    persist_directory="vector_store"
)
```

#### LLMConfig

```python
from wx_gov_agent_eval import LLMConfig

config = LLMConfig(
    model_id="meta-llama/llama-3-70b-instruct",
    max_new_tokens=500,
    decoding_method="greedy",
    repetition_penalty=1.0
)
```

### Utility Functions

#### Vector Store Utilities

```python
from wx_gov_agent_eval import create_vector_store, create_retriever

# Create vector store
vector_store = create_vector_store(
    documents=docs,
    chunk_size=400,
    persist_directory="my_store"
)

# Create retriever
retriever = create_retriever(
    vector_store,
    search_type="similarity_score_threshold",
    top_k=3,
    score_threshold=0.1
)
```

#### Metrics Utilities

```python
from wx_gov_agent_eval import format_metrics_dataframe, compare_experiments

# Format metrics
df = format_metrics_dataframe(eval_result)

# Compare experiments
comparison = compare_experiments(
    [result1, result2, result3],
    ["Baseline", "Improved", "Final"]
)
```

#### Batch Processing

```python
from wx_gov_agent_eval import prepare_test_data

# Prepare test data
test_df = prepare_test_data(
    input_texts=["Q1", "Q2"],
    ground_truths=["A1", "A2"],
    interaction_ids=["id1", "id2"]  # Optional
)
```

## Advanced Usage

### Custom Configuration

```python
from wx_gov_agent_eval import (
    BasicRAGEvaluator,
    WatsonxConfig,
    EvaluationConfig,
    VectorStoreConfig,
    LLMConfig
)

# Custom configs
watsonx_config = WatsonxConfig(
    apikey="your-key",
    project_id="your-project"
)

eval_config = EvaluationConfig(
    compute_real_time=True,
    enable_tracing=True,
    batch_size=20
)

vector_config = VectorStoreConfig(
    chunk_size=500,
    top_k=5
)

llm_config = LLMConfig(
    model_id="meta-llama/llama-3-405b-instruct",
    max_new_tokens=1000
)

# Initialize with custom configs
evaluator = BasicRAGEvaluator(
    watsonx_config=watsonx_config,
    eval_config=eval_config,
    vector_store_config=vector_config,
    llm_config=llm_config
)
```

### Experiment Tracking

```python
# Track experiments in watsonx.governance
experiment_id = evaluator.track_experiment(
    experiment_name="RAG Baseline v1",
    use_existing=False
)

# Run evaluations (automatically tracked)
evaluator.evaluate_single(...)
evaluator.evaluate_batch(...)

# Results are logged to watsonx.governance
```

### Performance Optimization

```python
# Use parallel processing for large datasets
results = evaluator.evaluate_batch(
    test_data=large_test_df,
    batch_size=20,
    parallel=True  # Enable parallel processing
)

# Disable real-time computation for better performance
eval_config = EvaluationConfig(compute_real_time=False)
evaluator = BasicRAGEvaluator(eval_config=eval_config)
```

### Content Safety Checks

```python
from wx_gov_agent_eval import ToolCallingEvaluator, EvaluationConfig

# Enable content safety metrics
eval_config = EvaluationConfig(enable_content_safety=True)

evaluator = ToolCallingEvaluator(eval_config=eval_config)
evaluator.build_agent(tools=my_tools)

# Evaluation will include PII, HAP, and HARM metrics
result = evaluator.evaluate_single(...)
```

## Metrics Explained

### Context Relevance
Measures how relevant the retrieved context is to the input question. Higher scores indicate better retrieval quality.

### Faithfulness
Measures whether the generated answer is faithful to the retrieved context (i.e., not hallucinated). Higher scores indicate the answer is grounded in the context.

### Answer Similarity
Measures similarity between the generated answer and ground truth answer. Useful for evaluating answer quality when ground truth is available.

### Tool Call Accuracy
For tool-calling agents, measures whether the correct tools were called with appropriate parameters.

### Content Safety
- **PII Detection**: Identifies personally identifiable information in outputs
- **HAP Detection**: Identifies hate, abuse, and profanity
- **HARM Detection**: Identifies potentially harmful content

## Best Practices

### 1. Use Appropriate Batch Sizes

```python
# For large datasets, use larger batch sizes
evaluator.evaluate_batch(test_data, batch_size=50)

# For complex queries, use smaller batches
evaluator.evaluate_batch(test_data, batch_size=5)
```

### 2. Enable Tracing for Debugging

```python
eval_config = EvaluationConfig(enable_tracing=True)
evaluator = BasicRAGEvaluator(eval_config=eval_config)
# Traces will be available in watsonx.governance
```

### 3. Use Existing Vector Stores

```python
# First run: create and persist
evaluator.build_agent(documents=docs)

# Subsequent runs: reuse
evaluator.build_agent(
    documents=docs,
    vector_store_path="vector_store"
)
```

### 4. Track Experiments Systematically

```python
# Create experiments for different configurations
baseline_id = evaluator.track_experiment("Baseline")
# ... run evaluations ...

improved_id = evaluator.track_experiment("Improved v1")
# ... run evaluations ...

# Compare in watsonx.governance dashboard
```

### 5. Handle API Credentials Securely

```python
# Use environment variables (recommended)
config = WatsonxConfig.from_env()

# Never hardcode credentials in source code
# ❌ config = WatsonxConfig(apikey="hardcoded-key")  # Don't do this
```

## Troubleshooting

### Import Errors

```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Verify watsonx packages
pip list | grep watsonx
```

### Authentication Errors

```bash
# Verify environment variables are set
echo $WATSONX_APIKEY
echo $WATSONX_PROJECT_ID

# Or use explicit configuration
config = WatsonxConfig(apikey="...", project_id="...")
```

### Vector Store Issues

```python
# Clear existing vector store if corrupted
import shutil
shutil.rmtree("vector_store", ignore_errors=True)

# Rebuild
evaluator.build_agent(documents=docs)
```

### Performance Issues

```python
# Disable real-time computation
eval_config = EvaluationConfig(compute_real_time=False)

# Use smaller chunk sizes for documents
vector_config = VectorStoreConfig(chunk_size=200)

# Reduce batch size
evaluator.evaluate_batch(test_data, batch_size=5)
```

## Examples

See `example_usage.py` for comprehensive examples covering:

1. Basic RAG evaluation
2. Tool calling evaluation
3. Advanced RAG evaluation
4. Batch evaluation
5. Experiment tracking

Run examples:

```bash
python example_usage.py
```

## Contributing

When contributing to this package:

1. Follow Google-style docstrings
2. Include type hints for all function signatures
3. Add comprehensive error handling
4. Update tests and documentation
5. Run validation before committing

## License

IBM Internal Use

## Support

For issues or questions:
- Check the troubleshooting section above
- Review `example_usage.py` for usage patterns
- Consult the original notebooks for detailed explanations
- Contact the IBM watsonx.governance team

---

**Version**: 0.1.0
**Author**: IBM
**Last Updated**: 2025-12-23
