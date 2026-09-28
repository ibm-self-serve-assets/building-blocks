"""
Example usage of wx_gov_agent_eval package.

This file demonstrates how to use all three evaluators for different agent types:
1. BasicRAGEvaluator - for simple RAG agents
2. ToolCallingEvaluator - for agents with custom tools
3. AdvancedRAGEvaluator - for multi-source RAG agents

Prerequisites:
    - Set environment variables: WATSONX_APIKEY, WATSONX_PROJECT_ID
    - For web search: TAVILY_API_KEY
    - Install dependencies: pip install -r requirements.txt
"""

import pandas as pd
from wx_gov_agent_eval import (
    BasicRAGEvaluator,
    ToolCallingEvaluator,
    AdvancedRAGEvaluator,
    WatsonxConfig,
    EvaluationConfig,
    prepare_test_data,
)


# ==============================================================================
# Example 1: Basic RAG Evaluator
# ==============================================================================

def example_basic_rag():
    """Demonstrate BasicRAGEvaluator with local documents."""
    print("=" * 80)
    print("Example 1: Basic RAG Evaluator")
    print("=" * 80)

    # Sample documents
    documents = [
        {
            "id": "1",
            "document": "Artificial Intelligence (AI) is the simulation of human intelligence "
                       "by machines. AI systems can learn, reason, and self-correct."
        },
        {
            "id": "2",
            "document": "Machine Learning is a subset of AI that enables systems to learn "
                       "from data without explicit programming. It uses algorithms to "
                       "find patterns in data."
        },
        {
            "id": "3",
            "document": "Deep Learning is a subset of machine learning that uses neural "
                       "networks with multiple layers. It's particularly effective for "
                       "image and speech recognition."
        }
    ]

    # Initialize evaluator
    evaluator = BasicRAGEvaluator()

    # Build agent with documents
    print("\nBuilding Basic RAG agent...")
    evaluator.build_agent(documents=documents)

    # Single evaluation
    print("\nEvaluating single query...")
    result = evaluator.evaluate_single(
        input_text="What is Machine Learning?",
        ground_truth="Machine Learning is a subset of AI that learns from data without explicit programming.",
        interaction_id="example-1"
    )

    print(f"Generated answer: {result.get('generated_text', 'N/A')}")

    # Display metrics
    print("\nMetrics:")
    evaluator.display_results()

    # Get aggregated metrics
    print("\nAggregated metrics for Retrieval Node:")
    retrieval_metrics = evaluator.get_aggregated_metrics("Retrieval Node")
    print(retrieval_metrics)

    print("\nAggregated metrics for Generation Node:")
    generation_metrics = evaluator.get_aggregated_metrics("Generation Node")
    print(generation_metrics)


# ==============================================================================
# Example 2: Tool Calling Evaluator
# ==============================================================================

def example_tool_calling():
    """Demonstrate ToolCallingEvaluator with custom tools."""
    print("\n" + "=" * 80)
    print("Example 2: Tool Calling Evaluator")
    print("=" * 80)

    from langchain_core.tools import tool

    # Define custom tools
    @tool
    def get_exchange_rate(from_currency: str, to_currency: str) -> str:
        """Get the exchange rate between two currencies.

        Args:
            from_currency: Source currency code (e.g., USD).
            to_currency: Target currency code (e.g., EUR).

        Returns:
            Exchange rate information.
        """
        # Mock implementation
        rates = {
            ("USD", "EUR"): 0.85,
            ("USD", "GBP"): 0.73,
            ("EUR", "USD"): 1.18,
        }
        rate = rates.get((from_currency.upper(), to_currency.upper()), 1.0)
        return f"The exchange rate from {from_currency} to {to_currency} is {rate}"

    @tool
    def calculate_loan_risk(credit_score: int, loan_amount: float, income: float) -> str:
        """Calculate loan risk assessment.

        Args:
            credit_score: Credit score (300-850).
            loan_amount: Requested loan amount.
            income: Annual income.

        Returns:
            Risk assessment (Low, Medium, High).
        """
        # Mock implementation
        debt_to_income = loan_amount / income
        if credit_score > 700 and debt_to_income < 0.3:
            return "Low risk - Loan approved"
        elif credit_score > 600 and debt_to_income < 0.4:
            return "Medium risk - Conditional approval"
        else:
            return "High risk - Loan denied"

    # Initialize evaluator
    evaluator = ToolCallingEvaluator()

    # Build agent with tools
    print("\nBuilding Tool Calling agent...")
    evaluator.build_agent(tools=[get_exchange_rate, calculate_loan_risk])

    # Single evaluation
    print("\nEvaluating single query...")
    result = evaluator.evaluate_single(
        input_text="What is the exchange rate from USD to EUR?",
        ground_truth="The exchange rate from USD to EUR is approximately 0.85",
        interaction_id="example-2"
    )

    print(f"Generated answer: {result.get('generated_text', 'N/A')}")

    # Display metrics
    print("\nMetrics:")
    evaluator.display_results()


# ==============================================================================
# Example 3: Advanced RAG Evaluator
# ==============================================================================

