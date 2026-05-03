from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.services.chunking import fixed_chunk
from app.services.repository import DocumentRecord


@dataclass
class ChunkRecord:
    chunk_index: int
    text: str


def build_chunks_for_document(document: DocumentRecord, size: int = 200, overlap: int = 20) -> List[ChunkRecord]:
    chunks = fixed_chunk(document.content, size=size, overlap=overlap)
    return [ChunkRecord(chunk_index=i, text=c) for i, c in enumerate(chunks)]
