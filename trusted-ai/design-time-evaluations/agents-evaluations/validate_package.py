"""
Validation script for wx_gov_agent_eval package.

Tests package structure, syntax, and basic functionality without requiring
full watsonx dependencies.
"""

import ast
import sys
from pathlib import Path

def validate_syntax(file_path):
    """Validate Python syntax using AST parsing."""
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)

def check_imports(file_path):
    """Check what modules are imported."""
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        tree = ast.parse(code)

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return imports
    except Exception as e:
        return []

def check_classes(file_path):
    """Check classes defined in the file."""
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        tree = ast.parse(code)

        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)

        return classes
    except Exception as e:
        return []

def check_functions(file_path):
    """Check functions defined in the file."""
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        tree = ast.parse(code)

        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)

        return functions
    except Exception as e:
        return []

def main():
    print("=" * 80)
    print("wx_gov_agent_eval Package Validation")
    print("=" * 80)

    package_root = Path("wx_gov_agent_eval")

    if not package_root.exists():
        print(f"✗ Package directory not found: {package_root}")
        return 1

    # Files to test
    files_to_test = [
        "config.py",
        "base_evaluator.py",
        "basic_rag.py",
        "tool_calling.py",
        "advanced_rag.py",
        "__init__.py",
        "utils/__init__.py",
        "utils/auth.py",
        "utils/vector_store.py",
        "utils/metrics.py",
        "utils/batch_processing.py",
    ]

    all_passed = True

    print("\n1. SYNTAX VALIDATION")
    print("-" * 80)
    for file_name in files_to_test:
        file_path = package_root / file_name
        if file_path.exists():
            valid, error = validate_syntax(file_path)
            if valid:
                print(f"✓ {file_name:<40} Valid syntax")
            else:
                print(f"✗ {file_name:<40} Syntax error: {error}")
                all_passed = False
        else:
            print(f"✗ {file_name:<40} File not found")
            all_passed = False

    print("\n2. MODULE STRUCTURE")
    print("-" * 80)

    # Check config.py
    config_classes = check_classes(package_root / "config.py")
    expected_configs = ["WatsonxConfig", "EvaluationConfig", "VectorStoreConfig", "LLMConfig"]
    if all(c in config_classes for c in expected_configs):
        print(f"✓ config.py has all expected classes: {', '.join(expected_configs)}")
    else:
        print(f"✗ config.py missing classes. Found: {config_classes}")
        all_passed = False

    # Check evaluators
    evaluators = {
        "basic_rag.py": "BasicRAGEvaluator",
        "tool_calling.py": "ToolCallingEvaluator",
        "advanced_rag.py": "AdvancedRAGEvaluator",
        "base_evaluator.py": "BaseAgentEvaluator"
    }

    for file_name, expected_class in evaluators.items():
        classes = check_classes(package_root / file_name)
        if expected_class in classes:
            print(f"✓ {file_name:<40} Has {expected_class}")
        else:
            print(f"✗ {file_name:<40} Missing {expected_class}")
            all_passed = False

    # Check utility functions
    print("\n3. UTILITY FUNCTIONS")
    print("-" * 80)

    utils_checks = {
        "utils/auth.py": ["setup_environment", "get_api_credentials"],
        "utils/vector_store.py": ["create_vector_store", "create_retriever"],
        "utils/metrics.py": ["format_metrics_dataframe", "display_metrics"],
        "utils/batch_processing.py": ["batch_evaluate", "prepare_test_data"]
    }

    for file_name, expected_funcs in utils_checks.items():
        funcs = check_functions(package_root / file_name)
        missing = [f for f in expected_funcs if f not in funcs]
        if not missing:
            print(f"✓ {file_name:<40} All functions present")
        else:
            print(f"✗ {file_name:<40} Missing: {', '.join(missing)}")
            all_passed = False

    # Check package exports
    print("\n4. PACKAGE EXPORTS")
    print("-" * 80)

    init_file = package_root / "__init__.py"
    if init_file.exists():
        with open(init_file, 'r') as f:
            init_content = f.read()

        expected_exports = [
            "BasicRAGEvaluator",
            "ToolCallingEvaluator",
            "AdvancedRAGEvaluator",
            "WatsonxConfig",
            "EvaluationConfig",
            "create_vector_store",
            "batch_evaluate"
        ]

        missing_exports = [e for e in expected_exports if e not in init_content]
        if not missing_exports:
            print(f"✓ __init__.py exports all expected classes/functions")
        else:
            print(f"✗ __init__.py missing exports: {', '.join(missing_exports)}")
            all_passed = False

    # Check supporting files
    print("\n5. SUPPORTING FILES")
    print("-" * 80)

    supporting_files = [
        "example_usage.py",
        "requirements.txt",
        "setup.py",
        ".gitignore",
        "wx_gov_agent_eval_README.md"
    ]

    for file_name in supporting_files:
        file_path = Path(file_name)
        if file_path.exists():
            if file_name.endswith('.py'):
                valid, error = validate_syntax(file_path)
                if valid:
                    print(f"✓ {file_name:<40} Exists and has valid syntax")
                else:
                    print(f"✗ {file_name:<40} Syntax error: {error}")
                    all_passed = False
            else:
                print(f"✓ {file_name:<40} Exists")
        else:
            print(f"✗ {file_name:<40} Not found")
            all_passed = False

    # Summary
    print("\n" + "=" * 80)
    if all_passed:
        print("✓ ALL VALIDATION CHECKS PASSED")
        print("\nNote: Full integration testing requires:")
        print("  - IBM watsonx.ai credentials (WATSONX_APIKEY, WATSONX_PROJECT_ID)")
        print("  - Installation of all dependencies from requirements.txt")
        print("  - For full testing: pip install ibm-watsonx-ai ibm-watsonx-gov langchain-ibm")
        return 0
    else:
        print("✗ SOME VALIDATION CHECKS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
