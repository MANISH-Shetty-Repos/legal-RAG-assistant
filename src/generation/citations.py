"""
Citation Enforcement — Validate and parse citations from LLM responses.
"""

import re
from dataclasses import dataclass
from loguru import logger


@dataclass
class Citation:
    """Represents a single citation extracted from the LLM response."""

    filename: str
    page_number: int | str
    text_snippet: str = ""  # The claim that is being cited


def extract_citations(response_text: str) -> list[Citation]:
    """
    Extract all citations from an LLM response.

    Looks for patterns like: [Source: filename.pdf, Page: 12]

    Args:
        response_text: The LLM's response text

    Returns:
        List of Citation objects found in the response
    """
    # Pattern: [Source: filename, Page: number]
    pattern = r"\[Source:\s*(.+?)(?:,|\s*\|)\s*Page:\s*([^\]]+)\]"
    matches = re.findall(pattern, response_text)

    citations = []
    for filename, page in matches:
        citations.append(
            Citation(
                filename=filename.strip(),
                page_number=page.strip(),
            )
        )

    logger.debug(f"Extracted {len(citations)} citations from response")
    return citations


def validate_citations_from_text(
    response_text: str,
    available_sources: list[dict],
) -> dict:
    """
    Extract and validate citations from a response text against available source chunks.

    Args:
        response_text: The LLM response text
        available_sources: List of chunk dicts that were provided as context

    Returns:
        Validation results including the valid citation objects.
    """
    citations = extract_citations(response_text)
    return validate_citations(citations, available_sources)


def validate_citations(
    citations: list[Citation],
    available_sources: list[dict],
) -> dict:
    """
    Validate extracted citations against available source chunks.

    Args:
        citations: List of Citation objects from the response
        available_sources: List of chunk dicts that were provided as context

    Returns:
        Dict with validation results:
        {
            "total_citations": int,
            "valid_citations": int,
            "invalid_citations": int,
            "citation_rate": float,  # valid / total
            "citations": list[Citation],
            "details": list[dict]
        }
    """
    available_pairs = set()
    for chunk in available_sources:
        meta = chunk.get("metadata", {})
        filename = meta.get("filename", "")
        page = str(meta.get("page_number", ""))
        available_pairs.add((filename, page))

    details = []
    valid_citations: list[Citation] = []
    valid_count = 0

    for citation in citations:
        citation_pair = (citation.filename, str(citation.page_number))
        is_valid = citation_pair in available_pairs
        if is_valid:
            valid_count += 1
            valid_citations.append(citation)

        details.append(
            {
                "filename": citation.filename,
                "page_number": citation.page_number,
                "valid": is_valid,
            }
        )

    total = len(citations)

    return {
        "total_citations": total,
        "valid_citations": valid_count,
        "invalid_citations": total - valid_count,
        "citation_rate": valid_count / total if total > 0 else 0.0,
        "citations": valid_citations,
        "details": details,
    }


def has_citations(response_text: str) -> bool:
    """Quick check: does the response contain at least one citation?"""
    pattern = r"\[Source:\s*(.+?)(?:,|\s*\|)\s*Page:\s*([^\]]+)\]"
    return bool(re.search(pattern, response_text))


def add_citation_warning(response_text: str) -> str:
    """
    If the response has no citations, append a warning.
    """
    if not has_citations(response_text):
        response_text += (
            "\n\n> ⚠️ **Warning:** This response does not contain source citations. "
            "The information may not be verified against the available documents."
        )
    return response_text
