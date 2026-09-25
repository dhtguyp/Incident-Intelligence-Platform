"""Semantic search over Qdrant-backed operational knowledge."""
from __future__ import annotations

import os
from typing import Any

from qdrant_client import QdrantClient, models

from app.embeddings.client import EmbeddingClient, GeminiEmbeddingClient
from app.ingestion.index_documents import COLLECTION_NAME, VECTOR_SIZE


class SemanticRetrievalService:
    def __init__(
        self,
        client: QdrantClient | None = None,
        embedding_client: EmbeddingClient | None = None,
    ) -> None:
        self.client = client or QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
        self.embedding_client = embedding_client or GeminiEmbeddingClient()

    @staticmethod
    def build_filter(service: str | None, document_type: str | None) -> models.Filter | None:
        conditions: list[models.FieldCondition] = []
        if service:
            conditions.append(models.FieldCondition(key="service", match=models.MatchValue(value=service)))
        if document_type:
            conditions.append(models.FieldCondition(key="document_type", match=models.MatchValue(value=document_type)))
        return models.Filter(must=conditions) if conditions else None

    def search(
        self,
        query: str,
        *,
        service: str | None = None,
        document_type: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        if not self.client.collection_exists(COLLECTION_NAME):
            return []

        vector = self.embedding_client.embed(query, task_type="retrieval_query")
        if len(vector) != VECTOR_SIZE:
            raise ValueError(f"Query embedding has {len(vector)} dimensions; expected {VECTOR_SIZE}.")

        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            query_filter=self.build_filter(service, document_type),
            limit=limit,
            with_payload=True,
        ).points

        evidence: list[dict[str, Any]] = []
        for point in results:
            payload = point.payload or {}
            evidence.append({
                "id": str(point.id),
                "content": payload.get("content", ""),
                "document_id": payload.get("document_id"),
                "document_type": payload.get("document_type"),
                "service": payload.get("service"),
                "timestamp": payload.get("timestamp"),
                "source": payload.get("source"),
                "chunk_index": payload.get("chunk_index"),
                "score": point.score,
            })
        return evidence
