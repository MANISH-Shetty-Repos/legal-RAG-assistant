"""
Cross-Encoder Re-Ranker — BAAI/bge-reranker-base
Re-ranks retrieved chunks by relevance to the query.
"""

from loguru import logger
from sentence_transformers import CrossEncoder

from src.config import get_config


_reranker: CrossEncoder | None = None


def get_reranker() -> CrossEncoder:
    """Get or create the singleton cross-encoder re-ranker."""
    global _reranker

    if _reranker is None:
        config = get_config()
        model_name = config.reranker.model_name

        logger.info(f"Loading re-ranker model: {model_name}")
        _reranker = CrossEncoder(model_name, max_length=512)
        logger.info(f"Re-ranker model loaded: {model_name}")

    return _reranker


def rerank(
    query: str,
    documents: list[dict],
    top_k: int | None = None,
) -> list[dict]:
    """
    Re-rank documents using the cross-encoder model.

    Takes the hybrid search results and re-scores each document
    against the query using a cross-encoder, then returns the top-k
    most relevant results.

    Args:
        query: The user's query
        documents: List of dicts from hybrid search (must have 'text' key)
        top_k: Number of top results to return

    Returns:
        Re-ranked list of dicts, sorted by relevance score (descending)
    """
    if not documents:
        return []

    config = get_config()
    k = top_k or config.retrieval.rerank_top_k

    reranker = get_reranker()

    # Create query-document pairs for the cross-encoder
    pairs = [[query, doc["text"]] for doc in documents]

    # Score all pairs
    scores = reranker.predict(pairs)

    # Attach scores and sort
    scored_docs = []
    for doc, score in zip(documents, scores):
        scored_doc = {**doc}
        scored_doc["rerank_score"] = float(score)
        scored_docs.append(scored_doc)

    # Sort by re-rank score (descending) and take top-k
    scored_docs.sort(key=lambda x: x["rerank_score"], reverse=True)
    top_results = scored_docs[:k]

    logger.info(
        f"Re-ranked {len(documents)} → top {len(top_results)} "
        f"(scores: {[round(d['rerank_score'], 3) for d in top_results]})"
    )

    return top_results
