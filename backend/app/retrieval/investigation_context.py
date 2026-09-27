"""Shared evidence contracts for hybrid incident investigation retrieval."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    id: str
    source_type: str
    source: Literal["sqlite", "qdrant"]
    content: str
    timestamp: datetime | None = None
    service: str | None = None
    relevance: float | None = None
    metadata: dict[str, str | int | float | None] = Field(default_factory=dict)


class RelatedIncident(BaseModel):
    id: str
    title: str
    severity: str
    started_at: datetime
    summary: str | None = None
    affected_services: list[str]


class InvestigationContext(BaseModel):
    incident_id: str
    incident_title: str
    incident_summary: str | None = None
    affected_services: list[str]
    structured_evidence: list[Evidence]
    semantic_evidence: list[Evidence]
    related_incidents: list[RelatedIncident]
