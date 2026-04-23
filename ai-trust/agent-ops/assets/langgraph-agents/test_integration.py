"""
Integration test for wx_gov_agent_eval package.

Run this script with your existing Python environment that has the dependencies installed.
Make sure .env file is present with WATSONX credentials.
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded .env file")
except ImportError:
    print("⚠ python-dotenv not installed, using existing environment variables")

# Add package to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all package imports work."""
    print("\n" + "=" * 70)
    print("TEST 1: Package Imports")
    print("=" * 70)

    try:
        from wx_gov_agent_eval import (
            BasicRAGEvaluator,
            ToolCallingEvaluator,
            AdvancedRAGEvaluator,
            WatsonxConfig,
            EvaluationConfig,
            VectorStoreConfig,
            LLMConfig,
            create_vector_store,
            batch_evaluate,
            prepare_test_data
        )
        print("✓ All package imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test configuration classes."""
    print("\n" + "=" * 70)
    print("TEST 2: Configuration Classes")
    print("=" * 70)

    try:
        from wx_gov_agent_eval import WatsonxConfig, EvaluationConfig, VectorStoreConfig, LLMConfig

        # Test WatsonxConfig.from_env()
        config = WatsonxConfig.from_env()
        print(f"✓ WatsonxConfig.from_env() works")
        print(f"  - Project ID: {config.project_id[:20]}...")
        print(f"  - URL: {config.url}")

        # Test EvaluationConfig
        eval_config = EvaluationConfig(batch_size=5, compute_real_time=True)
        print(f"✓ EvaluationConfig works")
        print(f"  - Batch size: {eval_config.batch_size}")
        print(f"  - Real-time: {eval_config.compute_real_time}")

        # Test VectorStoreConfig
        vector_config = VectorStoreConfig(chunk_size=300, top_k=5)
        print(f"✓ VectorStoreConfig works")
        print(f"  - Chunk size: {vector_config.chunk_size}")
        print(f"  - Top K: {vector_config.top_k}")

        # Test LLMConfig
        llm_config = LLMConfig(max_new_tokens=200)
        print(f"✓ LLMConfig works")
        print(f"  - Model: {llm_config.model_id}")
        print(f"  - Max tokens: {llm_config.max_new_tokens}")

        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_rag_evaluator():
    """Test BasicRAGEvaluator with minimal example."""
    print("\n" + "=" * 70)
    print("TEST 3: BasicRAGEvaluator")
    print("=" * 70)

    try:
        from wx_gov_agent_eval import BasicRAGEvaluator, EvaluationConfig

        # Create simple test documents
        documents = [
            {
                "id": "1",
                "document": "Python is a high-level programming language known for its simplicity and readability."
            },
            {
                "id": "2",
                "document": "Machine learning is a subset of artificial intelligence that enables systems to learn from data."
            }
        ]

        print("Creating BasicRAGEvaluator...")
        eval_config = EvaluationConfig(
            compute_real_time=False,  # Faster for testing
            enable_tracing=False       # Skip tracing for quick test
        )
        evaluator = BasicRAGEvaluator(eval_config=eval_config)
        print("✓ BasicRAGEvaluator instantiated")

        print("Building agent with test documents...")
        evaluator.build_agent(documents=documents)
        print("✓ Agent built successfully")

        print("Running single evaluation...")
        result = evaluator.evaluate_single(
            input_text="What is Python?",
            ground_truth="Python is a programming language known for simplicity.",
            interaction_id="test-1"
        )
        print("✓ Evaluation completed")
        print(f"  - Generated text: {result.get('generated_text', 'N/A')[:100]}...")

        return True
    except Exception as e:
        print(f"✗ BasicRAGEvaluator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_processing():
    """Test batch evaluation utilities."""
    print("\n" + "=" * 70)
    print("TEST 4: Batch Processing")
    print("=" * 70)

    try:
        from wx_gov_agent_eval import prepare_test_data

        # Prepare test data
        test_df = prepare_test_data(
            input_texts=["Question 1", "Question 2", "Question 3"],
            ground_truths=["Answer 1", "Answer 2", "Answer 3"]
        )

        print("✓ prepare_test_data works")
        print(f"  - Created DataFrame with {len(test_df)} rows")
        print(f"  - Columns: {list(test_df.columns)}")

        return True
    except Exception as e:
        print(f"✗ Batch processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_calling_evaluator():
    """Test ToolCallingEvaluator initialization."""
    print("\n" + "=" * 70)
    print("TEST 5: ToolCallingEvaluator (initialization only)")
    print("=" * 70)

    try:
        from wx_gov_agent_eval import ToolCallingEvaluator, EvaluationConfig
        from langchain_core.tools import tool

        # Define a simple test tool
        @tool
        def test_calculator(expression: str) -> str:
            """Calculate a simple expression."""
            try:
                return str(eval(expression))
            except:
                return "Error in calculation"

        print("Creating ToolCallingEvaluator...")
        eval_config = EvaluationConfig(
            compute_real_time=False,
            enable_tracing=False
        )
        evaluator = ToolCallingEvaluator(eval_config=eval_config)
        print("✓ ToolCallingEvaluator instantiated")

        print("Building agent with test tool...")
        evaluator.build_agent(tools=[test_calculator])
        print("✓ Agent built successfully with tools")

        return True
    except Exception as e:
        print(f"✗ ToolCallingEvaluator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all integration tests."""
    print("=" * 70)
    print("wx_gov_agent_eval - Integration Tests")
    print("=" * 70)

    # Check environment variables
    apikey = os.getenv("WATSONX_APIKEY")
    project_id = os.getenv("WXG_PROJECT_ID") or os.getenv("WATSONX_PROJECT_ID")

    if not apikey or not project_id:
        print("\n⚠ WARNING: WATSONX credentials not found in environment")
        print("Make sure .env file exists with:")
        print("  - WATSONX_APIKEY")
        print("  - WXG_PROJECT_ID (or WATSONX_PROJECT_ID)")
        return 1

    print(f"\n✓ Found credentials:")
    print(f"  - API Key: {apikey[:20]}...")
    print(f"  - Project ID: {project_id[:20]}...")

    # Run tests
    results = []

    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Batch Processing", test_batch_processing()))
    results.append(("ToolCallingEvaluator", test_tool_calling_evaluator()))
    results.append(("BasicRAGEvaluator", test_basic_rag_evaluator()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:<30} {status}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests PASSED! Package is working correctly.")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
