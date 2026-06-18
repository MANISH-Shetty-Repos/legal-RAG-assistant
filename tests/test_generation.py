"""
Unit Tests for LLM Generation and Citations
"""

from src.generation.citations import (
    extract_citations,
    validate_citations,
    has_citations,
)


def test_extract_citations():
    """Test extracting citations from generated response text."""
    text = "The applicant can request information [Source: RTI_Act_2005.txt, Page: 1] and gets response in 30 days [Source: RTI_Act.pdf, Page: 5]."

    citations = extract_citations(text)
    assert len(citations) == 2
    assert citations[0].filename == "RTI_Act_2005.txt"
    assert citations[0].page_number == "1"
    assert citations[1].filename == "RTI_Act.pdf"
    assert citations[1].page_number == "5"


def test_validate_citations():
    """Test validating citations against retrieved source metadata."""
    citations = extract_citations(
        "Reference text [Source: RTI_Act_2005.txt, Page: 2] and [Source: Invalid.txt, Page: 1]"
    )

    available_sources = [
        {"metadata": {"filename": "RTI_Act_2005.txt", "page_number": 2}},
        {
            "metadata": {
                "filename": "Consumer_Protection_Act_2019.txt",
                "page_number": 1,
            }
        },
    ]

    report = validate_citations(citations, available_sources)

    assert report["total_citations"] == 2
    assert report["valid_citations"] == 1
    assert report["invalid_citations"] == 1
    assert report["citation_rate"] == 0.5
    assert report["details"][0]["valid"] is True
    assert report["details"][1]["valid"] is False


def test_has_citations():
    """Test utility checking citation presence."""
    assert has_citations("No citations here.") is False
    assert has_citations("Contains one [Source: Doc.txt, Page: 1]") is True
