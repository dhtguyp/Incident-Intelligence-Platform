import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.seed import seed_database
from app.llm.models import IncidentAnalysis

TEST_DATABASE_URL = "sqlite://"

@pytest.fixture
def db_session():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    seed_database(session)
    yield session
    session.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_list_incidents_endpoint(client):
    response = client.get("/api/incidents")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    ids = [item["id"] for item in data]
    assert "INC-1042" in ids

def test_get_incident_endpoint(client):
    response = client.get("/api/incidents/INC-1042")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "INC-1042"
    assert data["severity"] == "SEV-2"
    assert "affected_services" in data

def test_get_incident_not_found(client):
    response = client.get("/api/incidents/INC-9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Incident 'INC-9999' not found"

def test_get_incident_timeline_endpoint(client):
    response = client.get("/api/incidents/INC-1042/timeline")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    types = {item["type"] for item in data}
    assert "event" in types or "deployment" in types or "metric" in types

@patch("app.api.incidents.LLMInvestigationService.analyze", new_callable=AsyncMock)
def test_investigate_incident_endpoint(mock_analyze, client):
    # Mock LLM response to avoid calling external Gemini API in API tests
    fake_analysis = IncidentAnalysis(
        summary="Database connection pool exhaustion caused elevated checkout API latency.",
        likely_root_cause="Deployment v1.8.2 introduced unclosed PostgreSQL connections.",
        confidence=0.85,
        root_cause_evidence_ids=["incident-INC-1042"],
        timeline=[{
            "timestamp": "2026-09-20 14:31",
            "description": "Checkout API latency spike detected.",
            "evidence_ids": ["incident-INC-1042"],
        }],
        evidence=[{
            "evidence_id": "incident-INC-1042",
            "description": "INC-1042 incident record.",
        }],
        related_incidents=["INC-1017"],
        uncertainties=["Exact commit author unverified."],
    )
    mock_analyze.return_value = fake_analysis

    response = client.post("/api/incidents/INC-1042/investigate")
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == fake_analysis.summary
    assert data["likely_root_cause"] == fake_analysis.likely_root_cause
    assert data["confidence"] == 0.85
    assert "root_cause_evidence_ids" in data
