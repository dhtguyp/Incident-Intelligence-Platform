"""Repeatable command: python -m app.ingestion.index_documents."""
from __future__ import annotations

import os
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient, models

from app.embeddings.client import GeminiEmbeddingClient
from app.ingestion.document_loader import chunk_document, load_documents

COLLECTION_NAME = "operational_knowledge"
VECTOR_SIZE = 768
KNOWLEDGE_ROOT = Path(os.getenv("KNOWLEDGE_DIR", Path(__file__).resolve().parents[2] / "knowledge"))


def build_payload(chunk) -> dict[str, str | int | None]:
    document = chunk.document
    return {
        "document_id": document.document_id,
        "document_type": document.document_type,
        "service": document.service,
        "timestamp": document.timestamp,
        "source": document.source,
        "chunk_index": chunk.chunk_index,
        "content": chunk.content,
    }


def ensure_collection(client: QdrantClient) -> None:
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE),
        )


def index_documents() -> int:
    documents = load_documents(KNOWLEDGE_ROOT)
    if not documents:
        raise RuntimeError(f"No markdown documents found in {KNOWLEDGE_ROOT}")

    client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
    ensure_collection(client)
    embedding_client = GeminiEmbeddingClient()
    points: list[models.PointStruct] = []

    for document in documents:
        for chunk in chunk_document(document):
            point_id = str(uuid5(NAMESPACE_URL, f"{document.document_id}:{chunk.chunk_index}"))
            points.append(models.PointStruct(
                id=point_id,
                vector=embedding_client.embed(chunk.content, task_type="retrieval_document"),
                payload=build_payload(chunk),
            ))

    client.upsert(collection_name=COLLECTION_NAME, points=points, wait=True)
    return len(points)


if __name__ == "__main__":
    count = index_documents()
    print(f"Indexed {count} chunks into {COLLECTION_NAME}.")
