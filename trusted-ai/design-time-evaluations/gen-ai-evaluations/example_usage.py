"""
Example usage of wx_gov_prompt_eval package.

This script demonstrates how to use the PromptTemplateEvaluator to create,
configure, and evaluate prompt template assets in IBM watsonx.governance.
"""

import os
from dotenv import load_dotenv

from wx_gov_prompt_eval import (
    PromptTemplateEvaluator,
    WatsonxConfig,
    EvaluatorConfig,
    MonitorConfig
)

# Load environment variables from .env file
load_dotenv()


def example_slm_evaluation():
    """
    Example: Evaluate prompt template using SLM (built-in models).

    This approach uses OpenScale's built-in smaller models for evaluation
    metrics like faithfulness and answer relevance.
    """
    print("\n" + "=" * 80)
    print("Example 1: SLM (Built-in Models) Evaluation")
    print("=" * 80 + "\n")

    # Step 1: Configure watsonx credentials
    watsonx_config = WatsonxConfig(
        wos_url=os.getenv("WOS_URL"),
        wos_username=os.getenv("WOS_USERNAME"),
        wos_password=os.getenv("WOS_PASSWORD"),
        wml_url=os.getenv("WML_URL"),
        wml_username=os.getenv("WML_USERNAME"),
        wml_password=os.getenv("WML_PASSWORD")
    )

    # Step 2: Configure for SLM evaluation
    evaluator_config = EvaluatorConfig(
        evaluator_type="slm"  # Use built-in models
    )

    # Step 3: Configure monitors
    monitor_config = MonitorConfig(
        faithfulness_enabled=True,
        faithfulness_attributions_count=3,  # SLM-specific parameter
        faithfulness_ngrams=2,  # SLM-specific parameter
        answer_relevance_enabled=True,
        rouge_score_enabled=True,
        context_relevance_enabled=True,
        context_relevance_ngrams=2,  # SLM-specific parameter
        retrieval_quality_enabled=True
    )

    # Step 4: Create evaluator
    evaluator = PromptTemplateEvaluator(
        watsonx_config=watsonx_config,
        evaluator_config=evaluator_config,
        monitor_config=monitor_config,
        project_id=os.getenv("PROJECT_ID")
    )

    # Step 5: Create prompt template
    prompt_text = """
Answer the question using below context.
{retrieved_contexts}

Question: {user_input}
"""

    prompt_id = evaluator.create_prompt_template(
        name="RAG Q&A Prompt (SLM Evaluation)",
        prompt_text=prompt_text,
        prompt_variables={"retrieved_contexts": "", "user_input": ""},
        model_id="ibm/granite-3-8b-instruct",
        description="RAG prompt template evaluated with SLM"
    )

    # Step 6: Setup monitoring
    subscription_id = evaluator.setup_monitoring(
        context_fields=["retrieved_contexts"],
        question_field="user_input",
        label_column="ground_truths"
    )

    # Step 7: Evaluate with test data
    results = evaluator.evaluate(
        test_data_path="test_data.csv"  # Your test data file
    )

    # Step 8: Display metrics
    evaluator.display_metrics(monitor_type="generative_ai_quality")

    # Step 9: Get record-level metrics
    metrics_df = evaluator.get_record_level_metrics()
    print("\nRecord-level metrics:")
    print(metrics_df.head())

    # Step 10: Plot metrics
    evaluator.plot_metrics(
        metric_columns=["faithfulness", "answer_relevance", "rouge_score"]
    )

    # Step 11: Get factsheets URL
    factsheets_url = evaluator.get_factsheets_url()
    print(f"\nView factsheets at: {factsheets_url}")

    return evaluator


