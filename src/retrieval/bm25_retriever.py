"""
BM25 Retriever — Keyword-based retrieval using Okapi BM25 algorithm.
"""

from rank_bm25 import BM25Okapi
from loguru import logger

from src.config import get_config


class BM25Retriever:
    """
    BM25 keyword retriever that maintains an index of document chunks.
    The index is built from chunk texts and can be queried with natural language.
    """

    def __init__(self):
        self.corpus: list[dict] = []  # Store full chunk dicts
        self.tokenized_corpus: list[list[str]] = []
        self.bm25: BM25Okapi | None = None

    def build_index(self, chunks: list[dict]) -> None:
        """
        Build or rebuild the BM25 index from chunk data.

        Args:
            chunks: List of dicts with at least 'id', 'text', 'metadata' keys
        """
        self.corpus = chunks
        self.tokenized_corpus = [self._tokenize(chunk["text"]) for chunk in chunks]

        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)
            logger.info(f"BM25 index built with {len(chunks)} documents")
        else:
            self.bm25 = None
            logger.warning("BM25 index is empty — no documents to index")

    def query(
        self,
        query: str,
        top_k: int | None = None,
        user_id: int | None = None,
        is_admin: bool = False,
    ) -> list[dict]:
        """
        Retrieve top-k documents matching the query using BM25 scoring.

        Args:
            query: Natural language query string
            top_k: Number of results to return
            user_id: Optional ID of the user querying
            is_admin: Whether the querying user is an admin

        Returns:
            List of dicts with keys: id, text, metadata, score
        """
        if self.bm25 is None or not self.corpus:
            logger.warning("BM25 index is empty. Returning empty results.")
            return []

        config = get_config()
        k = top_k or config.retrieval.bm25_top_k

        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        # Sort all indices by score descending to apply permissions check on sorted list
        scored_indices = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )

        results = []
        for idx in scored_indices:
            if scores[idx] > 0:  # Only include non-zero scores
                meta = self.corpus[idx]["metadata"]
                uploaded_by = meta.get("uploaded_by_id", 0)

                # Permission check
                if not is_admin:
                    if user_id is None or user_id == 0:
                        if uploaded_by != 0:
                            continue
                    else:
                        if uploaded_by != 0 and uploaded_by != user_id:
                            continue

                results.append(
                    {
                        "id": self.corpus[idx]["id"],
                        "text": self.corpus[idx]["text"],
                        "metadata": self.corpus[idx]["metadata"],
                        "score": float(scores[idx]),
                    }
                )
                if len(results) >= k:
                    break

        logger.debug(
            f"BM25 query returned {len(results)} results for: '{query[:50]}...'"
        )
        return results

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Simple whitespace + lowercase tokenization."""
        return text.lower().split()

    @property
    def index_size(self) -> int:
        """Return the number of documents in the index."""
        return len(self.corpus)
