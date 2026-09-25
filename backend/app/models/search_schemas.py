from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2000)
    service: str | None = Field(default=None, min_length=1, max_length=100)
    document_type: Literal["runbook", "postmortem", "service_doc", "log"] | None = None
    limit: int = Field(default=5, ge=1, le=20)


class SearchEvidence(BaseModel):
    id: str
    content: str
    document_id: str | None = None
    document_type: str | None = None
    service: str | None = None
    timestamp: str | None = None
    source: str | None = None
    chunk_index: int | None = None
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchEvidence]

    model_config = ConfigDict(from_attributes=True)
