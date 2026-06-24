# Indian Legal Rights Assistant

## Overview

Indian Legal Rights Assistant is a production-grade Retrieval-Augmented Generation (RAG) application designed to answer legal rights-related questions using verified Indian legal documents. The system combines semantic search, keyword-based retrieval, reranking, and large language models to generate accurate, context-aware responses with source citations.

The project demonstrates an end-to-end RAG pipeline suitable for real-world AI applications, including document ingestion, retrieval optimization, response generation, evaluation, and deployment.

> **Disclaimer:** This application is intended for educational and informational purposes only. It does not provide legal advice.

---

## Architecture

```
User Question
      │
      ▼
┌─────────────────────────────┐
│     Streamlit Frontend      │
│       (frontend/app.py)     │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│   LangGraph RAG Pipeline    │
│  (src/orchestration/graph)  │
│                             │
│  ┌───────────────────────┐  │
│  │  Query Processing     │  │
│  └──────────┬────────────┘  │
│             │               │
│  ┌──────────▼────────────┐  │
│  │  Vector Search        │──│──▶ ChromaDB (Embedded)
│  │  BM25 Search          │──│──▶ In-Memory BM25 Index
│  └──────────┬────────────┘  │
│             │               │
│  ┌──────────▼────────────┐  │
│  │  Hybrid Fusion (RRF)  │  │
│  └──────────┬────────────┘  │
│             │               │
│  ┌──────────▼────────────┐  │
│  │  Cross-Encoder        │──│──▶ BGE Reranker (HuggingFace)
│  │  Reranking            │  │
│  └──────────┬────────────┘  │
│             │               │
│  ┌──────────▼────────────┐  │
│  │  LLM Generation       │──│──▶ Groq Cloud (Qwen3-32B)
│  └──────────┬────────────┘  │
│             │               │
│  ┌──────────▼────────────┐  │
│  │  Citation Extraction  │  │
│  └──────────┬────────────┘  │
│             │               │
│  ┌──────────▼────────────┐  │
│  │  Evaluation (Judge)   │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
             │
             ▼
   Response with Citations
```

---

## Technology Stack

