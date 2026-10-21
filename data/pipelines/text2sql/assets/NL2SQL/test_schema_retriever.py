#!/usr/bin/env python3
"""
test_schema_retriever.py — semantic search evaluation script
"""

import os
import sys
import json
from dotenv import load_dotenv

# Ensure we can import from backend/schema_retriever and embedding
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "schema_retriever"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "embedding"))

import schema_retriever_pgvector as sr

def run_retrieval_test(user_query: str, top_k: int = 3):
    print(f"\nEvaluating user query: '{user_query}'")
    print("-" * 60)
    
    # Mock the request
    req = sr.Req(user_query=user_query, top_k=top_k)
    response = sr.retrieve_schema(req)
    
    print(f"Retrieval served in {response['took_ms']} ms. Found {len(response['results'])} matches.")
    
    for i, res in enumerate(response['results'], 1):
        print(f"\n  [{i}] Table: {res['table_id']} (Confidence: {res['confidence']:.4f})")
        print(f"      Columns: {', '.join([c['name'] for c in res['columns'][:5]])} ... ({len(res['columns'])} total)")
        print(f"      Primary Key: {res['pk']}")
        print(f"      Foreign Keys: {res['fk']}")
        if res['sample_rows']:
            print(f"      Sample Row (first): {json.dumps(res['sample_rows'][0])[:120]}...")
        else:
            print(f"      Sample Rows: None")
        print(f"      Example SQL Sketch: {res['sketches'][0]['sql'] if res['sketches'] else 'None'}")
        
    return response['results']

def main():
    # Load .env
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "schema_retriever", ".env")
    load_dotenv(dotenv_path=env_path)
    
    print("Initialising Schema Retriever (pgvector)...")
    sr.initialize_and_validate_env()
    sr.CFG = sr.load_config()
    sr.EMBEDDER = sr.get_embedder(sr.CFG)
    
    test_questions = [
        "Find all customers and their basic info",
        "List all milestones and tasks for our projects",
        "Get all purchase order header and detail relations",
        "List all part numbers and descriptions"
    ]
    
    all_results = {}
    for q in test_questions:
        all_results[q] = run_retrieval_test(q)
        
if __name__ == "__main__":
    main()
