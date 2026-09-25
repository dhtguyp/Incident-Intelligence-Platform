"""Load markdown knowledge documents and split them into retrieval-sized chunks."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KnowledgeDocument:
    document_id: str
    document_type: str
    service: str | None
    timestamp: str | None
    source: str
    content: str


@dataclass(frozen=True)
class DocumentChunk:
    document: KnowledgeDocument
    chunk_index: int
    content: str


def _parse_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    if not raw.startswith("---\n"):
        return {}, raw.strip()
    _, header, body = raw.split("---\n", 2)
    metadata = {
        key.strip(): value.strip()
        for line in header.splitlines()
        if ":" in line
        for key, value in [line.split(":", 1)]
    }
    return metadata, body.strip()


def load_documents(root: Path) -> list[KnowledgeDocument]:
    documents: list[KnowledgeDocument] = []
    for path in sorted(root.glob("*/*.md")):
        metadata, content = _parse_frontmatter(path.read_text(encoding="utf-8"))
        documents.append(KnowledgeDocument(
            document_id=metadata.get("document_id", path.stem),
            document_type=metadata.get("document_type", path.parent.name.rstrip("s")),
            service=metadata.get("service") or None,
            timestamp=metadata.get("timestamp") or None,
            source=str(path.relative_to(root)),
            content=content,
        ))
    return documents


def chunk_document(document: KnowledgeDocument, *, chunk_size: int = 900, overlap: int = 150) -> list[DocumentChunk]:
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")
    words = document.content.split()
    chunks: list[DocumentChunk] = []
    current: list[str] = []
    start = 0
    while start < len(words):
        current = []
        length = 0
        end = start
        while end < len(words):
            next_length = length + len(words[end]) + (1 if current else 0)
            if current and next_length > chunk_size:
                break
            current.append(words[end])
            length = next_length
            end += 1
        chunks.append(DocumentChunk(document=document, chunk_index=len(chunks), content=" ".join(current)))
        if end == len(words):
            break
        retained = 0
        next_start = end
        while next_start > start and retained < overlap:
            next_start -= 1
            retained += len(words[next_start]) + 1
        start = next_start
    return chunks
