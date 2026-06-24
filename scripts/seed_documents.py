"""
Seed Documents Script — Ingest sample Indian legal documents into the RAG system.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from src.orchestration.graph import RAGPipeline


def main():
    """Seed the RAG system with sample Indian legal documents."""

    raw_dir = project_root / "data" / "raw"

    if not raw_dir.exists():
        logger.error(f"Data directory not found: {raw_dir}")
        sys.exit(1)

    # Check for documents
    supported_extensions = {".pdf", ".docx", ".txt", ".md", ".markdown"}
    files = [f for f in raw_dir.iterdir() if f.suffix.lower() in supported_extensions]

    if not files:
        logger.error(f"No supported documents found in {raw_dir}")
        sys.exit(1)

    logger.info(f"Found {len(files)} documents to ingest:")
    for f in files:
        logger.info(f"  → {f.name}")

    # Initialize pipeline
    logger.info("Initializing RAG Pipeline...")
    pipeline = RAGPipeline()

    # Ingest each document
    results = []
    for file_path in files:
        logger.info(f"\nIngesting: {file_path.name}")
        try:
            result = pipeline.ingest_file(str(file_path))
            results.append(result)
            logger.info(f"  ✓ {result['filename']}: {result['chunks']} chunks in {result['time_seconds']}s")
        except Exception as e:
            logger.error(f"  ✗ Failed to ingest {file_path.name}: {e}")
            results.append({"status": "error", "filename": file_path.name, "error": str(e)})

    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("INGESTION SUMMARY")
    logger.info("=" * 50)

    total_chunks = sum(r.get("chunks", 0) for r in results if r.get("status") == "success")
    success_count = sum(1 for r in results if r.get("status") == "success")
    error_count = sum(1 for r in results if r.get("status") == "error")

    logger.info(f"  Documents processed: {len(results)}")
    logger.info(f"  Successful: {success_count}")
    logger.info(f"  Failed: {error_count}")
    logger.info(f"  Total chunks: {total_chunks}")

    stats = pipeline.get_stats()
    logger.info(f"  ChromaDB chunks: {stats['total_chunks']}")
    logger.info(f"  BM25 index size: {stats['bm25_index_size']}")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
