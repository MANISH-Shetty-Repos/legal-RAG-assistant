"""
Unit Tests for Semantic Chunker
"""

from src.document_processing.loaders import LoadedDocument, PageContent
from src.document_processing.chunker import SemanticChunker


def test_semantic_chunker():
    """Test splitting a loaded document into chunks."""
    pages = [
        PageContent(
            text="Section A of the Right to Information Act 2005. It provides citizens the right to request information.",
            page_number=1,
        ),
        PageContent(
            text="Section B contains exemptions from disclosure. For example information affecting national security.",
            page_number=2,
        ),
    ]

    doc = LoadedDocument(
        filename="test_act.txt",
        file_path="/path/to/test_act.txt",
        file_type="txt",
        upload_date="2026-06-16T00:00:00Z",
        pages=pages,
        total_pages=2,
    )

    # Use a small chunk size to force multiple chunks
    chunker = SemanticChunker(chunk_size=50, chunk_overlap=10)
    chunks = chunker.chunk_document(doc)

    assert len(chunks) > 0
    # Every chunk must have correct metadata
    for i, chunk in enumerate(chunks):
        assert chunk.metadata.filename == "test_act.txt"
        assert chunk.metadata.chunk_index == i
        assert chunk.metadata.total_chunks_in_doc == len(chunks)
        assert len(chunk.text) > 0