| Category             | Technologies                     |
| -------------------- | -------------------------------- |
| Programming Language | Python                           |
| Frameworks           | LangChain, LangGraph             |
| LLM Provider         | Groq Cloud (Free Tier)           |
| LLM Model            | Qwen3-32B                        |
| API                  | FastAPI                          |
| Frontend             | Streamlit                        |
| Vector Database      | ChromaDB                         |
| Embedding Model      | BGE Embeddings (bge-base-en-v1.5)|
| Reranker             | BGE Cross Encoder                |
| Retrieval            | BM25 + Dense Retrieval           |
| Evaluation           | RAGAS + LLM-as-a-Judge           |
| Deployment           | Docker, Render                   |
| Version Control      | Git & GitHub                     |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Free Groq API key from [console.groq.com/keys](https://console.groq.com/keys)

### 1. Clone & Configure

```bash
git clone https://github.com/your-username/legal-RAG-assistant.git
cd legal-RAG-assistant

cp .env.example .env
# Edit .env and set your GROQ_API_KEY
```

### 2. Setup & Run

```bash
make setup          # Create venv and install dependencies
make seed           # Ingest sample legal documents
make run-ui         # Launch Streamlit on http://localhost:8501
```

### 3. Optional: FastAPI Backend

```bash
make run-api        # Launch FastAPI on http://localhost:8000
```

---

## Docker

### Standalone (Recommended)

```bash
docker build -t rag-system .
docker run --rm -p 8501:8501 --env-file .env rag-system
```

### Docker Compose

```bash
docker compose up -d --build
docker compose down
```

---

## Render Deployment

This project is designed to deploy on **Render Free Tier**.

### Steps

1. Push your repository to GitHub.
2. Create a new **Web Service** on [Render](https://render.com).
3. Connect your GitHub repository.
4. Configure:
   - **Environment**: Docker
   - **Dockerfile Path**: `./Dockerfile`
5. Add environment variable:
   - `GROQ_API_KEY` = your Groq API key
6. Deploy.

Render automatically injects the `PORT` environment variable. The Dockerfile is configured to use `${PORT:-8501}`.

---

## Environment Variables

| Variable                | Default              | Description                         |
| ----------------------- | -------------------- | ----------------------------------- |
| `GROQ_API_KEY`          | (required)           | Groq Cloud API key                  |
| `GROQ_MODEL`            | `qwen/qwen3-32b`    | Groq model identifier               |
| `LLM_TEMPERATURE`       | `0.1`                | LLM temperature                     |
| `LLM_MAX_TOKENS`        | `2048`               | Max tokens per response             |
| `EMBEDDING_MODEL`       | `BAAI/bge-base-en-v1.5` | HuggingFace embedding model      |
| `EMBEDDING_DIMENSION`   | `768`                | Embedding vector dimension          |
| `RERANKER_MODEL`        | `BAAI/bge-reranker-base` | Cross-encoder reranker model     |
| `BM25_TOP_K`            | `20`                 | BM25 retrieval top-k                |
| `VECTOR_TOP_K`          | `20`                 | Vector retrieval top-k              |
| `HYBRID_TOP_K`          | `20`                 | Hybrid fusion top-k                 |
| `RERANK_TOP_K`          | `5`                  | Reranker top-k                      |
| `CHUNK_SIZE`            | `500`                | Document chunk size (characters)    |
| `CHUNK_OVERLAP`         | `100`                | Chunk overlap (characters)          |
| `CHROMA_PERSIST_DIR`    | `./chroma_db`        | ChromaDB persistence directory      |
| `CHROMA_COLLECTION_NAME`| `rag_documents`      | ChromaDB collection name            |
| `LOG_LEVEL`             | `INFO`               | Logging level                       |
| `LOG_DIR`               | `./logs`             | Log file directory                  |
| `DATA_DIR`              | `./data`             | Data directory                      |
| `PORT`                  | `8501`               | Streamlit server port (set by Render)|

---

## Project Structure

```
.
├── frontend/                   # Streamlit UI
│   ├── app.py                  # Main entry point
│   ├── styles.py               # Global CSS
│   ├── components/             # Sidebar, chat message, landing
│   └── pages/                  # Chat page, evaluation dashboard
├── src/                        # Backend source code
│   ├── config.py               # Central configuration
│   ├── api/                    # FastAPI REST API
│   ├── document_processing/    # Loaders, chunker, embeddings
│   ├── generation/             # LLM wrapper, prompts, citations, evaluation
│   ├── orchestration/          # LangGraph pipeline (graph, nodes, state)
│   └── retrieval/              # Vector store, BM25, hybrid search, reranker
├── scripts/                    # Utility scripts
│   ├── seed_documents.py       # Document ingestion
│   ├── run_evaluation.py       # RAGAS evaluation
│   └── test_query.py           # Quick retrieval test
├── evaluation/                 # Evaluation testset and reports
├── data/                       # Document storage (raw/processed)
├── Dockerfile                  # Production Docker image
├── docker-compose.yml          # Optional Compose file
├── Makefile                    # Development commands
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
└── README.md                   # This file
```

---

## RAG Pipeline

1. Collect and preprocess legal documents.
2. Split documents into optimized chunks.
3. Generate embeddings using the BGE embedding model.
4. Store embeddings in ChromaDB.
5. Retrieve relevant documents using Hybrid Search (BM25 + Vector Search).
6. Rerank retrieved results using a Cross Encoder.
7. Generate grounded responses via Groq Cloud LLM.
8. Return answers along with supporting citations.
9. Evaluate response quality using LLM-as-a-Judge metrics.

---

## Development Commands

| Command         | Description                          |
| --------------- | ------------------------------------ |
| `make setup`    | Create venv and install dependencies |
| `make install`  | Install dependencies (existing venv) |
| `make run-ui`   | Launch Streamlit frontend            |
| `make run-api`  | Launch FastAPI backend               |
| `make seed`     | Ingest sample documents              |
| `make test`     | Run all tests                        |
| `make evaluate` | Run RAGAS evaluation                 |
| `make lint`     | Run linter                           |
| `make format`   | Format code                          |
| `make clean`    | Remove generated data                |
| `make clean-all`| Full clean including venv            |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `GROQ_API_KEY is not set` | Add your API key to `.env`. Get one free at [console.groq.com/keys](https://console.groq.com/keys) |
| `Rate limit exceeded` | Groq free tier allows ~30 req/min. Wait and retry. |
| Slow first query | HuggingFace embedding/reranker models download on first use (~800MB). Subsequent queries are fast. |
| ChromaDB errors on Streamlit reload | The app uses singleton caching. Restart the app if issues persist. |
| Docker build fails | Ensure Docker has at least 4GB memory available for the build stage. |
| Port already in use | Change the port: `streamlit run frontend/app.py --server.port 8502` |

---

## Future Improvements

* User authentication and authorization
* Conversation memory
* Continuous document indexing
* Advanced observability
* Model caching in Docker build
