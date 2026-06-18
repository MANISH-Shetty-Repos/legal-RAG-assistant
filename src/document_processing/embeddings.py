"""
Embedding Generation — BGE Embeddings via HuggingFace.
Wraps the BAAI/bge-base-en-v1.5 model for generating document and query embeddings.
"""

from loguru import logger
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import get_config


_embedding_model: HuggingFaceEmbeddings | None = None


def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Get or create the singleton embedding model.

    Returns:
        HuggingFaceEmbeddings instance configured with BGE model.
    """
    global _embedding_model

    if _embedding_model is None:
        config = get_config()
        model_name = config.embedding.model_name

        logger.info(f"Loading embedding model: {model_name}")

        _embedding_model = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={
                "normalize_embeddings": True,  # BGE models benefit from normalization
                "batch_size": 32,
            },
        )

        logger.info(f"Embedding model loaded: {model_name}")

    return _embedding_model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts.

    Args:
        texts: List of text strings to embed

    Returns:
        List of embedding vectors (each is a list of floats)
    """
    model = get_embedding_model()
    embeddings = model.embed_documents(texts)
    logger.debug(
        f"Embedded {len(texts)} texts → {len(embeddings)} vectors (dim={len(embeddings[0])})"
    )
    return embeddings


def embed_query(query: str) -> list[float]:
    """
    Generate embedding for a single query.

    BGE models use a different prefix for queries vs documents.

    Args:
        query: Query string

    Returns:
        Embedding vector
    """
    model = get_embedding_model()
    embedding = model.embed_query(query)
    return embedding
