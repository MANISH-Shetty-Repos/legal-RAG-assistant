# Legal RAG Assistant – AI-Powered Legal Document Question Answering System

## Overview

The **Legal RAG Assistant** is a **Retrieval-Augmented Generation (RAG)** application that answers legal rights-related questions using verified Indian legal documents. Instead of relying solely on a Large Language Model (LLM), the system retrieves relevant legal provisions from an indexed knowledge base and generates grounded, citation-backed responses.

The application is built with a complete end-to-end RAG architecture featuring document ingestion, semantic search, hybrid retrieval, reranking, answer generation, and evaluation. Users can upload their own legal documents through the Streamlit interface, which are automatically processed, chunked, embedded, and indexed into ChromaDB for future retrieval without requiring manual reseeding.

The retrieval pipeline combines dense vector search with BM25 keyword search using Reciprocal Rank Fusion (RRF), followed by cross-encoder reranking to improve retrieval accuracy before passing the final context to the Groq-hosted Qwen3-32B language model.

This project demonstrates a production-ready implementation of modern RAG techniques using LangGraph orchestration, ChromaDB, Hugging Face embedding models, and Groq Cloud for high-performance inference, with integrated **evaluation**, **monitoring**, and **observability** to ensure reliable, high-quality, and trustworthy responses.


> **Disclaimer:** This application is intended for educational and informational purposes only. It should not be considered legal advice.

---

### Features

* Answer legal rights questions using a Retrieval-Augmented Generation (RAG) pipeline.
* Upload PDF legal documents through the UI for automatic processing and indexing.
* Automatically parse, chunk, embed, and store documents in ChromaDB.
* Perform hybrid retrieval using semantic search and BM25 keyword search.
* Improve retrieval accuracy with Cross-Encoder reranking.
* Generate grounded responses with source citations using Groq Cloud (Qwen3-32B).
* Built with LangGraph for a modular and scalable RAG workflow.
* Interactive Streamlit interface for document management and chat-based question answering.
* Evaluate response quality using RAGAS and LLM-as-a-Judge.
* Modular architecture designed for easy deployment and future scalability.

---

## Production Monitoring & Observability

To support production readiness and continuous quality assurance, the Legal RAG Assistant includes a comprehensive monitoring and observability layer that tracks system performance, retrieval quality, and response reliability throughout the RAG pipeline.

* Monitors end-to-end pipeline latency, including retrieval, reranking, LLM generation, evaluation, citation extraction, and total response time.
* Tracks retrieval quality using **Context Precision**, **Context Recall**, and **Answer Relevancy** metrics to evaluate retrieval effectiveness.
* Detects **hallucinations** and measures response faithfulness using **RAGAS** and **LLM-as-a-Judge** evaluation techniques.
* Automatically logs user queries, retrieved document chunks, source citations, model responses, evaluation scores, and system performance metrics for analysis and debugging.
* Provides a real-time monitoring dashboard to visualize **latency trends**, **retrieval performance**, **response quality**, and overall **system health**.
* Enables production-grade observability by identifying retrieval failures, hallucinations, slow responses, and quality degradation, supporting continuous monitoring and iterative improvement of the RAG system.



---

# System Architecture

```text
                          ┌──────────────────────────┐
                          │        User              │
                          └────────────┬─────────────┘
                                       │
                                       ▼
                    ┌─────────────────────────────────┐
                    │      Streamlit Frontend         │
                    │  • Chat Interface               │
                    │  • Document Upload              │
                    │  • Response Display             │
                    └────────────┬────────────────────┘
                                 │
                                 ▼
                ┌──────────────────────────────────────┐
                │       LangGraph Orchestrator         │
                └────────────┬─────────────────────────┘
                             │
         ┌───────────────────┼────────────────────┐
         │                   │                    │
         ▼                   ▼                    ▼
 ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐
 │ Query Handler  │  │Document Loader │  │Evaluation Layer │
 └───────┬────────┘  └────────┬───────┘  └─────────────────┘
         │                    │
         ▼                    ▼
 ┌────────────────┐   ┌───────────────────────┐
 │ Hybrid Search  │   │ Chunking & Embedding  │
 │                │   └──────────┬────────────┘
 │ • BM25         │              │
 │ • Vector Search│              ▼
 └───────┬────────┘     ┌─────────────────────┐
         │              │      ChromaDB       │
         ▼              │ Persistent Storage  │
 ┌────────────────┐     └─────────────────────┘
 │ RRF Fusion     │
 └───────┬────────┘
         ▼
 ┌─────────────────────────┐
 │ Cross Encoder Reranker  │
 └──────────┬──────────────┘
            ▼
 ┌─────────────────────────┐
 │ Groq Cloud (Qwen3-32B)  │
 └──────────┬──────────────┘
            ▼
 ┌─────────────────────────┐
 │ Response + Citations    │
 └─────────────────────────┘
```

---

# RAG Pipeline

```text
              Legal Documents
                     │
                     ▼
           Document Upload (UI)
                     │
                     ▼
              PDF Processing
                     │
                     ▼
             Document Chunking
                     │
                     ▼
        BGE Embedding Generation
                     │
                     ▼
        ChromaDB Vector Storage
                     │
──────────────────────────────────────────────────────────────
                     │
               User Question
                     │
                     ▼
           Query Preprocessing
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
  Dense Vector Search      BM25 Search
         │                       │
         └───────────┬───────────┘
                     ▼
        Reciprocal Rank Fusion
                     │
                     ▼
        Cross-Encoder Reranking
                     │
                     ▼
     Top Relevant Document Chunks
                     │
                     ▼
      Groq Cloud LLM (Qwen3-32B)
                     │
                     ▼
      Grounded Answer + Citations
```

---

## Technology Stack

| Category                 | Technology                                          |
| ------------------------ | --------------------------------------------------- |
| **Programming Language** | Python 3.11                                         |
| **Frontend**             | Streamlit                                           |
| **Backend API**          | FastAPI                                             |
| **LLM Orchestration**    | LangGraph                                           |
| **RAG Framework**        | LangChain                                           |
| **LLM Provider**         | Groq Cloud                                          |
| **LLM Model**            | Qwen3-32B                                           |
| **Embedding Model**      | BAAI BGE Base (bge-base-en-v1.5)                    |
| **Reranker**             | BAAI BGE Reranker Base                              |
| **Vector Database**      | ChromaDB                                            |
| **Retrieval**            | Dense Retrieval, BM25, Reciprocal Rank Fusion (RRF) |
| **Document Processing**  | PyPDF, Recursive Character Text Splitter            |
| **Evaluation**           | RAGAS, LLM-as-a-Judge                               |
| **CI/CD**                | GitHub Actions                                      |
| **Deployment**           | Docker, Render                                      |
| **Version Control**      | Git & GitHub                                        |
