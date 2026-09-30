"""
Batch processing utilities for high-performance evaluation.

This module provides efficient batch evaluation capabilities for agent testing.
"""

import pandas as pd
from typing import List, Dict, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings


def batch_evaluate(
    agent,
    test_data: pd.DataFrame,
    evaluator,
    batch_size: int = 10,
    parallel: bool = False,
    max_workers: int = 4
) -> List[Dict[str, Any]]:
    """Evaluate agent on a batch of test data with performance optimization.

    Args:
        agent: LangGraph agent to evaluate.
        test_data: DataFrame with test data (must include required fields).
        evaluator: AgenticEvaluator instance.
        batch_size: Number of records to process in each batch.
        parallel: Whether to use parallel processing (experimental).
        max_workers: Maximum number of parallel workers if parallel=True.

    Returns:
        List of evaluation results.

    Example:
        ```python
        results = batch_evaluate(
            agent=my_agent,
            test_data=test_df,
            evaluator=evaluator,
            batch_size=10
        )
        ```
    """
    warnings.filterwarnings('ignore')

    # Convert to records
    records = test_data.to_dict("records")

    if parallel:
        return _batch_evaluate_parallel(
            agent, records, evaluator, batch_size, max_workers
        )
    else:
        return _batch_evaluate_sequential(
            agent, records, evaluator, batch_size
        )


def _batch_evaluate_sequential(
    agent,
    records: List[Dict],
    evaluator,
    batch_size: int
) -> List[Dict[str, Any]]:
    """Sequential batch evaluation."""
    results = []

    # Process in batches
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        batch_results = agent.batch(inputs=batch)
        results.extend(batch_results)

    return results


def _batch_evaluate_parallel(
    agent,
    records: List[Dict],
    evaluator,
    batch_size: int,
    max_workers: int
) -> List[Dict[str, Any]]:
    """Parallel batch evaluation (experimental).

    Note: This may not work with all agent types due to state management.
    """
    results = []

    def process_batch(batch):
        return agent.batch(inputs=batch)

    # Create batches
    batches = [
        records[i:i + batch_size]
        for i in range(0, len(records), batch_size)
    ]

    # Process batches in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_batch, batch): i
            for i, batch in enumerate(batches)
        }

        for future in as_completed(futures):
            batch_results = future.result()
            results.extend(batch_results)

    return results


def prepare_test_data(
    input_texts: List[str],
    ground_truths: Optional[List[str]] = None,
    interaction_ids: Optional[List[str]] = None
) -> pd.DataFrame:
    """Prepare test data in the correct format for evaluation.

    Args:
        input_texts: List of input questions/queries.
        ground_truths: Optional list of ground truth answers.
        interaction_ids: Optional list of interaction IDs (auto-generated if not provided).

    Returns:
        DataFrame ready for batch evaluation.

    Example:
        ```python
        test_df = prepare_test_data(
            input_texts=["What is AI?", "Explain ML"],
            ground_truths=["AI is...", "ML is..."]
        )
        ```
    """
    data = {"input_text": input_texts}

    if ground_truths:
        data["ground_truth"] = ground_truths

    if interaction_ids:
        data["interaction_id"] = interaction_ids
    else:
        data["interaction_id"] = [str(i) for i in range(len(input_texts))]

    return pd.DataFrame(data)
