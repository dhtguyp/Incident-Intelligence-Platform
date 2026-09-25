import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.seed import seed_database
from app.repositories.incident_repository import IncidentRepository
from app.models.models import Deployment, Event, MetricSnapshot

# In-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    seed_database(session)
    yield session
    session.close()

def test_get_all_incidents(db_session):
    incidents = IncidentRepository.get_all_incidents(db_session)
    assert len(incidents) >= 3
    inc_ids = [inc.id for inc in incidents]
    assert "INC-1042" in inc_ids
    assert "INC-1017" in inc_ids
    assert len(incidents) >= 10
    assert db_session.query(Deployment).count() >= 10
    assert db_session.query(Event).count() >= 30
    assert db_session.query(MetricSnapshot).count() >= 20

def test_get_incident_by_id(db_session):
    inc = IncidentRepository.get_incident_by_id(db_session, "INC-1042")
    assert inc is not None
    assert inc.title == "Checkout API elevated latency and HTTP 500 spikes"
    assert inc.severity == "SEV-2"
    assert len(inc.affected_services) == 3
    svc_names = [s.name for s in inc.affected_services]
    assert "Checkout API" in svc_names

def test_get_incident_timeline(db_session):
    timeline = IncidentRepository.get_incident_timeline(db_session, "INC-1042")
    assert len(timeline) > 0
    # Check that events and deployments are included chronologically
    types = [item.type for item in timeline]
    assert "event" in types
    assert "deployment" in types
    assert "metric" in types
    # Check chronological sorting
    for i in range(len(timeline) - 1):
        assert timeline[i].timestamp <= timeline[i + 1].timestamp

def test_seeding_is_idempotent_for_the_supplied_session(db_session):
    seed_database(db_session)
    incidents = IncidentRepository.get_all_incidents(db_session)
    assert [incident.id for incident in incidents].count("INC-1042") == 1
