from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Optional, List


@dataclass
class DocumentRecord:
    id: str
    title: str
    doc_type: str
    content: str
    status: str = "ready"


@dataclass
class ChunkStoredRecord:
    document_id: str
    chunk_index: int
    text: str


class DocumentRepository(Protocol):
    def create(self, title: str, doc_type: str, content: str) -> DocumentRecord:
        ...

    def list(self) -> List[DocumentRecord]:
        ...

    def get(self, document_id: str) -> Optional[DocumentRecord]:
        ...


class ChunkRepository(Protocol):
    def save_for_document(self, document_id: str, chunks: List[str]) -> int:
        ...

    def list_for_document(self, document_id: str) -> List[ChunkStoredRecord]:
        ...
