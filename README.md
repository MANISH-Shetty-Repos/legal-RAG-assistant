# Indian Legal Rights Assistant

## Overview

The **Indian Legal Rights Assistant** is a production-grade **Retrieval-Augmented Generation (RAG)** application that answers legal rights-related questions using verified Indian legal documents. Instead of relying solely on a Large Language Model (LLM), the system retrieves relevant legal provisions from an indexed knowledge base and generates grounded, citation-backed responses.

The application is built with a complete end-to-end RAG architecture featuring document ingestion, semantic search, hybrid retrieval, reranking, answer generation, and evaluation. Users can upload their own legal documents through the Streamlit interface, which are automatically processed, chunked, embedded, and indexed into ChromaDB for future retrieval without requiring manual reseeding.

The retrieval pipeline combines dense vector search with BM25 keyword search using Reciprocal Rank Fusion (RRF), followed by cross-encoder reranking to improve retrieval accuracy before passing the final context to the Groq-hosted Qwen3-32B language model.

This project demonstrates practical implementation of modern RAG techniques using LangGraph orchestration, ChromaDB, Hugging Face embedding models, and Groq Cloud for high-performance inference.

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

# Technology Stack

| Category                 | Technology                       |
| ------------------------ | -------------------------------- |
| **Programming Language** | Python 3.11                      |
| **Frontend**             | Streamlit                        |
| **Backend API**          | FastAPI                          |
| **LLM Orchestration**    | LangGraph                        |
| **RAG Framework**        | LangChain                        |
| **LLM Provider**         | Groq Cloud                       |
| **LLM Model**            | Qwen3-32B                        |
| **Embedding Model**      | BAAI BGE Base (bge-base-en-v1.5) |
| **Reranker**             | BAAI BGE Reranker Base           |
| **Vector Database**      | ChromaDB                         |
| **Keyword Retrieval**    | BM25                             |
| **Hybrid Search**        | Reciprocal Rank Fusion (RRF)     |
| **Evaluation**           | RAGAS, LLM-as-a-Judge            |
| **Document Processing**  | PyPDF, Recursive Text Splitter   |
| **Deployment**           | Docker, Render                   |
| **Version Control**      | Git & GitHub                     |
