from types import SimpleNamespace

from app.models.search_schemas import SearchRequest
from app.retrieval.semantic_search import SemanticRetrievalService


class FakeEmbeddingClient:
    def embed(self, text: str, *, task_type: str) -> list[float]:
        assert task_type == "retrieval_query"
        return [0.1] * 768


class FakeQdrantClient:
    def collection_exists(self, name: str) -> bool:
        assert name == "operational_knowledge"
        return True

    def query_points(self, **kwargs):
        self.query = kwargs
        return SimpleNamespace(points=[SimpleNamespace(
            id="point-1",
            payload={
                "content": "Requests wait when all database connections are busy.",
                "document_id": "runbook-db-pool",
                "document_type": "runbook",
                "service": "postgres-primary",
                "timestamp": "2026-08-01T09:00:00Z",
                "source": "runbooks/connection_pool_exhaustion.md",
                "chunk_index": 0,
            },
            score=0.91,
        )])


def test_search_normalizes_results_and_applies_metadata_filters():
    qdrant = FakeQdrantClient()
    service = SemanticRetrievalService(qdrant, FakeEmbeddingClient())

    results = service.search(
        "requests waiting for a free database connection",
        service="postgres-primary",
        document_type="runbook",
        limit=3,
    )

    assert results[0]["id"] == "point-1"
    assert results[0]["score"] == 0.91
    assert results[0]["source"] == "runbooks/connection_pool_exhaustion.md"
    assert qdrant.query["limit"] == 3
    assert qdrant.query["query_filter"].must[0].key == "service"
    assert qdrant.query["query_filter"].must[1].key == "document_type"


def test_search_request_bounds_limit_and_validates_query():
    assert SearchRequest(query="database pool", limit=20).limit == 20

    try:
        SearchRequest(query="x", limit=21)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid short query and excessive limit must be rejected")


def test_search_returns_empty_when_collection_is_missing():
    class EmptyQdrantClient:
        def collection_exists(self, name: str) -> bool:
            return False

    service = SemanticRetrievalService(EmptyQdrantClient(), FakeEmbeddingClient())
    assert service.search("database connections") == []