def example_advanced_rag():
    """Demonstrate AdvancedRAGEvaluator with multi-source retrieval."""
    print("\n" + "=" * 80)
    print("Example 3: Advanced RAG Evaluator")
    print("=" * 80)

    # Sample documents
    documents = [
        {
            "id": "1",
            "document": "Our company was founded in 2010 and specializes in cloud computing solutions."
        },
        {
            "id": "2",
            "document": "We offer three main products: Cloud Storage, Cloud Compute, and Cloud AI."
        },
        {
            "id": "3",
            "document": "Our customer support is available 24/7 via phone, email, and chat."
        }
    ]

    # Initialize evaluator
    # Note: Set enable_web_search=False if you don't have TAVILY_API_KEY
    evaluator = AdvancedRAGEvaluator()

    # Build agent
    print("\nBuilding Advanced RAG agent...")
    evaluator.build_agent(
        documents=documents,
        enable_web_search=False  # Set to True if you have Tavily API key
    )

    # Single evaluation - local document query
    print("\nEvaluating local query...")
    result1 = evaluator.evaluate_single(
        input_text="What products does the company offer?",
        ground_truth="The company offers Cloud Storage, Cloud Compute, and Cloud AI.",
        interaction_id="example-3a"
    )

    print(f"Generated answer: {result1.get('generated_text', 'N/A')}")

    # Display metrics
    print("\nMetrics:")
    evaluator.display_results()


# ==============================================================================
# Example 4: Batch Evaluation
# ==============================================================================

def example_batch_evaluation():
    """Demonstrate batch evaluation with test dataset."""
    print("\n" + "=" * 80)
    print("Example 4: Batch Evaluation")
    print("=" * 80)

    # Sample documents
    documents = [
        {
            "id": "1",
            "document": "Python is a high-level programming language known for its simplicity and readability."
        },
        {
            "id": "2",
            "document": "Java is an object-oriented programming language designed for platform independence."
        },
        {
            "id": "3",
            "document": "JavaScript is primarily used for web development and runs in browsers."
        }
    ]

    # Prepare test data
    test_questions = [
        "What is Python known for?",
        "What type of language is Java?",
        "Where does JavaScript run?"
    ]

    test_answers = [
        "Python is known for its simplicity and readability.",
        "Java is an object-oriented programming language.",
        "JavaScript runs in web browsers."
    ]

    test_df = prepare_test_data(
        input_texts=test_questions,
        ground_truths=test_answers
    )

    # Initialize evaluator
    evaluator = BasicRAGEvaluator()

    # Build agent
    print("\nBuilding agent...")
    evaluator.build_agent(documents=documents)

    # Batch evaluation
    print(f"\nEvaluating {len(test_df)} test cases...")
    results = evaluator.evaluate_batch(
        test_data=test_df,
        batch_size=5,
        parallel=False  # Set to True for parallel processing
    )

    print(f"Completed {len(results)} evaluations")

    # Get results as DataFrame
    print("\nMetrics DataFrame:")
    metrics_df = evaluator.get_metrics_dataframe()
    print(metrics_df.head())

    # Display summary
    print("\nMetrics Summary:")
    evaluator.display_results()


# ==============================================================================
# Example 5: Experiment Tracking
# ==============================================================================

def example_experiment_tracking():
    """Demonstrate experiment tracking in watsonx.governance."""
    print("\n" + "=" * 80)
    print("Example 5: Experiment Tracking")
    print("=" * 80)

    # Sample documents
    documents = [
        {"id": "1", "document": "AI is transforming various industries including healthcare and finance."}
    ]

    # Initialize evaluator with custom config
    eval_config = EvaluationConfig(
        compute_real_time=True,
        enable_tracing=True
    )

    evaluator = BasicRAGEvaluator(eval_config=eval_config)

    # Track experiment
    print("\nStarting experiment tracking...")
    experiment_id = evaluator.track_experiment(
        experiment_name="RAG Evaluation Experiment",
        use_existing=False
    )
    print(f"Experiment ID: {experiment_id}")

    # Build and evaluate
    evaluator.build_agent(documents=documents)

    result = evaluator.evaluate_single(
        input_text="How is AI being used?",
        ground_truth="AI is being used in healthcare and finance industries.",
        interaction_id="exp-1"
    )

    print(f"Generated answer: {result.get('generated_text', 'N/A')}")

    # Results are automatically tracked in watsonx.governance
    print("\nResults have been logged to watsonx.governance")
    evaluator.display_results()


# ==============================================================================
# Main
# ==============================================================================

def main():
    """Run all examples."""
    print("wx_gov_agent_eval - Usage Examples")
    print("===================================\n")

    try:
        # Run examples
        example_basic_rag()
        # example_tool_calling()  # Uncomment to run
        # example_advanced_rag()  # Uncomment to run
        # example_batch_evaluation()  # Uncomment to run
        # example_experiment_tracking()  # Uncomment to run

        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\nError running examples: {e}")
        print("\nMake sure you have:")
        print("1. Set WATSONX_APIKEY and WATSONX_PROJECT_ID environment variables")
        print("2. Installed all required dependencies: pip install -r requirements.txt")
        print("3. For web search examples: Set TAVILY_API_KEY environment variable")


if __name__ == "__main__":
    main()
