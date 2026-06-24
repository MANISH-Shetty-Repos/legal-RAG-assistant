"""
Test Query Script — Run a query through the retrieval pipeline to test BM25, Vector Search, and Re-ranking.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.orchestration.graph import RAGPipeline


def main():
    print("Initializing RAG Pipeline...")
    pipeline = RAGPipeline()

    query = "What is the fee for filing an RTI application?"
    print(f"\nQuery: '{query}'")

    # 1. Test hybrid search
    print("\n--- Testing Hybrid Search ---")
    hybrid_res = pipeline.hybrid_searcher.search(query, top_k=5)
    for idx, doc in enumerate(hybrid_res, 1):
        print(f"[{idx}] Score: {doc['score']:.4f} | Source: {doc['metadata']['filename']} | Page: {doc['metadata']['page_number']}")
        print(f"    Text: {doc['text'][:150]}...")

    # 2. Test re-ranking
    print("\n--- Testing Cross-Encoder Re-ranking ---")
    from src.retrieval.reranker import rerank
    reranked_res = rerank(query, hybrid_res, top_k=3)
    for idx, doc in enumerate(reranked_res, 1):
        print(f"[{idx}] Re-rank Score: {doc['rerank_score']:.4f} | Source: {doc['metadata']['filename']} | Page: {doc['metadata']['page_number']}")
        print(f"    Text: {doc['text'][:150]}...")


if __name__ == "__main__":
    main()
