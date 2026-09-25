from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import Base, SessionLocal
from app.models.models import Service, Incident, Deployment, Event, MetricSnapshot

def seed_database(db: Session):
    # Check if database is already seeded
    if db.query(Service).first():
        return

    # 1. Create Services
    services = [
        Service(id="checkout-api", name="Checkout API", description="Handles user cart checkout transactions", owner_team="Checkout Engineering"),
        Service(id="payments-api", name="Payments API", description="Processes credit card and gateway payments", owner_team="Payments Team"),
        Service(id="inventory-api", name="Inventory API", description="Tracks product stock levels", owner_team="Fulfillment Team"),
        Service(id="user-api", name="User API", description="User authentication and profile management", owner_team="Core Platform"),
        Service(id="postgres-primary", name="PostgreSQL Primary Database", description="Main relational database cluster", owner_team="Database Infrastructure"),
        Service(id="redis-cache", name="Redis Cache", description="In-memory cache for session & product data", owner_team="Database Infrastructure"),
        Service(id="notification-service", name="Notification Service", description="Sends emails and push notifications", owner_team="Growth & Engagement")
    ]
    db.add_all(services)
    db.commit()

    # Map services for convenience
    svc_map = {s.id: db.query(Service).filter(Service.id == s.id).first() for s in services}

    # 2. Create Incidents
    # INC-1042 (The primary demo incident)
    inc_1042 = Incident(
        id="INC-1042",
        title="Checkout API elevated latency and HTTP 500 spikes",
        status="INVESTIGATING",
        severity="SEV-2",
        started_at=datetime(2026, 9, 20, 14, 35),
        summary="Checkout API error rates spiked to 12% and P99 latency exceeded 4500ms following a database connection pool depletion."
    )
    inc_1042.affected_services = [svc_map["checkout-api"], svc_map["payments-api"], svc_map["postgres-primary"]]

    inc_1017 = Incident(
        id="INC-1017",
        title="Historical: Postgres connection leak during peak sale",
        status="RESOLVED",
        severity="SEV-1",
        started_at=datetime(2026, 8, 10, 10, 15),
        resolved_at=datetime(2026, 8, 10, 11, 45),
        summary="Unclosed DB sessions in background tasks caused max connection limit exhaustion on postgres-primary."
    )
    inc_1017.affected_services = [svc_map["postgres-primary"], svc_map["user-api"]]

    inc_1039 = Incident(
        id="INC-1039",
        title="Redis Cache node memory pressure",
        status="RESOLVED",
        severity="SEV-3",
        started_at=datetime(2026, 9, 15, 8, 0),
        resolved_at=datetime(2026, 9, 15, 8, 40),
        summary="Cache eviction policy failure led to Redis OOM restarts."
    )
    inc_1039.affected_services = [svc_map["redis-cache"]]

    db.add_all([inc_1042, inc_1017, inc_1039])
    db.commit()

    # 3. Create Deployments
    deployments = [
        Deployment(
            id="dep-101",
            service_id="checkout-api",
            version="v1.8.2",
            deployed_at=datetime(2026, 9, 20, 14, 25),
            deployed_by="alex.sre",
            commit_hash="a1b2c3d",
            description="Deployment v1.8.2 modifies database transaction handling and connection pool settings"
        ),
        Deployment(
            id="dep-100",
            service_id="payments-api",
            version="v2.4.0",
            deployed_at=datetime(2026, 9, 20, 12, 00),
            deployed_by="sarah.dev",
            commit_hash="e5f6g7h",
            description="Upgrade payment gateway SDK to latest major version"
        ),
        Deployment(
            id="dep-099",
            service_id="user-api",
            version="v3.1.0",
            deployed_at=datetime(2026, 9, 19, 16, 30),
            deployed_by="ci-cd-bot",
            commit_hash="890123a",
            description="Routine security patch updates"
        )
    ]
    db.add_all(deployments)

    # 4. Create Events for INC-1042 Causal Chain
    events = [
        Event(
            id="evt-201",
            incident_id="INC-1042",
            service_id="checkout-api",
            event_type="deployment",
            timestamp=datetime(2026, 9, 20, 14, 25),
            description="checkout-api version v1.8.2 deployed to production",
            severity="INFO"
        ),
        Event(
            id="evt-202",
            incident_id="INC-1042",
            service_id="postgres-primary",
            event_type="database_connection_usage_rise",
            timestamp=datetime(2026, 9, 20, 14, 27),
            description="PostgreSQL active connections rose from 45 to 190 (pool warning threshold)",
            severity="WARNING"
        ),
        Event(
            id="evt-203",
            incident_id="INC-1042",
            service_id="postgres-primary",
            event_type="database_connection_exhaustion",
            timestamp=datetime(2026, 9, 20, 14, 31),
            description="PostgreSQL reached maximum connection limit (200/200). New requests queuing.",
            severity="CRITICAL"
        ),
        Event(
            id="evt-204",
            incident_id="INC-1042",
            service_id="checkout-api",
            event_type="latency_spike",
            timestamp=datetime(2026, 9, 20, 14, 32),
            description="checkout-api P99 latency increased to 4800ms due to DB connection acquisition timeouts",
            severity="ERROR"
        ),
        Event(
            id="evt-205",
            incident_id="INC-1042",
            service_id="checkout-api",
            event_type="error_rate_spike",
            timestamp=datetime(2026, 9, 20, 14, 33),
            description="HTTP 500 error rate exceeded 10% on /checkout/process route",
            severity="CRITICAL"
        ),
        Event(
            id="evt-206",
            incident_id="INC-1042",
            service_id="checkout-api",
            event_type="incident_declared",
            timestamp=datetime(2026, 9, 20, 14, 35),
            description="PagerDuty alert triggered. Incident INC-1042 declared SEV-2.",
            severity="CRITICAL"
        )
    ]
    db.add_all(events)

    # 5. Metric Snapshots
    metrics = [
        MetricSnapshot(service_id="checkout-api", timestamp=datetime(2026, 9, 20, 14, 20), metric_name="latency_p99", value=120.0, unit="ms"),
        MetricSnapshot(service_id="checkout-api", timestamp=datetime(2026, 9, 20, 14, 32), metric_name="latency_p99", value=4800.0, unit="ms"),
        MetricSnapshot(service_id="checkout-api", timestamp=datetime(2026, 9, 20, 14, 33), metric_name="error_rate", value=12.4, unit="percent"),
        MetricSnapshot(service_id="postgres-primary", timestamp=datetime(2026, 9, 20, 14, 25), metric_name="active_connections", value=45.0, unit="count"),
        MetricSnapshot(service_id="postgres-primary", timestamp=datetime(2026, 9, 20, 14, 31), metric_name="active_connections", value=200.0, unit="count"),
    ]
    db.add_all(metrics)

    # Additional incidents provide realistic retrieval noise and historical context.
    # Their timestamps and symptoms are intentionally varied, while INC-1042 remains
    # the deterministic end-to-end demonstration scenario.
    additional_incidents = [
        ("INC-1018", "Payments gateway timeout increase", "payments-api", "SEV-2"),
        ("INC-1019", "Inventory synchronization backlog", "inventory-api", "SEV-3"),
        ("INC-1020", "User session authentication failures", "user-api", "SEV-2"),
        ("INC-1021", "Notification delivery queue delay", "notification-service", "SEV-3"),
        ("INC-1022", "Redis cache failover instability", "redis-cache", "SEV-2"),
        ("INC-1023", "Checkout promotion traffic saturation", "checkout-api", "SEV-3"),
        ("INC-1024", "PostgreSQL replication lag", "postgres-primary", "SEV-2"),
    ]
    for offset, (incident_id, title, service_id, severity) in enumerate(additional_incidents, start=1):
        started_at = datetime(2026, 9, 1 + offset, 9, 0)
        incident = Incident(
            id=incident_id,
            title=title,
            status="RESOLVED",
            severity=severity,
            started_at=started_at,
            resolved_at=started_at + timedelta(minutes=45),
            summary=f"Synthetic resolved incident affecting {service_id}.",
        )
        incident.affected_services = [svc_map[service_id]]
        db.add(incident)
        db.add(Deployment(
            id=f"dep-{101 + offset}",
            service_id=service_id,
            version=f"v1.{offset}.0",
            deployed_at=started_at - timedelta(minutes=20),
            deployed_by="ci-cd-bot",
            commit_hash=f"seed{offset:03d}",
            description=f"Routine deployment for {service_id}.",
        ))
        for event_offset, (event_type, description, event_severity) in enumerate([
            ("deployment", "Routine deployment completed.", "INFO"),
            ("latency_spike", "Service latency crossed its warning threshold.", "WARNING"),
            ("error_rate_spike", "Error rate increased during the incident.", "ERROR"),
            ("incident_resolved", "Mitigation completed and service recovered.", "INFO"),
        ]):
            db.add(Event(
                id=f"evt-{206 + offset * 10 + event_offset}",
                incident_id=incident_id,
                service_id=service_id,
                event_type=event_type,
                timestamp=started_at + timedelta(minutes=event_offset * 10 - 10),
                description=description,
                severity=event_severity,
            ))
        for metric_offset, value in enumerate((120.0, 950.0, 180.0)):
            db.add(MetricSnapshot(
                service_id=service_id,
                timestamp=started_at + timedelta(minutes=metric_offset * 10),
                metric_name="latency_p99",
                value=value,
                unit="ms",
            ))

    db.commit()

def init_db():
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
