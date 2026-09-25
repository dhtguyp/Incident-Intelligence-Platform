from datetime import timedelta
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.models import Incident, Event, Deployment, MetricSnapshot
from app.models.schemas import TimelineItem

class IncidentRepository:

    @staticmethod
    def get_all_incidents(db: Session) -> List[Incident]:
        return db.query(Incident).options(joinedload(Incident.affected_services)).order_by(Incident.started_at.desc()).all()

    @staticmethod
    def get_incident_by_id(db: Session, incident_id: str) -> Optional[Incident]:
        return db.query(Incident).options(joinedload(Incident.affected_services)).filter(Incident.id == incident_id).first()

    @staticmethod
    def get_incident_timeline(db: Session, incident_id: str) -> List[TimelineItem]:
        incident = db.query(Incident).options(joinedload(Incident.affected_services)).filter(Incident.id == incident_id).first()
        if not incident:
            return []

        timeline: List[TimelineItem] = []

        # 1. Direct events associated with this incident or affected services around the incident time window
        affected_service_ids = [s.id for s in incident.affected_services]
        window_start = incident.started_at - timedelta(minutes=60)
        window_end = (incident.resolved_at or incident.started_at) + timedelta(minutes=30)

        # Direct Incident Events
        events = db.query(Event).filter(
            (Event.incident_id == incident_id) | 
            ((Event.service_id.in_(affected_service_ids)) & (Event.timestamp >= window_start) & (Event.timestamp <= window_end))
        ).all()

        for event in events:
            timeline.append(TimelineItem(
                id=str(event.id),
                timestamp=event.timestamp,
                type="event",
                service_id=event.service_id,
                title=f"Event: {event.event_type}",
                description=event.description,
                severity=event.severity
            ))

        # 2. Deployments on affected services during the window
        deployments = db.query(Deployment).filter(
            Deployment.service_id.in_(affected_service_ids),
            Deployment.deployed_at >= window_start,
            Deployment.deployed_at <= window_end
        ).all()

        for dep in deployments:
            timeline.append(TimelineItem(
                id=str(dep.id),
                timestamp=dep.deployed_at,
                type="deployment",
                service_id=dep.service_id,
                title=f"Deployment {dep.version} ({dep.service_id})",
                description=dep.description or f"Deployed {dep.version} by {dep.deployed_by or 'automated workflow'}",
                severity="INFO",
                details={"commit_hash": dep.commit_hash, "version": dep.version}
            ))

        # Metric observations are evidence too: retain their exact value and
        # timestamp for the later investigation pipeline.
        metrics = db.query(MetricSnapshot).filter(
            MetricSnapshot.service_id.in_(affected_service_ids),
            MetricSnapshot.timestamp >= window_start,
            MetricSnapshot.timestamp <= window_end,
        ).all()

        for metric in metrics:
            timeline.append(TimelineItem(
                id=f"metric-{metric.id}",
                timestamp=metric.timestamp,
                type="metric",
                service_id=metric.service_id,
                title=f"Metric: {metric.metric_name}",
                description=(
                    f"{metric.service_id} {metric.metric_name} was "
                    f"{metric.value:g} {metric.unit}"
                ),
                details={
                    "metric_name": metric.metric_name,
                    "value": metric.value,
                    "unit": metric.unit,
                },
            ))

        # Sort combined timeline chronologically
        timeline.sort(key=lambda x: x.timestamp)
        return timeline
