"""
LangGraph Nodes — Individual processing steps in the RAG pipeline.
Each node takes the RAGState and returns a partial state update.
"""

import time
from loguru import logger

from src.orchestration.state import RAGState
from src.retrieval.vector_store import VectorStore
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.hybrid_search import HybridSearcher
from src.retrieval.reranker import rerank
from src.generation.llm import generate_response
from src.generation.citations import (
    validate_citations_from_text,
    add_citation_warning,
)
from src.generation.prompts import build_user_prompt
from src.config import get_config


# Module-level instances (set by graph.py during initialization)
_vector_store: VectorStore | None = None
_bm25_retriever: BM25Retriever | None = None
_hybrid_searcher: HybridSearcher | None = None


def set_retrieval_components(
    vector_store: VectorStore,
    bm25_retriever: BM25Retriever,
    hybrid_searcher: HybridSearcher,
):
    """Set the retrieval components for use by graph nodes."""
    global _vector_store, _bm25_retriever, _hybrid_searcher
    _vector_store = vector_store
    _bm25_retriever = bm25_retriever
    _hybrid_searcher = hybrid_searcher


def query_processing_node(state: RAGState) -> dict:
    """
    Node 1: Process and validate the user query.
    """
    start = time.time()
    query = state["query"].strip()

    if not query:
        return {
            "error": "Empty query provided",
            "latency": {**state.get("latency", {}), "query_processing": 0},
        }

    logger.info(f"Processing query: '{query[:80]}'")

    return {
        "query": query,
        "latency": {
            **state.get("latency", {}),
            "query_processing": time.time() - start,
        },
    }


def retrieval_node(state: RAGState) -> dict:
    """
    Node 2: Retrieve from BM25 and Vector DB.
    """
    start = time.time()
    query = state["query"]
    user_id = state.get("user_id")
    is_admin = state.get("is_admin", False)

    if _bm25_retriever is None or _vector_store is None:
        return {"error": "Retrieval components not initialized", "bm25_results": [], "vector_results": []}

    try:
        from src.document_processing.embeddings import embed_query
        config = get_config()

        # BM25 retrieval
        bm25_results = _bm25_retriever.query(
            query, top_k=config.retrieval.bm25_top_k, user_id=user_id, is_admin=is_admin
        )

        # Vector retrieval
        query_embedding = embed_query(query)
        vector_results = _vector_store.query(
            query_embedding,
            top_k=config.retrieval.vector_top_k,
            user_id=user_id,
            is_admin=is_admin,
        )

        logger.info(f"Retrieval Node: BM25={len(bm25_results)}, Vector={len(vector_results)}")

        return {
            "bm25_results": bm25_results,
            "vector_results": vector_results,
            "latency": {
                **state.get("latency", {}),
                "retrieval": time.time() - start,
            },
        }
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        return {
            "error": f"Retrieval failed: {str(e)}",
            "bm25_results": [],
            "vector_results": [],
            "latency": {
                **state.get("latency", {}),
                "retrieval": time.time() - start,
            },
        }


def hybrid_search_node(state: RAGState) -> dict:
    """
    Node 3: Perform Reciprocal Rank Fusion on BM25 and Vector results.
    """
    start = time.time()
    bm25_results = state.get("bm25_results", [])
    vector_results = state.get("vector_results", [])

    if _hybrid_searcher is None:
        return {"error": "Hybrid searcher not initialized", "hybrid_results": []}

    try:
        config = get_config()
        fused = _hybrid_searcher._reciprocal_rank_fusion(
            bm25_results=bm25_results,
            vector_results=vector_results,
            bm25_weight=1.0,
            vector_weight=1.0,
        )
        # Sort by fused score and return top-k
        k = config.retrieval.hybrid_top_k
        fused_sorted = sorted(fused.values(), key=lambda x: x["score"], reverse=True)[:k]

        logger.info(f"Hybrid Search Node: Fused={len(fused_sorted)}")

        return {
            "hybrid_results": fused_sorted,
            "latency": {
                **state.get("latency", {}),
                "hybrid_search": time.time() - start,
            },
        }
    except Exception as e:
        logger.error(f"Hybrid search fusion failed: {e}")
        return {
            "error": f"Hybrid search failed: {str(e)}",
            "hybrid_results": [],
            "latency": {
                **state.get("latency", {}),
                "hybrid_search": time.time() - start,
            },
        }


def reranking_node(state: RAGState) -> dict:
    """
    Node 3: Re-rank hybrid results using cross-encoder.
    """
    start = time.time()
    query = state["query"]
    hybrid_results = state.get("hybrid_results", [])

    if not hybrid_results:
        logger.warning("No hybrid results to re-rank")
        return {
            "reranked_results": [],
            "latency": {**state.get("latency", {}), "reranking": time.time() - start},
        }

    try:
        reranked = rerank(query, hybrid_results)

        logger.info(f"Re-ranking: {len(hybrid_results)} → {len(reranked)}")

        return {
            "reranked_results": reranked,
            "latency": {**state.get("latency", {}), "reranking": time.time() - start},
        }

    except Exception as e:
        logger.error(f"Re-ranking failed: {e}")
        # Fall back to using hybrid results directly
        config = get_config()
        return {
            "reranked_results": hybrid_results[: config.retrieval.rerank_top_k],
            "latency": {**state.get("latency", {}), "reranking": time.time() - start},
        }


