from __future__ import annotations

from typing import Dict, List, Optional
from uuid import uuid4

from app.services.repository import ChunkRepository, ChunkStoredRecord, DocumentRecord, DocumentRepository


class InMemoryDocumentRepository(DocumentRepository):
    def __init__(self) -> None:
        self._documents: Dict[str, DocumentRecord] = {}

    def create(self, title: str, doc_type: str, content: str) -> DocumentRecord:
        doc = DocumentRecord(id=str(uuid4()), title=title, doc_type=doc_type, content=content)
        self._documents[doc.id] = doc
        return doc

    def list(self) -> List[DocumentRecord]:
        return list(self._documents.values())

    def get(self, document_id: str) -> Optional[DocumentRecord]:
        return self._documents.get(document_id)


class InMemoryChunkRepository(ChunkRepository):
    def __init__(self) -> None:
        self._chunks: Dict[str, List[ChunkStoredRecord]] = {}

    def save_for_document(self, document_id: str, chunks: List[str]) -> int:
        records = [ChunkStoredRecord(document_id=document_id, chunk_index=i, text=t) for i, t in enumerate(chunks)]
        self._chunks[document_id] = records
        return len(records)

    def list_for_document(self, document_id: str) -> List[ChunkStoredRecord]:
        return self._chunks.get(document_id, [])
