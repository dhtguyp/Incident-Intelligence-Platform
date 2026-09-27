"""Validated contracts for evidence-backed incident analyses."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AnalysisTimelineEntry(BaseModel):
    timestamp: datetime | None = None
    description: str
    evidence_ids: list[str] = Field(min_length=1)


class EvidenceCitation(BaseModel):
    evidence_id: str
    description: str


class IncidentAnalysis(BaseModel):
    summary: str
    likely_root_cause: str
    root_cause_evidence_ids: list[str] = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    timeline: list[AnalysisTimelineEntry]
    evidence: list[EvidenceCitation]
    related_incidents: list[str]
    uncertainties: list[str]
