"""
Production-Grade RAG System - Central Configuration
Loads environment variables and provides typed configuration objects.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load .env from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class LLMConfig(BaseModel):
    """LLM configuration settings."""

    base_url: str = Field(
        default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )
    model: str = Field(default_factory=lambda: os.getenv("LLM_MODEL", "qwen3:1.5b"))
    temperature: float = Field(
        default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.1"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "2048"))
    )


class EmbeddingConfig(BaseModel):
    """Embedding model configuration."""

    model_name: str = Field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
    )
    dimension: int = Field(
        default_factory=lambda: int(os.getenv("EMBEDDING_DIMENSION", "768"))
    )


class RerankerConfig(BaseModel):
    """Cross-encoder re-ranker configuration."""

    model_name: str = Field(
        default_factory=lambda: os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-base")
    )


class RetrievalConfig(BaseModel):
    """Retrieval pipeline configuration."""

    bm25_top_k: int = Field(default_factory=lambda: int(os.getenv("BM25_TOP_K", "20")))
    vector_top_k: int = Field(
        default_factory=lambda: int(os.getenv("VECTOR_TOP_K", "20"))
    )
    hybrid_top_k: int = Field(
        default_factory=lambda: int(os.getenv("HYBRID_TOP_K", "20"))
    )
    rerank_top_k: int = Field(
        default_factory=lambda: int(os.getenv("RERANK_TOP_K", "5"))
    )
    chunk_size: int = Field(default_factory=lambda: int(os.getenv("CHUNK_SIZE", "500")))
    chunk_overlap: int = Field(
        default_factory=lambda: int(os.getenv("CHUNK_OVERLAP", "100"))
    )


class ChromaConfig(BaseModel):
    """ChromaDB configuration."""

    persist_dir: str = Field(
        default_factory=lambda: os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    )
    collection_name: str = Field(
        default_factory=lambda: os.getenv("CHROMA_COLLECTION_NAME", "rag_documents")
    )


class AppConfig(BaseModel):
    """Top-level application configuration."""

    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_dir: Path = Field(default_factory=lambda: Path(os.getenv("LOG_DIR", "./logs")))
    data_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("DATA_DIR", "./data"))
    )
    project_root: Path = Field(default=PROJECT_ROOT)
    database_url: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "postgresql://user:password@localhost:5432/citizen_rights_db",
        )
    )

    # Sub-configurations

    llm: LLMConfig = Field(default_factory=LLMConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    reranker: RerankerConfig = Field(default_factory=RerankerConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    chroma: ChromaConfig = Field(default_factory=ChromaConfig)


# Singleton configuration instance
_config: AppConfig | None = None


def get_config() -> AppConfig:
    """Get or create the application configuration singleton."""
    global _config
    if _config is None:
        _config = AppConfig()
    return _config
