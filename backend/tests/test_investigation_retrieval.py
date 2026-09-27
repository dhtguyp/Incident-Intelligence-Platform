import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.seed import seed_database
from app.services.investigation_retrieval import (
    IncidentNotFoundError,
    InvestigationRetrievalService,
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    seed_database(session)
    yield session
    session.close()


class FakeSemanticRetrieval:
    def __init__(self):
        self.calls: list[dict[str, object]] = []

    def search(self, query: str, **kwargs):
        self.calls.append({"query": query, **kwargs})
        return [{
            "id": "qdrant-runbook-1",
            "content": "Connection pools queue requests when PostgreSQL has no free connections.",
            "document_id": "runbook-connection-pool",
            "document_type": "runbook",
            "service": "postgres-primary",
            "timestamp": "2026-08-01T09:00:00Z",
            "source": "runbooks/connection_pool_exhaustion.md",
            "chunk_index": 0,
            "score": 0.91,
        }]


def test_build_context_combines_and_deduplicates_evidence(db_session):
    semantic = FakeSemanticRetrieval()
    context = InvestigationRetrievalService(db_session, semantic).build_context("INC-1042")

    assert context.incident_id == "INC-1042"
    assert {"event", "deployment", "metric"}.issubset(
        {item.source_type for item in context.structured_evidence}
    )
    assert any(item.id == "INC-1017" for item in context.related_incidents)
    assert len(context.semantic_evidence) == 1
    assert context.semantic_evidence[0].source == "qdrant"
    assert semantic.calls[0]["service"] is None
    assert "checkout-api" in semantic.calls[0]["query"]
    assert "postgres-primary" in semantic.calls[0]["query"]


def test_build_context_rejects_unknown_incident(db_session):
    with pytest.raises(IncidentNotFoundError, match="INC-404"):
        InvestigationRetrievalService(db_session, FakeSemanticRetrieval()).build_context("INC-404")
