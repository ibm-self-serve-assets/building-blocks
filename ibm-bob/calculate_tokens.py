#!/usr/bin/env python3
"""
Calculate token counts for text files using tiktoken (OpenAI's tokenizer).
This provides accurate token counts from an LLM perspective.

USAGE:
    # Count tokens in a single file
    python count_token.py /path/to/file.txt

    # Count tokens in all files within a directory (recursive)
    python count_token.py /path/to/directory

    # Examples:
    python count_token.py README.md
    python count_token.py ./my_project
    python count_token.py /Users/username/documents/report.txt

REQUIREMENTS:
    - Python 3.6+
    - tiktoken library (auto-installed if missing)

OUTPUT:
    Displays total token count for the specified file or all files in directory.
    Uses GPT-4 tokenizer for accurate LLM token counting.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import tiktoken
except ImportError:
    print("Installing tiktoken...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tiktoken"])
    import tiktoken

def count_tokens_in_file(file_path: str) -> int:
    """
    Count tokens in a single file using GPT-4 tokenizer.

    Args:
        file_path: Path to the file to analyze

    Returns:
        Number of tokens in the file, or 0 if error occurs
    """
    try:
        if (".DS_Store" in file_path):
            return 0
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            encoding = tiktoken.encoding_for_model("gpt-4")
            tokens = encoding.encode(content)
            token_count = len(tokens)
            return token_count
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0


def count_tokens_in_directory(directory: str) -> int:
    """
    Recursively count tokens in all files within a directory.

    Args:
        directory: Path to the directory to analyze

    Returns:
        Total number of tokens across all files
    """
    total_token_count = 0
    for root, dirs, files in os.walk(Path(directory)):
        for file in files:
            file_path = os.path.join(root, file)
            total_token_count += count_tokens_in_file(file_path)

        for dir in dirs:
            dir_path = os.path.join(root, dir)
            total_token_count += count_tokens_in_file(dir_path)

    return total_token_count

def main():
    """
    Main entry point for the token counter script.
    Handles both file and directory paths.
    """
    parser = argparse.ArgumentParser(
        description='Count tokens in a file or directory using GPT-4 tokenizer'
    )
    parser.add_argument(
        'target_path',
        type=str,
        help='Path to a file or directory to analyze'
    )
    args = parser.parse_args()

    target_path = Path(args.target_path)

    # Check if path exists
    if not target_path.exists():
        print(f"Error: Path not found: {args.target_path}")
        sys.exit(1)

    # Handle file vs directory
    if target_path.is_file():
        token_count = count_tokens_in_file(str(target_path))
        print(f"{token_count} tokens in file: {args.target_path}")
    elif target_path.is_dir():
        token_count = count_tokens_in_directory(str(target_path))
        print(f"{token_count} tokens across all files in directory: {args.target_path}")
    else:
        print(f"Error: {args.target_path} is neither a file nor a directory")
        sys.exit(1)

if __name__ == "__main__":
    main()
