from __future__ import annotations

import os
from typing import List, Optional
from uuid import uuid4

from app.services.repository import ChunkRepository, ChunkStoredRecord, DocumentRecord, DocumentRepository


class PostgresDocumentRepository(DocumentRepository):
    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn or os.getenv("RACHEL_POSTGRES_DSN", "postgresql://rachel:rachel@localhost:5432/rachel")

    def _conn(self):
        import psycopg

        return psycopg.connect(self.dsn)

    def create(self, title: str, doc_type: str, content: str) -> DocumentRecord:
        doc = DocumentRecord(id=str(uuid4()), title=title, doc_type=doc_type, content=content)
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO documents(id, title, doc_type, content, status) VALUES (%s, %s, %s, %s, %s)",
                    (doc.id, doc.title, doc.doc_type, doc.content, doc.status),
                )
        return doc

    def list(self) -> List[DocumentRecord]:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, title, doc_type, content, status FROM documents")
                rows = cur.fetchall()
        return [DocumentRecord(*row) for row in rows]

    def get(self, document_id: str) -> Optional[DocumentRecord]:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, title, doc_type, content, status FROM documents WHERE id = %s",
                    (document_id,),
                )
                row = cur.fetchone()
        return DocumentRecord(*row) if row else None


class PostgresChunkRepository(ChunkRepository):
    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn or os.getenv("RACHEL_POSTGRES_DSN", "postgresql://rachel:rachel@localhost:5432/rachel")

    def _conn(self):
        import psycopg

        return psycopg.connect(self.dsn)

    def save_for_document(self, document_id: str, chunks: List[str]) -> int:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM chunks WHERE document_id = %s", (document_id,))
                cur.executemany(
                    "INSERT INTO chunks(document_id, chunk_index, chunk_text) VALUES (%s, %s, %s)",
                    [(document_id, i, t) for i, t in enumerate(chunks)],
                )
        return len(chunks)

    def list_for_document(self, document_id: str) -> List[ChunkStoredRecord]:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT document_id, chunk_index, chunk_text FROM chunks WHERE document_id = %s ORDER BY chunk_index",
                    (document_id,),
                )
                rows = cur.fetchall()
        return [ChunkStoredRecord(document_id=r[0], chunk_index=r[1], text=r[2]) for r in rows]
