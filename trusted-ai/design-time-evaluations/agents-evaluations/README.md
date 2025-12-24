# Agent Evaluations for IBM watsonx.governance

Production-ready Python package for evaluating AI agents using IBM watsonx.governance metrics.

## 📦 Package: wx_gov_agent_eval

**Production-ready evaluation framework** for RAG and agentic AI applications built with LangChain and IBM watsonx.

### ✅ Status

**Fully validated and production-ready** (as of 2025-12-24)

- ✅ All code tested and working
- ✅ Evaluation metrics functional
- ✅ Complete documentation
- ✅ Example code provided

### 🚀 Installation

#### Prerequisites

- Python 3.9-3.12 (Python 3.11 recommended)
- Virtual environment (recommended)

#### Option 1: Simple Installation (Recommended)

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

**Note**: The `requirements.txt` is structured to handle dependency resolution automatically. However, if you encounter dependency conflicts, use Option 2 below.

#### Option 2: Step-by-Step Installation (If conflicts occur)

If you experience dependency conflicts with Option 1, install in this specific order:

```bash
# Step 1: Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Step 2: Upgrade pip
pip install --upgrade pip

# Step 3: Install core IBM packages first (this resolves most dependencies)
pip install ibm-watsonx-gov==1.2.2 \
            ibm-watsonx-ai>=1.3.0 \
            ibm-agent-analytics>=0.5.0 \
            pandas>=2.1.0,\<2.2.0 \
            python-dotenv

# Step 4: Install LangChain and supporting packages
pip install langchain>=0.3.0,\<0.4.0 \
            langchain-core>=0.3.0,\<0.4.0 \
            langchain-community>=0.3.0,\<0.4.0 \
            langchain-ibm>=0.3.0,\<0.4.0 \
            langgraph>=0.3.0,\<0.4.0

# Step 5: Install vector store and utilities
pip install chromadb>=0.4.22 \
            unitxt \
            scikit-learn \
            textstat \
            nltk \
            jsonpath-ng \
            pypdf

# Step 6: Install Jupyter (if needed for notebooks)
pip install jupyter ipykernel ipython nbformat
```

**Why this order?**
- Installing IBM packages first ensures opentelemetry and analytics dependencies are resolved correctly
- ChromaDB must be >= 0.4.22 to avoid Rust bindings bugs (version 1.1.1 has critical bugs)

#### Quick Start After Installation

```bash
# Set environment variables
export WATSONX_APIKEY="your-api-key"
export WXG_PROJECT_ID="your-project-id"  # or WATSONX_PROJECT_ID

# Run example
python example_usage.py
```

#### Verify Installation

```bash
# Quick verification
python -c "from wx_gov_agent_eval import BasicRAGEvaluator; print('✅ Installation successful!')"

# Full validation
python validate_package.py

# Run tests
python test_integration.py
```

### 📚 Documentation

- **[Package README](wx_gov_agent_eval/README.md)** - Comprehensive package documentation
- **[example_usage.py](example_usage.py)** - Complete working examples
- **[test_integration.py](test_integration.py)** - Integration tests

### 🔧 Key Features

1. **BasicRAGEvaluator** - Simple RAG agent evaluation with local vector stores
2. **AdvancedRAGEvaluator** - Multi-source RAG with intelligent routing (local + web search)
3. **ToolCallingEvaluator** - Custom tool/function calling agent evaluation

### 📊 Metrics Evaluated

- Context relevance
- Faithfulness
- Answer similarity
- Tool call accuracy
- Content safety (PII, HAP, HARM detection)
- Latency and token cost tracking

### ⚙️ Requirements

- **Python**: 3.9-3.12 (3.11 recommended)
- **IBM watsonx.governance**: 1.2.2
- **IBM agent analytics**: Required for evaluation metrics
- See [requirements.txt](requirements.txt) for full list

### 🎯 Critical Dependencies

⚠️ **Important**: The `ibm-agent-analytics` packages are **required** but not declared as dependencies by IBM SDK:

```
ibm-agent-analytics>=0.5.0
ibm-agent-analytics-common>=0.1.0
ibm-agent-analytics-core>=0.9.0
```

These are included in `requirements.txt` and must be installed for evaluation metrics to work.

### 📁 Package Structure

```
wx_gov_agent_eval/
├── __init__.py              # Package exports
├── config.py                # Configuration classes
├── base_evaluator.py        # Abstract base class
├── basic_rag.py            # Basic RAG evaluator
├── advanced_rag.py         # Advanced RAG with routing
├── tool_calling.py         # Tool calling evaluator
└── utils/
    ├── auth.py             # Authentication helpers
    ├── vector_store.py     # Vector store utilities
    ├── metrics.py          # Metrics helpers
    └── batch_processing.py # Batch evaluation utilities
```

### 🧪 Testing

```bash
# Validate package structure
python validate_package.py

# Run integration tests
python test_integration.py
```

### 🔧 Troubleshooting

#### Dependency Conflicts

If you encounter dependency conflicts during installation:

1. **Use Python 3.11**: Some packages don't support Python 3.13+ yet
2. **Try Option 2 installation**: Step-by-step installation resolves conflicts
3. **Check ChromaDB version**: Must be >= 0.4.22 (not 1.1.1 which has bugs)

#### Missing ibm-agent-analytics

If you see this warning:
```
No module named 'ibm_agent_analytics'
```

**Solution**: Install the agent analytics packages:
```bash
pip install ibm-agent-analytics ibm-agent-analytics-common ibm-agent-analytics-core
```

These packages are **required** for evaluation metrics but not declared by IBM SDK.

#### Evaluation Fails with NameError

If evaluation fails with errors like:
- `NameError: name 'AIEventRecorder' is not defined`
- `NameError: name 'get_current_trace_id' is not defined`

**Solution**: You're missing `ibm-agent-analytics` packages. Install them as shown above.

#### ChromaDB Rust Bindings Error

If you see:
```
pyo3_runtime.PanicException: range start index 10 out of range
```

**Solution**: Upgrade ChromaDB:
```bash
pip install --upgrade "chromadb>=0.4.22"
```

#### Model Not Found Error

If you see:
```
Model 'ibm/slate-30m-english-rtrvr' was not found
```

**Solution**: The package uses the updated model ID `ibm/slate-30m-english-rtrvr-v2`. This is already configured in the code. If you're using an old version, update to the latest package.

### 📝 Example Usage

```python
from wx_gov_agent_eval import BasicRAGEvaluator

# Create evaluator
evaluator = BasicRAGEvaluator()

# Build agent with your documents
evaluator.build_agent(documents=my_docs)

# Evaluate
result = evaluator.evaluate_single(
    input_text="What is Python?",
    ground_truth="Python is a programming language..."
)

# View results
evaluator.display_results()
```

See [example_usage.py](example_usage.py) for complete examples.

### 🤝 Contributing

This package is production-ready and has been thoroughly validated. See [VALIDATION_REPORT.md](VALIDATION_REPORT.md) for details.

### 📄 License

[Add your license here]

### 👥 Authors

IBM Trusted AI Team

---

For detailed package documentation, see [wx_gov_agent_eval/README.md](wx_gov_agent_eval/README.md)
