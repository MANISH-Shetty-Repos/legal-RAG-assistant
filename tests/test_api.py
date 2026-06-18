from fastapi.testclient import TestClient
import pytest

from src.api.main import app


@pytest.fixture(scope="module")
def api_client():
    with TestClient(app) as client:
        yield client


def test_health_check(api_client) -> None:
    response = api_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_stats_endpoint(api_client) -> None:
    response = api_client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "total_chunks" in data
    assert "bm25_index_size" in data


def test_query_empty_request(api_client) -> None:
    response = api_client.post("/query", json={"query": ""})
    assert response.status_code == 400
    assert response.json()["detail"] == "Query text must not be empty"
