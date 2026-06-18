"""
LangGraph State Schema — Typed state that flows through the RAG pipeline.
"""

from typing import TypedDict


class RAGState(TypedDict):
    """
    State schema for the LangGraph RAG pipeline.
    Each node reads from and writes to this state.
    """

    # --- Input ---
    query: str  # User's original question

    # --- Retrieval ---
    bm25_results: list[dict]  # Results from BM25 retrieval
    vector_results: list[dict]  # Results from vector retrieval
    hybrid_results: list[dict]  # Fused hybrid search results
    reranked_results: list[dict]  # Top-k after cross-encoder re-ranking

    # --- Generation ---
    context_text: str  # Formatted context for the LLM
    response: str  # LLM-generated response
    citations: list[dict]  # Extracted citations
    citation_validation: dict  # Validation results for response citations

    # --- Metadata ---
    error: str  # Error message if any step fails
    latency: dict  # Per-node latency tracking
    faithfulness_score: float  # Real-time faithfulness evaluation score
    relevancy_score: float  # Real-time relevancy evaluation score

    # --- User Update Plan Additions ---
    response_mode: str  # 'legal', 'simple', or 'normal'
    user_id: int  # ID of the querying user (for permission filters)
    is_admin: bool  # Whether the user is an admin
    follow_up_questions: list[str]  # List of related follow-up questions
