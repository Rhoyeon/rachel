from __future__ import annotations

import os
import sqlite3
from typing import List, Optional
from uuid import uuid4

from app.services.repository import ChunkRepository, ChunkStoredRecord, DocumentRecord, DocumentRepository


class SQLiteDocumentRepository(DocumentRepository):
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path or os.getenv("RACHEL_DB_PATH", "/tmp/rachel.db")
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY,title TEXT NOT NULL,doc_type TEXT NOT NULL,content TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'ready')")

    def create(self, title: str, doc_type: str, content: str) -> DocumentRecord:
        doc = DocumentRecord(id=str(uuid4()), title=title, doc_type=doc_type, content=content)
        with self._conn() as conn:
            conn.execute("INSERT INTO documents(id, title, doc_type, content, status) VALUES (?, ?, ?, ?, ?)",(doc.id, doc.title, doc.doc_type, doc.content, doc.status))
        return doc

    def list(self) -> List[DocumentRecord]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id, title, doc_type, content, status FROM documents").fetchall()
        return [DocumentRecord(*row) for row in rows]

    def get(self, document_id: str) -> Optional[DocumentRecord]:
        with self._conn() as conn:
            row = conn.execute("SELECT id, title, doc_type, content, status FROM documents WHERE id = ?",(document_id,)).fetchone()
        return DocumentRecord(*row) if row else None


class SQLiteChunkRepository(ChunkRepository):
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path or os.getenv("RACHEL_DB_PATH", "/tmp/rachel.db")
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS chunks (document_id TEXT NOT NULL, chunk_index INTEGER NOT NULL, chunk_text TEXT NOT NULL)")

    def save_for_document(self, document_id: str, chunks: List[str]) -> int:
        with self._conn() as conn:
            conn.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
            conn.executemany("INSERT INTO chunks(document_id, chunk_index, chunk_text) VALUES (?, ?, ?)",[(document_id, i, t) for i, t in enumerate(chunks)])
        return len(chunks)

    def list_for_document(self, document_id: str) -> List[ChunkStoredRecord]:
        with self._conn() as conn:
            rows = conn.execute("SELECT document_id, chunk_index, chunk_text FROM chunks WHERE document_id = ? ORDER BY chunk_index", (document_id,)).fetchall()
        return [ChunkStoredRecord(document_id=r[0], chunk_index=r[1], text=r[2]) for r in rows]
