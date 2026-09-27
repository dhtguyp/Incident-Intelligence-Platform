"""Build evidence-grounded context for an incident investigation."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.incident_repository import IncidentRepository
from app.retrieval.investigation_context import Evidence, InvestigationContext, RelatedIncident
from app.retrieval.semantic_search import SemanticRetrievalService


class IncidentNotFoundError(ValueError):
    pass


class InvestigationRetrievalService:
    def __init__(
        self,
        db: Session,
        semantic_retrieval: SemanticRetrievalService | None = None,
    ) -> None:
        self.db = db
        self.semantic_retrieval = semantic_retrieval or SemanticRetrievalService()

    def build_context(self, incident_id: str) -> InvestigationContext:
        incident = IncidentRepository.get_incident_by_id(self.db, incident_id)
        if incident is None:
            raise IncidentNotFoundError(f"Incident '{incident_id}' not found")

        affected_services = [service.id for service in incident.affected_services]
        timeline = IncidentRepository.get_incident_timeline(self.db, incident.id)
        structured_evidence = [self._incident_evidence(incident)]
        structured_evidence.extend(self._timeline_evidence(item) for item in timeline)
        structured_evidence = self._deduplicate(structured_evidence)

        related_incidents = [
            RelatedIncident(
                id=item.id,
                title=item.title,
                severity=item.severity,
                started_at=item.started_at,
                summary=item.summary,
                affected_services=[service.id for service in item.affected_services],
            )
            for item in IncidentRepository.get_nearby_incidents(self.db, incident)
        ]
        semantic_evidence = self._semantic_evidence(
            incident.title,
            incident.summary,
            affected_services,
            [item.title for item in timeline if item.type == "event"],
        )

        return InvestigationContext(
            incident_id=incident.id,
            incident_title=incident.title,
            incident_summary=incident.summary,
            affected_services=affected_services,
            structured_evidence=sorted(
                structured_evidence,
                key=lambda evidence: evidence.timestamp or incident.started_at,
            ),
            semantic_evidence=semantic_evidence,
            related_incidents=related_incidents,
        )

    @staticmethod
    def _incident_evidence(incident) -> Evidence:
        services = ", ".join(service.id for service in incident.affected_services)
        return Evidence(
            id=f"incident-{incident.id}",
            source_type="incident",
            source="sqlite",
            timestamp=incident.started_at,
            content=f"{incident.id}: {incident.title}. {incident.summary or ''}".strip(),
            metadata={"severity": incident.severity, "status": incident.status, "affected_services": services},
        )

    @staticmethod
    def _timeline_evidence(item) -> Evidence:
        metadata = {"title": item.title, "severity": item.severity}
        if item.details:
            metadata.update(item.details)
        return Evidence(
            id=item.id,
            source_type=item.type,
            source="sqlite",
            timestamp=item.timestamp,
            service=item.service_id,
            content=item.description,
            metadata=metadata,
        )

    def _semantic_evidence(
        self,
        title: str,
        summary: str | None,
        affected_services: list[str],
        event_titles: list[str],
    ) -> list[Evidence]:
        details = " ".join([title, summary or "", *affected_services, *event_titles])
        queries: list[tuple[str, str | None]] = [(details, None)]
        queries.extend((details, service) for service in affected_services)

        evidence: list[Evidence] = []
        for query, service in queries:
            for result in self.semantic_retrieval.search(query, service=service, limit=4):
                evidence.append(Evidence(
                    id=result["id"],
                    source_type=result.get("document_type") or "document",
                    source="qdrant",
                    content=result["content"],
                    timestamp=result.get("timestamp"),
                    service=result.get("service"),
                    relevance=result.get("score"),
                    metadata={
                        "document_id": result.get("document_id"),
                        "source": result.get("source"),
                        "chunk_index": result.get("chunk_index"),
                    },
                ))
        return self._deduplicate(evidence)

    @staticmethod
    def _deduplicate(evidence: list[Evidence]) -> list[Evidence]:
        seen: set[str] = set()
        unique: list[Evidence] = []
        for item in evidence:
            if item.id not in seen:
                seen.add(item.id)
                unique.append(item)
        return unique
