"""
ChromaDB Vector Store — Persistent vector storage and retrieval.
"""

import chromadb
from loguru import logger

from src.config import get_config
from src.document_processing.chunker import DocumentChunk


class VectorStore:
    """ChromaDB-backed vector store for document chunks."""

    def __init__(self):
        config = get_config()
        self.persist_dir = config.chroma.persist_dir
        self.collection_name = config.chroma.collection_name

        # Use Streamlit's cache_resource to prevent ChromaDB reload teardown bugs
        import streamlit as st
        
        @st.cache_resource
        def get_chroma_client(persist_dir):
            import chromadb
            return chromadb.PersistentClient(path=persist_dir)

        self.client = get_chroma_client(self.persist_dir)
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},  # Cosine similarity for BGE
        )

        logger.info(
            f"ChromaDB initialized: collection='{self.collection_name}', "
            f"persist_dir='{self.persist_dir}', "
            f"existing_count={self.collection.count()}"
        )

    def add_chunks(
        self, chunks: list[DocumentChunk], embeddings: list[list[float]]
    ) -> None:
        """
        Add document chunks with their embeddings to the vector store.

        Args:
            chunks: List of DocumentChunk objects
            embeddings: Corresponding embedding vectors
        """
        if not chunks:
            logger.warning("No chunks to add")
            return

        ids = [chunk.metadata.chunk_id for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [chunk.metadata.to_dict() for chunk in chunks]

        # Add in batches to avoid memory issues
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            end = min(i + batch_size, len(chunks))
            self.collection.add(
                ids=ids[i:end],
                documents=documents[i:end],
                embeddings=embeddings[i:end],
                metadatas=metadatas[i:end],
            )

        logger.info(
            f"Added {len(chunks)} chunks to ChromaDB (total: {self.collection.count()})"
        )

    def query(
        self,
        query_embedding: list[float],
        top_k: int | None = None,
        user_id: int | None = None,
        is_admin: bool = False,
    ) -> list[dict]:
        """
        Query the vector store for similar documents.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            user_id: Optional ID of the user querying
            is_admin: Whether the querying user is an admin

        Returns:
            List of dicts with keys: id, text, metadata, distance
        """
        config = get_config()
        k = top_k or config.retrieval.vector_top_k

        if self.collection.count() == 0:
            logger.warning("Vector store collection is empty. Returning empty results.")
            return []

        where = None
        if not is_admin:
            if user_id is None or user_id == 0:
                where = {"uploaded_by_id": 0}
            else:
                where = {"$or": [{"uploaded_by_id": 0}, {"uploaded_by_id": user_id}]}

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(k, self.collection.count()),
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        # Flatten results into a list of dicts
        output = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                output.append(
                    {
                        "id": results["ids"][0][i],
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                        "score": 1
                        - results["distances"][0][i],  # Convert distance to similarity
                    }
                )

        logger.debug(f"Vector query returned {len(output)} results")
        return output

    def get_all_chunks(self) -> list[dict]:
        """
        Retrieve all chunks from the vector store.
        Used for rebuilding BM25 index.

        Returns:
            List of dicts with keys: id, text, metadata
        """
        if self.collection.count() == 0:
            return []

        results = self.collection.get(
            include=["documents", "metadatas"],
        )

        output = []
        for i in range(len(results["ids"])):
            output.append(
                {
                    "id": results["ids"][i],
                    "text": results["documents"][i],
                    "metadata": results["metadatas"][i],
                }
            )

        return output

    def delete_by_filename(self, filename: str) -> int:
        """Delete all chunks from a specific file."""
        all_chunks = self.get_all_chunks()
        ids_to_delete = [
            c["id"] for c in all_chunks if c["metadata"].get("filename") == filename
        ]

        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)
            logger.info(f"Deleted {len(ids_to_delete)} chunks for '{filename}'")

        return len(ids_to_delete)

    def clear(self) -> None:
        """Delete the entire collection and recreate it."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("Cleared vector store")

    @property
    def count(self) -> int:
        """Return the number of chunks in the store."""
        return self.collection.count()
