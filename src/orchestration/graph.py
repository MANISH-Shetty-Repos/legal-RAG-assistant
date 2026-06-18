"""
LangGraph Workflow — The main RAG pipeline graph.
Connects all nodes into a directed acyclic graph for query processing.
"""

import time
from loguru import logger
from langgraph.graph import StateGraph, END

from src.orchestration.state import RAGState
from src.orchestration.nodes import (
    query_processing_node,
    retrieval_node,
    hybrid_search_node,
    reranking_node,
    generation_node,
    citation_node,
    evaluation_node,
    set_retrieval_components,
)
from src.retrieval.vector_store import VectorStore
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.hybrid_search import HybridSearcher
from src.document_processing.embeddings import embed_texts
from src.document_processing.loaders import load_document
from src.document_processing.chunker import chunk_documents


class RAGPipeline:
    """
    Production-grade RAG pipeline orchestrated by LangGraph.

    Flow:
        Query → Hybrid Retrieval → Re-Ranking → Generation → Citation
    """

    def __init__(self):
        """Initialize the RAG pipeline with all components."""
        logger.info("Initializing RAG Pipeline...")

        # Initialize retrieval components
        self.vector_store = VectorStore()
        self.bm25_retriever = BM25Retriever()
        self.hybrid_searcher = HybridSearcher(
            vector_store=self.vector_store,
            bm25_retriever=self.bm25_retriever,
        )

        # Set components for node access
        set_retrieval_components(
            vector_store=self.vector_store,
            bm25_retriever=self.bm25_retriever,
            hybrid_searcher=self.hybrid_searcher,
        )

        # Rebuild BM25 index from existing ChromaDB data
        self._rebuild_bm25_index()

        # Build the LangGraph
        self.graph = self._build_graph()

        logger.info("RAG Pipeline initialized successfully")

    def _build_graph(self):
        """Build and compile the LangGraph state machine."""

        # Define the graph
        workflow = StateGraph(RAGState)

        # Add nodes
        workflow.add_node("query_processing", query_processing_node)
        workflow.add_node("retrieval", retrieval_node)
        workflow.add_node("hybrid_search", hybrid_search_node)
        workflow.add_node("reranking", reranking_node)
        workflow.add_node("generation", generation_node)
        workflow.add_node("citation", citation_node)
        workflow.add_node("evaluation", evaluation_node)

        # Define edges (linear flow)
        workflow.set_entry_point("query_processing")
        workflow.add_edge("query_processing", "retrieval")
        workflow.add_edge("retrieval", "hybrid_search")
        workflow.add_edge("hybrid_search", "reranking")
        workflow.add_edge("reranking", "generation")
        workflow.add_edge("generation", "citation")
        workflow.add_edge("citation", "evaluation")
        workflow.add_edge("evaluation", END)

        # Compile
        compiled = workflow.compile()
        logger.info("LangGraph compiled successfully")

        return compiled

    def _rebuild_bm25_index(self):
        """Rebuild the BM25 index from ChromaDB data."""
        all_chunks = self.vector_store.get_all_chunks()
        if all_chunks:
            self.bm25_retriever.build_index(all_chunks)
            logger.info(f"BM25 index rebuilt with {len(all_chunks)} chunks")
        else:
            logger.info("No existing chunks in ChromaDB — BM25 index is empty")

    def ingest_file(self, file_path: str, uploaded_by_id: int = 0) -> dict:
        """
        Ingest a single document into the pipeline.

        Args:
            file_path: Path to the document file
            uploaded_by_id: ID of the user uploading the document

        Returns:
            Dict with ingestion results
        """
        start = time.time()

        # 1. Load document
        document = load_document(file_path)

        # 2. Chunk document
        chunks = chunk_documents([document], uploaded_by_id=uploaded_by_id)

        if not chunks:
            return {"status": "warning", "message": "No chunks generated from document"}

        # 3. Generate embeddings
        texts = [chunk.text for chunk in chunks]
        embeddings = embed_texts(texts)

        # 4. Store in ChromaDB
        self.vector_store.add_chunks(chunks, embeddings)

        # 5. Rebuild BM25 index
        self._rebuild_bm25_index()

        elapsed = time.time() - start

        result = {
            "status": "success",
            "filename": document.filename,
            "chunks": len(chunks),
            "pages": document.total_pages,
            "time_seconds": round(elapsed, 2),
        }

        logger.info(
            f"Ingested '{document.filename}': {len(chunks)} chunks in {elapsed:.2f}s"
        )
        return result

    def query(self, query: str) -> dict:
        """
        Process a user query through the full RAG pipeline.
        """
        return self.query_with_state({"query": query})

    def query_with_state(self, initial_state_override: dict) -> dict:
        """
        Process a user query with custom state overrides (e.g. response_mode, user_id).
        """
        start = time.time()

        # Initialize state with overrides
        state: RAGState = {
            "query": initial_state_override.get("query", ""),
            "bm25_results": [],
            "vector_results": [],
            "hybrid_results": [],
            "reranked_results": [],
            "context_text": "",
            "response": "",
            "citations": [],
            "citation_validation": {
                "total_citations": 0,
                "valid_citations": 0,
                "invalid_citations": 0,
                "citation_rate": 0.0,
                "citations": [],
                "details": [],
            },
            "error": "",
            "latency": {},
            "faithfulness_score": 0.0,
            "relevancy_score": 0.0,
            "response_mode": initial_state_override.get("response_mode", "normal"),
            "user_id": initial_state_override.get("user_id"),
            "is_admin": initial_state_override.get("is_admin", False),
            "follow_up_questions": [],
        }

        # Run the graph
        final_state = self.graph.invoke(state)

        total_time = time.time() - start

        result = {
            "query": state["query"],
            "response": final_state.get("response", ""),
            "citations": final_state.get("citations", []),
            "source_chunks": final_state.get("reranked_results", []),
            "latency": {
                **final_state.get("latency", {}),
                "total": round(total_time, 3),
            },
            "error": final_state.get("error", ""),
            "response_mode": final_state.get("response_mode", "normal"),
            "follow_up_questions": final_state.get("follow_up_questions", []),
            "faithfulness_score": final_state.get("faithfulness_score", 0.0),
            "relevancy_score": final_state.get("relevancy_score", 0.0),
        }

        logger.info(
            f"Query processed in {total_time:.2f}s — "
            f"Sources: {len(result['source_chunks'])}, "
            f"Citations: {len(result['citations'])}"
        )

        return result

    def get_stats(self) -> dict:
        """Get pipeline statistics."""
        return {
            "total_chunks": self.vector_store.count,
            "bm25_index_size": self.bm25_retriever.index_size,
        }
