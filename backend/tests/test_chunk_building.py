from app.services.ingestion import build_chunks_for_document
from app.services.repository import DocumentRecord


def test_build_chunks_for_document() -> None:
    doc = DocumentRecord(id='d1', title='t', doc_type='md', content='a' * 450)
    chunks = build_chunks_for_document(doc, size=100, overlap=10)
    assert len(chunks) >= 4
    assert chunks[0].chunk_index == 0
