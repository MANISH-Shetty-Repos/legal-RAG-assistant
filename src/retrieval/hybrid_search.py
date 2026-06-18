"""
Hybrid Search — Reciprocal Rank Fusion (RRF) of BM25 + Vector results.
"""

from loguru import logger

from src.config import get_config
from src.document_processing.embeddings import embed_query
from src.retrieval.vector_store import VectorStore
from src.retrieval.bm25_retriever import BM25Retriever


class HybridSearcher:
    """
    Combines BM25 keyword retrieval and dense vector retrieval
    using Reciprocal Rank Fusion (RRF) for improved retrieval quality.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        bm25_retriever: BM25Retriever,
        rrf_k: int = 60,
    ):
        """
        Args:
            vector_store: ChromaDB vector store instance
            bm25_retriever: BM25 retriever instance
            rrf_k: RRF constant (default 60, standard value)
        """
        self.vector_store = vector_store
        self.bm25_retriever = bm25_retriever
        self.rrf_k = rrf_k

    def search(
        self,
        query: str,
        top_k: int | None = None,
        bm25_weight: float = 1.0,
        vector_weight: float = 1.0,
        user_id: int | None = None,
        is_admin: bool = False,
    ) -> list[dict]:
        """
        Perform hybrid search combining BM25 and vector retrieval.

        Args:
            query: Natural language query
            top_k: Number of final results to return
            bm25_weight: Weight multiplier for BM25 scores
            vector_weight: Weight multiplier for vector scores
            user_id: Optional ID of the user querying
            is_admin: Whether the querying user is an admin

        Returns:
            List of dicts with keys: id, text, metadata, score, sources
        """
        config = get_config()
        k = top_k or config.retrieval.hybrid_top_k

        # 1. BM25 retrieval
        bm25_results = self.bm25_retriever.query(
            query, top_k=config.retrieval.bm25_top_k, user_id=user_id, is_admin=is_admin
        )

        # 2. Vector retrieval
        query_embedding = embed_query(query)
        vector_results = self.vector_store.query(
            query_embedding,
            top_k=config.retrieval.vector_top_k,
            user_id=user_id,
            is_admin=is_admin,
        )

        # 3. Reciprocal Rank Fusion
        fused = self._reciprocal_rank_fusion(
            bm25_results=bm25_results,
            vector_results=vector_results,
            bm25_weight=bm25_weight,
            vector_weight=vector_weight,
        )

        # 4. Sort by fused score and return top-k
        fused_sorted = sorted(fused.values(), key=lambda x: x["score"], reverse=True)[
            :k
        ]

        logger.info(
            f"Hybrid search: BM25={len(bm25_results)}, Vector={len(vector_results)}, "
            f"Fused={len(fused_sorted)} (query: '{query[:50]}...')"
        )

        return fused_sorted

    def _reciprocal_rank_fusion(
        self,
        bm25_results: list[dict],
        vector_results: list[dict],
        bm25_weight: float,
        vector_weight: float,
    ) -> dict[str, dict]:
        """
        Merge results using Reciprocal Rank Fusion.

        RRF Score = Σ weight / (k + rank_i)

        Where k is the RRF constant and rank_i is the 1-based rank
        of the document in retriever i.
        """
        fused: dict[str, dict] = {}

        # Process BM25 results
        for rank, result in enumerate(bm25_results, start=1):
            doc_id = result["id"]
            rrf_score = bm25_weight / (self.rrf_k + rank)

            if doc_id not in fused:
                fused[doc_id] = {
                    "id": doc_id,
                    "text": result["text"],
                    "metadata": result["metadata"],
                    "score": 0.0,
                    "sources": [],
                }

            fused[doc_id]["score"] += rrf_score
            fused[doc_id]["sources"].append("bm25")

        # Process vector results
        for rank, result in enumerate(vector_results, start=1):
            doc_id = result["id"]
            rrf_score = vector_weight / (self.rrf_k + rank)

            if doc_id not in fused:
                fused[doc_id] = {
                    "id": doc_id,
                    "text": result["text"],
                    "metadata": result["metadata"],
                    "score": 0.0,
                    "sources": [],
                }

            fused[doc_id]["score"] += rrf_score
            fused[doc_id]["sources"].append("vector")

        return fused
