"""
Semantic Chunking Engine — Split documents into meaningful chunks
with metadata preservation.
"""

from dataclasses import dataclass
from loguru import logger

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import get_config
from src.document_processing.loaders import LoadedDocument
from src.document_processing.metadata import ChunkMetadata, create_chunk_metadata


@dataclass
class DocumentChunk:
    """A chunk of text with associated metadata."""

    text: str
    metadata: ChunkMetadata

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {"text": self.text, **self.metadata.to_dict()}


class SemanticChunker:
    """
    Splits documents into semantically meaningful chunks using
    RecursiveCharacterTextSplitter with configurable size and overlap.
    """

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        config = get_config()
        self.chunk_size = chunk_size or config.retrieval.chunk_size
        self.chunk_overlap = chunk_overlap or config.retrieval.chunk_overlap

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=[
                "\n\n\n",  # Triple newline (major section breaks)
                "\n\n",  # Double newline (paragraphs)
                "\n",  # Single newline
                ". ",  # Sentence boundary
                "? ",  # Question boundary
                "! ",  # Exclamation boundary
                "; ",  # Semicolon boundary
                ", ",  # Comma boundary
                " ",  # Word boundary
                "",  # Character boundary (last resort)
            ],
            is_separator_regex=False,
        )

    def chunk_document(
        self, document: LoadedDocument, uploaded_by_id: int = 0
    ) -> list[DocumentChunk]:
        """
        Split a LoadedDocument into chunks with metadata.

        Each page is chunked independently to preserve page-level metadata.
        """
        all_chunks: list[DocumentChunk] = []
        global_chunk_index = 0

        for page in document.pages:
            if not page.text.strip():
                continue

            # Split this page's text into chunks
            text_chunks = self.splitter.split_text(page.text)

            for chunk_text in text_chunks:
                if not chunk_text.strip():
                    continue

                metadata = create_chunk_metadata(
                    filename=document.filename,
                    file_path=document.file_path,
                    file_type=document.file_type,
                    page_number=page.page_number,
                    chunk_index=global_chunk_index,
                    upload_date=document.upload_date,
                    uploaded_by_id=uploaded_by_id,
                )

                all_chunks.append(
                    DocumentChunk(
                        text=chunk_text.strip(),
                        metadata=metadata,
                    )
                )
                global_chunk_index += 1

        # Update total_chunks_in_doc for all chunks
        for chunk in all_chunks:
            chunk.metadata.total_chunks_in_doc = len(all_chunks)

        logger.info(
            f"Chunked '{document.filename}' → {len(all_chunks)} chunks "
            f"(chunk_size={self.chunk_size}, overlap={self.chunk_overlap})"
        )
        return all_chunks


def chunk_documents(
    documents: list[LoadedDocument], uploaded_by_id: int = 0
) -> list[DocumentChunk]:
    """
    Convenience function: chunk a list of documents.

    Args:
        documents: List of LoadedDocument objects

    Returns:
        Flat list of all DocumentChunks
    """
    chunker = SemanticChunker()
    all_chunks = []
    for doc in documents:
        chunks = chunker.chunk_document(doc, uploaded_by_id=uploaded_by_id)
        all_chunks.extend(chunks)

    logger.info(f"Total chunks from {len(documents)} documents: {len(all_chunks)}")
    return all_chunks
