"""
IBM watsonx.governance Prompt Template Evaluation Package

A production-ready Python package for evaluating prompt template assets in IBM watsonx.governance.
Supports both SLM (Small Language Model) and LLM-as-Judge evaluation approaches.

Main Classes:
    - PromptTemplateEvaluator: Main evaluator for prompt template assets
    - EvaluatorConfig: Configuration for evaluation settings
    - WatsonxConfig: Configuration for IBM watsonx credentials
"""

from wx_gov_prompt_eval.config import (
    WatsonxConfig,
    EvaluatorConfig,
    MonitorConfig
)
from wx_gov_prompt_eval.prompt_evaluator import PromptTemplateEvaluator

__version__ = "0.1.0"

__all__ = [
    "PromptTemplateEvaluator",
    "WatsonxConfig",
    "EvaluatorConfig",
    "MonitorConfig",
]
