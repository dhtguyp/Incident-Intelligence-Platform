from pathlib import Path

from app.ingestion.document_loader import KnowledgeDocument, chunk_document, load_documents


def test_load_documents_reads_frontmatter_and_source():
    documents = load_documents(Path(__file__).resolve().parents[1] / "knowledge")
    checkout_runbook = next(document for document in documents if document.document_id == "runbook-connection-pool")
    assert checkout_runbook.document_type == "runbook"
    assert checkout_runbook.service == "postgres-primary"
    assert checkout_runbook.source == "runbooks/connection_pool_exhaustion.md"


def test_chunking_is_repeatable_and_preserves_content():
    document = KnowledgeDocument("test", "runbook", "checkout-api", None, "test.md", "one two three four five six")
    chunks = chunk_document(document, chunk_size=12, overlap=4)
    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))
    assert chunks[0].content == "one two"
    assert "six" in chunks[-1].content
