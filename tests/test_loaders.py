"""
Unit Tests for Document Loaders
"""

import pytest
from src.document_processing.loaders import (
    load_document,
)


def test_text_loader_txt(tmp_path):
    """Test loading a plain text file."""
    file_path = tmp_path / "test.txt"
    content = "Hello Indian Citizen rights information content."
    file_path.write_text(content, encoding="utf-8")

    doc = load_document(str(file_path))

    assert doc.filename == "test.txt"
    assert doc.file_type == "txt"
    assert doc.total_pages == 1
    assert doc.pages[0].text == content
    assert doc.pages[0].page_number == 1


def test_text_loader_md(tmp_path):
    """Test loading a markdown file."""
    file_path = tmp_path / "test.md"
    content = "# Citizen Rights\n\nThis is a markdown document."
    file_path.write_text(content, encoding="utf-8")

    doc = load_document(str(file_path))

    assert doc.filename == "test.md"
    assert doc.file_type == "markdown"
    assert doc.pages[0].text == content.strip()


def test_unsupported_file_type():
    """Test that unsupported file extensions raise ValueError."""
    with pytest.raises(ValueError):
        load_document("some_file.xyz")
