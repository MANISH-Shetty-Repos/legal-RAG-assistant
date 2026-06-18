"""
Unit Tests for Retrieval Module (BM25 and Vector Store)
"""

from src.retrieval.bm25_retriever import BM25Retriever


def test_bm25_retriever():
    """Test indexing and query retrieval with BM25."""
    retriever = BM25Retriever()

    chunks = [
        {
            "id": "c1",
            "text": "The fee for RTI application is ten rupees.",
            "metadata": {"filename": "rti.txt"},
        },
        {
            "id": "c2",
            "text": "Consumer Rights protection Act is active in India.",
            "metadata": {"filename": "consumer.txt"},
        },
        {
            "id": "c3",
            "text": "Fundamental rights include freedom of speech under Article 19.",
            "metadata": {"filename": "constitution.txt"},
        },
    ]

    retriever.build_index(chunks)

    assert retriever.index_size == 3

    # Test exact word query
    res = retriever.query("RTI fee", top_k=1)
    assert len(res) == 1
    assert res[0]["id"] == "c1"

    # Test another query
    res = retriever.query("freedom of speech", top_k=1)
    assert len(res) == 1
    assert res[0]["id"] == "c3"

    # Test query with no matching keywords
    res = retriever.query("unrelated keywords here", top_k=5)
    assert len(res) == 0


def test_bm25_retriever_permissions():
    """Test document visibility permissions filtering in BM25."""
    retriever = BM25Retriever()

    chunks = [
        {
            "id": "c1",
            "text": "The fee for RTI application is ten rupees",
            "metadata": {"filename": "rti.txt", "uploaded_by_id": 0},  # public
        },
        {
            "id": "c2",
            "text": "User one private file content details",
            "metadata": {"filename": "user1.txt", "uploaded_by_id": 10},  # user 10
        },
        {
            "id": "c3",
            "text": "User two private file content details",
            "metadata": {"filename": "user2.txt", "uploaded_by_id": 20},  # user 20
        },
    ]

    retriever.build_index(chunks)

    # 1. Admin should see all matching files
    res = retriever.query("details", top_k=5, user_id=10, is_admin=True)
    assert len(res) == 2
    assert {r["id"] for r in res} == {"c2", "c3"}

    # 2. Guest/Anonymous user should only see public files
    res = retriever.query("details", top_k=5, user_id=None, is_admin=False)
    assert len(res) == 0

    # 3. User 10 should see public files + user 10 files
    res = retriever.query("rupees details", top_k=5, user_id=10, is_admin=False)
    assert len(res) == 2
    assert {r["id"] for r in res} == {"c1", "c2"}

    # 4. User 20 should see public files + user 20 files
    res = retriever.query("rupees details", top_k=5, user_id=20, is_admin=False)
    assert len(res) == 2
    assert {r["id"] for r in res} == {"c1", "c3"}
