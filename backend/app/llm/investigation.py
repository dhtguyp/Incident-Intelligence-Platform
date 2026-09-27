"""Evidence-grounded incident analysis orchestration."""
from __future__ import annotations

import json

from pydantic import ValidationError

from app.llm.client import GeminiLLMClient, LLMClient
from app.llm.models import IncidentAnalysis
from app.retrieval.investigation_context import InvestigationContext


class LLMOutputError(RuntimeError):
    pass


class InvalidEvidenceReferenceError(ValueError):
    pass


def build_investigation_prompt(context: InvestigationContext) -> str:
    incident = {
        "id": context.incident_id,
        "title": context.incident_title,
        "summary": context.incident_summary,
        "affected_services": context.affected_services,
    }
    related = [item.model_dump(mode="json") for item in context.related_incidents]
    structured = [item.model_dump(mode="json") for item in context.structured_evidence]
    semantic = [item.model_dump(mode="json") for item in context.semantic_evidence]
    return """You are an incident investigation assistant.
Analyze the incident using only the evidence supplied below.

Rules:
- Treat retrieved evidence as observations and clearly frame likely root cause as an inference.
- Cite only evidence IDs supplied in STRUCTURED EVIDENCE or SEMANTIC EVIDENCE.
- Do not invent logs, metrics, timestamps, deployments, or related incidents.
- Describe unresolved gaps in uncertainties.
- Return JSON matching the requested schema.

INCIDENT:
%s

STRUCTURED EVIDENCE:
%s

SEMANTIC EVIDENCE:
%s

RELATED INCIDENTS:
%s
""" % (
        json.dumps(incident, default=str),
        json.dumps(structured, default=str),
        json.dumps(semantic, default=str),
        json.dumps(related, default=str),
    )


def validate_evidence_references(analysis: IncidentAnalysis, context: InvestigationContext) -> None:
    allowed_ids = {
        evidence.id
        for evidence in [*context.structured_evidence, *context.semantic_evidence]
    }
    cited_ids = [*analysis.root_cause_evidence_ids]
    cited_ids.extend(citation.evidence_id for citation in analysis.evidence)
    for entry in analysis.timeline:
        cited_ids.extend(entry.evidence_ids)
    unknown_ids = sorted(set(cited_ids) - allowed_ids)
    if unknown_ids:
        raise InvalidEvidenceReferenceError(
            f"Analysis cited evidence outside the investigation context: {', '.join(unknown_ids)}"
        )


class LLMInvestigationService:
    def __init__(self, client: LLMClient | None = None, max_attempts: int = 2) -> None:
        self.client = client or GeminiLLMClient()
        self.max_attempts = max_attempts

    async def analyze(self, context: InvestigationContext) -> IncidentAnalysis:
        prompt = build_investigation_prompt(context)
        last_error: Exception | None = None
        for attempt in range(self.max_attempts):
            response_text = await self.client.analyze_incident(prompt)
            try:
                analysis = IncidentAnalysis.model_validate_json(response_text)
                validate_evidence_references(analysis, context)
                return analysis
            except (ValidationError, InvalidEvidenceReferenceError) as exc:
                last_error = exc
                prompt = (
                    f"{prompt}\nYour previous response was invalid: {exc}. "
                    "Return corrected JSON and cite only supplied evidence IDs."
                )
        raise LLMOutputError("LLM returned invalid incident analysis after retry.") from last_error