def example_llm_as_judge_evaluation():
    """
    Example: Evaluate prompt template using LLM-as-Judge.

    This approach uses an external LLM (e.g., Llama 3.1) to judge the quality
    of generated responses. Provides more sophisticated evaluation but requires
    more compute resources.
    """
    print("\n" + "=" * 80)
    print("Example 2: LLM-as-Judge Evaluation")
    print("=" * 80 + "\n")

    # Step 1: Configure watsonx credentials
    watsonx_config = WatsonxConfig(
        wos_url=os.getenv("WOS_URL"),
        wos_username=os.getenv("WOS_USERNAME"),
        wos_password=os.getenv("WOS_PASSWORD"),
        wml_url=os.getenv("WML_URL"),
        wml_username=os.getenv("WML_USERNAME"),
        wml_password=os.getenv("WML_PASSWORD")
    )

    # Step 2: Configure for LLM-as-Judge evaluation
    evaluator_config = EvaluatorConfig(
        evaluator_type="llm",  # Use LLM as judge
        model_id="meta-llama/llama-3-1-8b-instruct",
        evaluator_name="Llama 3.1 Judge",
        evaluator_description="Evaluation using Llama 3.1 8B Instruct as judge"
    )

    # Step 3: Configure monitors
    monitor_config = MonitorConfig(
        faithfulness_enabled=True,
        # Note: attributions_count and ngrams are not used for LLM-as-judge
        answer_relevance_enabled=True,
        answer_similarity_enabled=True,  # Only available with LLM-as-judge
        rouge_score_enabled=True,
        context_relevance_enabled=True,
        retrieval_quality_enabled=True
    )

    # Step 4: Create evaluator (this will create the LLM evaluator)
    evaluator = PromptTemplateEvaluator(
        watsonx_config=watsonx_config,
        evaluator_config=evaluator_config,
        monitor_config=monitor_config,
        project_id=os.getenv("PROJECT_ID")
    )

    # Step 5: Create prompt template
    prompt_text = """
Answer the question using below context.
{retrieved_contexts}

Question: {user_input}
"""

    prompt_id = evaluator.create_prompt_template(
        name="RAG Q&A Prompt (LLM Judge)",
        prompt_text=prompt_text,
        prompt_variables={"retrieved_contexts": "", "user_input": ""},
        model_id="ibm/granite-3-8b-instruct",
        description="RAG prompt template evaluated with LLM-as-judge"
    )

    # Step 6: Setup monitoring
    subscription_id = evaluator.setup_monitoring(
        context_fields=["retrieved_contexts"],
        question_field="user_input",
        label_column="ground_truths"
    )

    # Step 7: Evaluate with test data
    results = evaluator.evaluate(
        test_data_path="test_data.csv"  # Your test data file
    )

    # Step 8: Display metrics
    evaluator.display_metrics(monitor_type="generative_ai_quality")

    # Step 9: Get record-level metrics
    metrics_df = evaluator.get_record_level_metrics()
    print("\nRecord-level metrics:")
    print(metrics_df.head())

    # Step 10: Plot metrics (including answer_similarity which is LLM-only)
    evaluator.plot_metrics(
        metric_columns=["faithfulness", "answer_relevance", "answer_similarity"]
    )

    # Step 11: Get factsheets URL
    factsheets_url = evaluator.get_factsheets_url()
    print(f"\nView factsheets at: {factsheets_url}")

    return evaluator


def example_minimal_usage():
    """
    Example: Minimal usage with defaults.

    This shows the simplest way to use the package with default configurations.
    """
    print("\n" + "=" * 80)
    print("Example 3: Minimal Usage")
    print("=" * 80 + "\n")

    # Configure and create evaluator with defaults (SLM evaluation)
    watsonx_config = WatsonxConfig()  # Reads from environment variables
    evaluator = PromptTemplateEvaluator(
        watsonx_config=watsonx_config,
        project_id=os.getenv("PROJECT_ID")
    )

    # Create prompt
    prompt_id = evaluator.create_prompt_template(
        name="Simple RAG Prompt",
        prompt_text="Answer: {context}\n\nQuestion: {question}",
        prompt_variables={"context": "", "question": ""}
    )

    # Setup and evaluate
    evaluator.setup_monitoring(
        context_fields=["context"],
        question_field="question",
        label_column="ground_truth"
    )

    evaluator.evaluate("test_data.csv")
    evaluator.display_metrics()

    return evaluator


if __name__ == "__main__":
    # Check that required environment variables are set
    required_vars = [
        "WOS_URL", "WOS_USERNAME", "WOS_PASSWORD",
        "WML_URL", "WML_USERNAME", "WML_PASSWORD",
        "PROJECT_ID"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these in your .env file or environment.")
        exit(1)

    # Run examples
    print("=" * 80)
    print("IBM watsonx.governance Prompt Template Evaluation Examples")
    print("=" * 80)

    # Uncomment the example you want to run:

    # Example 1: SLM (built-in models) evaluation
    # evaluator = example_slm_evaluation()

    # Example 2: LLM-as-Judge evaluation
    # evaluator = example_llm_as_judge_evaluation()

    # Example 3: Minimal usage
    # evaluator = example_minimal_usage()

    print("\nTo run an example, uncomment one of the example function calls at the bottom of this file.")
