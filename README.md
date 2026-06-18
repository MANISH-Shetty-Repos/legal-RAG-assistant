# Indian Legal Rights Assistant

## Overview

Indian Legal Rights Assistant is a production-grade Retrieval-Augmented Generation (RAG) application designed to answer legal rights-related questions using verified Indian legal documents. The system combines semantic search, keyword-based retrieval, reranking, and large language models to generate accurate, context-aware responses with source citations.

The project demonstrates an end-to-end RAG pipeline suitable for real-world AI applications, including document ingestion, retrieval optimization, response generation, evaluation, and deployment.

> **Disclaimer:** This application is intended for educational and informational purposes only. It does not provide legal advice.

---

## Features

* Domain-specific legal knowledge base
* Hybrid retrieval (BM25 + Vector Search)
* BGE embedding model for semantic search
* Cross-encoder reranking for improved retrieval quality
* Citation-based answer generation
* LangGraph workflow orchestration
* Local Large Language Model (LLM) integration
* REST API using FastAPI
* Interactive web interface using Streamlit
* Automated evaluation with RAGAS
* Dockerized deployment
* Logging and monitoring support

---

## System Architecture

```
Legal Documents
        │
        ▼
Document Processing
        │
        ▼
Chunking & Metadata Extraction
        │
        ▼
Embedding Generation (BGE)
        │
        ▼
ChromaDB Vector Store
        │
        ▼
User Query
        │
        ▼
Hybrid Retrieval
(BM25 + Vector Search)
        │
        ▼
Cross Encoder Reranker
        │
        ▼
LangGraph RAG Pipeline
        │
        ▼
Local LLM
        │
        ▼
Final Response with Citations
```

---

## Technology Stack

| Category             | Technologies           |
| -------------------- | ---------------------- |
| Programming Language | Python                 |
| Frameworks           | LangChain, LangGraph   |
| API                  | FastAPI                |
| Frontend             | Streamlit              |
| Vector Database      | ChromaDB               |
| Embedding Model      | BGE Embeddings         |
| Reranker             | BGE Cross Encoder      |
| LLM                  | Local LLM (Llama/Qwen) |
| Retrieval            | BM25 + Dense Retrieval |
| Evaluation           | RAGAS                  |
| Deployment           | Docker                 |
| Version Control      | Git & GitHub           |

---

## RAG Pipeline

1. Collect and preprocess legal documents.
2. Split documents into optimized chunks.
3. Generate embeddings using the BGE embedding model.
4. Store embeddings in ChromaDB.
5. Retrieve relevant documents using Hybrid Search (BM25 + Vector Search).
6. Rerank retrieved results using a Cross Encoder.
7. Generate grounded responses with the Local LLM.
8. Return answers along with supporting citations.
9. Evaluate response quality using RAGAS.

---

## Future Improvements

* User authentication and authorization
* Conversation memory
* Continuous document indexing
* Advanced observability
* Cloud deployment