def generation_node(state: RAGState) -> dict:
    """
    Node 4: Generate response using LLM with retrieved context.
    Supports response_mode parameters and follow-up recommendations.
    """
    start = time.time()
    query = state["query"]
    context_chunks = state.get("reranked_results", [])
    response_mode = state.get("response_mode", "normal")

    if not context_chunks:
        no_context_response = (
            "I don't have enough information in the available documents to answer this question. "
            "Please try uploading relevant documents or rephrasing your question."
        )
        return {
            "response": no_context_response,
            "context_text": "",
            "latency": {**state.get("latency", {}), "generation": time.time() - start},
            "follow_up_questions": [],
        }

    try:
        # Generate response using LLM with response_mode
        response = generate_response(query, context_chunks, response_mode=response_mode)

        # Validate citations against the provided context
        citation_validation = validate_citations_from_text(response, context_chunks)
        if citation_validation["valid_citations"] < 1 or citation_validation["valid_citations"] != citation_validation["total_citations"]:
            response = (
                "I do not have enough verified evidence in the available documents to answer this question. "
                "Please upload relevant documents or ask a different question."
            )
            citation_validation = {
                "total_citations": 0,
                "valid_citations": 0,
                "invalid_citations": 0,
                "citation_rate": 0.0,
                "citations": [],
                "details": [],
            }
        else:
            response = add_citation_warning(response)

        # Build context text for reference
        context_text = build_user_prompt(query, context_chunks)

        # Generate 3 follow-up questions
        follow_ups = []
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            from src.generation.llm import get_llm

            llm = get_llm()
            follow_up_prompt = [
                SystemMessage(
                    content=(
                        "You are a helpful assistant. Generate exactly 3 relevant, concise follow-up questions "
                        "that the user might want to ask next based on their original query and the assistant's response. "
                        "Return them as a simple numbered list from 1 to 3. Do not add any introductory or concluding text."
                    )
                ),
                HumanMessage(content=f"Original Query: {query}\nResponse: {response}"),
            ]
            follow_up_res = llm.invoke(follow_up_prompt).content
            # Parse lines starting with numbers
            for line in follow_up_res.split("\n"):
                line = line.strip()
                if (
                    line
                    and line[0].isdigit()
                    and len(line) > 1
                    and line[1] in [".", ")"]
                ):
                    question = line[2:].strip()
                    if question:
                        follow_ups.append(question)
        except Exception as fe:
            logger.error(f"Failed to generate follow-up recommendations: {fe}")

        # Fallback default recommendations if parsing failed or erred
        if not follow_ups:
            follow_ups = [
                "What evidence is required to support this?",
                "Where can I file a complaint for this issue?",
                "What is the contact or helpline number for this service?",
            ]

        logger.info(f"Response generated ({len(response)} chars)")

        return {
            "response": response,
            "context_text": context_text,
            "citation_validation": citation_validation,
            "latency": {**state.get("latency", {}), "generation": time.time() - start},
            "follow_up_questions": follow_ups[:3],
        }

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return {
            "response": f"An error occurred while generating the response: {str(e)}",
            "error": str(e),
            "latency": {**state.get("latency", {}), "generation": time.time() - start},
            "follow_up_questions": [],
        }


def citation_node(state: RAGState) -> dict:
    """
    Node 6: Extract and validate citations from the response.
    """
    start = time.time()
    citation_validation = state.get("citation_validation") or {
        "total_citations": 0,
        "valid_citations": 0,
        "invalid_citations": 0,
        "citation_rate": 0.0,
        "citations": [],
        "details": [],
    }
    citations_list = citation_validation.get("citations", [])
    citations_dicts = [
        {"filename": c.filename, "page_number": c.page_number} for c in citations_list
    ]

    logger.info(f"Validated citations: {len(citations_dicts)}")

    return {
        "citations": citations_dicts,
        "citation_validation": citation_validation or {
            "total_citations": 0,
            "valid_citations": 0,
            "invalid_citations": 0,
            "citation_rate": 0.0,
            "citations": [],
            "details": [],
        },
        "latency": {
            **state.get("latency", {}),
            "citation_extraction": time.time() - start,
        },
    }


def evaluation_node(state: RAGState) -> dict:
    """
    Node 7: Perform real-time LLM-as-a-judge evaluation of faithfulness and relevancy.
    """
    start = time.time()
    query = state.get("query", "")
    response = state.get("response", "")
    context_chunks = state.get("reranked_results", [])
    context_text = "\n\n".join([chunk["text"] for chunk in context_chunks])

    faithfulness = 0.0
    relevancy = 0.0

    try:
        from src.generation.evaluation import evaluate_faithfulness, evaluate_relevancy
        # Evaluate faithfulness
        faithfulness = evaluate_faithfulness(context_text, response)
        # Evaluate relevancy
        relevancy = evaluate_relevancy(query, response)
        logger.info(f"Evaluation Node: Faithfulness={faithfulness}, Relevancy={relevancy}")
    except Exception as e:
        logger.error(f"Real-time evaluation failed: {e}")

    return {
        "faithfulness_score": faithfulness,
        "relevancy_score": relevancy,
        "latency": {
            **state.get("latency", {}),
            "evaluation": time.time() - start,
        },
    }
