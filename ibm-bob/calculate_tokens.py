#!/usr/bin/env python3
"""
Calculate token counts for text files using tiktoken (OpenAI's tokenizer).
This provides accurate token counts from an LLM perspective.
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
    parser = argparse.ArgumentParser()
    parser.add_argument('target_dir', type=str)
    args = parser.parse_args()
    
    dir_path = Path(args.target_dir)
    if not dir_path.exists():
        print(f"Directory not found: {args.target_dir}")
        return

    token_count = count_tokens_in_directory(args.target_dir)
    
    print(f"{token_count} across all files in {args.target_dir}")

if __name__ == "__main__":
    main()
