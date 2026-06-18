"""
Metadata Extraction — Enrich document chunks with structured metadata.
"""

from datetime import datetime, timezone
from dataclasses import dataclass


@dataclass
class ChunkMetadata:
    """Structured metadata for a document chunk."""

    filename: str
    file_path: str
    file_type: str
    page_number: int
    chunk_id: str
    chunk_index: int
    upload_date: str
    total_chunks_in_doc: int = 0
    uploaded_by_id: int = 0  # 0 represents system/admin public documents

    def to_dict(self) -> dict:
        """Convert to dictionary for ChromaDB storage."""
        return {
            "filename": self.filename,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "page_number": self.page_number,
            "chunk_id": self.chunk_id,
            "chunk_index": self.chunk_index,
            "upload_date": self.upload_date,
            "total_chunks_in_doc": self.total_chunks_in_doc,
            "uploaded_by_id": self.uploaded_by_id,
        }


def generate_chunk_id(filename: str, page_number: int, chunk_index: int) -> str:
    """
    Generate a unique chunk ID.

    Format: {filename_stem}__p{page}__c{chunk_index}
    Example: RTI_Act__p5__c3
    """
    stem = filename.rsplit(".", 1)[0].replace(" ", "_")
    return f"{stem}__p{page_number}__c{chunk_index}"


def create_chunk_metadata(
    filename: str,
    file_path: str,
    file_type: str,
    page_number: int,
    chunk_index: int,
    upload_date: str | None = None,
    uploaded_by_id: int = 0,
) -> ChunkMetadata:
    """Create metadata for a document chunk."""
    return ChunkMetadata(
        filename=filename,
        file_path=file_path,
        file_type=file_type,
        page_number=page_number,
        chunk_id=generate_chunk_id(filename, page_number, chunk_index),
        chunk_index=chunk_index,
        upload_date=upload_date or datetime.now(timezone.utc).isoformat(),
        uploaded_by_id=uploaded_by_id,
    )
