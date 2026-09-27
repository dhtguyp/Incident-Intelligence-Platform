import asyncio

import pytest

from app.llm.investigation import (
    InvalidEvidenceReferenceError,
    LLMInvestigationService,
    build_investigation_prompt,
    validate_evidence_references,
)
from app.llm.models import IncidentAnalysis
from app.retrieval.investigation_context import Evidence, InvestigationContext


def sample_context() -> InvestigationContext:
    return InvestigationContext(
        incident_id="INC-1042",
        incident_title="Checkout API elevated latency",
        incident_summary="Database connections reached capacity.",
        affected_services=["checkout-api", "postgres-primary"],
        structured_evidence=[Evidence(
            id="evt-203",
            source_type="event",
            source="sqlite",
            content="PostgreSQL reached 200 active connections.",
            service="postgres-primary",
        )],
        semantic_evidence=[Evidence(
            id="qdrant-runbook-1",
            source_type="runbook",
            source="qdrant",
            content="Connection exhaustion queues new requests.",
            service="postgres-primary",
            relevance=0.9,
        )],
        related_incidents=[],
    )


def valid_analysis_json(evidence_id: str = "evt-203") -> str:
    return IncidentAnalysis(
        summary="Database connections reached capacity and checkout latency rose.",
        likely_root_cause="The evidence supports a likely connection-pool exhaustion hypothesis.",
        root_cause_evidence_ids=[evidence_id],
        confidence=0.8,
        timeline=[{
            "description": "PostgreSQL connection capacity was reached.",
            "evidence_ids": [evidence_id],
        }],
        evidence=[{"evidence_id": evidence_id, "description": "Connection capacity event."}],
        related_incidents=[],
        uncertainties=["The evidence does not directly identify the leaking code path."],
    ).model_dump_json()


class FakeLLMClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.prompts: list[str] = []

    async def analyze_incident(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


def test_prompt_separates_retrieved_evidence_sections():
    prompt = build_investigation_prompt(sample_context())
    assert "INCIDENT:" in prompt
    assert "STRUCTURED EVIDENCE:" in prompt
    assert "SEMANTIC EVIDENCE:" in prompt
    assert "RELATED INCIDENTS:" in prompt
    assert "evt-203" in prompt
    assert "qdrant-runbook-1" in prompt


def test_validation_rejects_citations_outside_context():
    with pytest.raises(InvalidEvidenceReferenceError, match="unknown-evidence"):
        validate_evidence_references(
            IncidentAnalysis.model_validate_json(valid_analysis_json("unknown-evidence")),
            sample_context(),
        )


def test_service_retries_invalid_output_and_returns_valid_analysis():
    client = FakeLLMClient(["not json", valid_analysis_json()])
    analysis = asyncio.run(LLMInvestigationService(client).analyze(sample_context()))

    assert analysis.confidence == 0.8
    assert len(client.prompts) == 2
    assert "previous response was invalid" in client.prompts[1]
