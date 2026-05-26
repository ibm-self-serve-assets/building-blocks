"""
wx_gov_agent_eval: Unified package for watsonx.governance agent evaluation.

This package provides production-ready evaluators for LangGraph agents using
IBM watsonx.governance, with support for:
- Basic RAG agents
- Tool-calling agents
- Advanced multi-source RAG agents

Key Features:
- Drop-in LangGraph integration
- High-performance batch evaluation
- Comprehensive metrics (context relevance, faithfulness, answer similarity, tool accuracy)
- Optional content safety checks (PII, HAP, HARM)
- Experiment tracking in watsonx.governance

Example:
    ```python
    from wx_gov_agent_eval import BasicRAGEvaluator

    evaluator = BasicRAGEvaluator()
    evaluator.build_agent(documents=my_docs)
    result = evaluator.evaluate_single(
        input_text="What is AI?",
        ground_truth="AI is..."
    )
    evaluator.display_results()
    ```
"""

__version__ = "0.1.0"
__author__ = "IBM"

# Core evaluators
from .basic_rag import BasicRAGEvaluator
from .tool_calling import ToolCallingEvaluator
from .advanced_rag import AdvancedRAGEvaluator
from .base_evaluator import BaseAgentEvaluator

# Configuration
from .config import (
    WatsonxConfig,
    EvaluationConfig,
    VectorStoreConfig,
    LLMConfig,
)

# Utilities
from .utils.auth import setup_environment, get_api_credentials
from .utils.vector_store import create_vector_store, create_retriever, load_documents_from_url
from .utils.metrics import format_metrics_dataframe, display_metrics, get_metric_summary, compare_experiments
from .utils.batch_processing import batch_evaluate, prepare_test_data

__all__ = [
    # Version
    "__version__",
    "__author__",

    # Evaluators
    "BasicRAGEvaluator",
    "ToolCallingEvaluator",
    "AdvancedRAGEvaluator",
    "BaseAgentEvaluator",

    # Configuration
    "WatsonxConfig",
    "EvaluationConfig",
    "VectorStoreConfig",
    "LLMConfig",

    # Auth utilities
    "setup_environment",
    "get_api_credentials",

    # Vector store utilities
    "create_vector_store",
    "create_retriever",
    "load_documents_from_url",

    # Metrics utilities
    "format_metrics_dataframe",
    "display_metrics",
    "get_metric_summary",
    "compare_experiments",

    # Batch processing
    "batch_evaluate",
    "prepare_test_data",
]
