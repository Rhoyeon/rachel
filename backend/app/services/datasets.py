from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Protocol
from uuid import uuid4
import json
import os
import sqlite3


@dataclass
class EvalDataset:
    dataset_id: str
    name: str
    items: list[dict]


class EvalDatasetStore(Protocol):
    def create(self, name: str, items: list[dict], dataset_id: str | None = None) -> EvalDataset: ...
    def list(self) -> List[dict]: ...


class InMemoryEvalDatasetStore:
    def __init__(self) -> None:
        self._items: Dict[str, EvalDataset] = {}

    def create(self, name: str, items: list[dict], dataset_id: str | None = None) -> EvalDataset:
        ds = EvalDataset(dataset_id=dataset_id or str(uuid4()), name=name, items=items)
        self._items[ds.dataset_id] = ds
        return ds

    def list(self) -> List[dict]:
        return [asdict(v) for v in self._items.values()]


class SQLiteEvalDatasetStore:
    def __init__(self, path: str | None = None) -> None:
        self.path = path or os.getenv("RACHEL_SQLITE_PATH", "rachel.db")
        self._ensure_table()

    def _conn(self):
        return sqlite3.connect(self.path)

    def _ensure_table(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS evaluation_datasets (
                    dataset_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    items_json TEXT NOT NULL
                )
                """
            )

    def create(self, name: str, items: list[dict], dataset_id: str | None = None) -> EvalDataset:
        ds = EvalDataset(dataset_id=dataset_id or str(uuid4()), name=name, items=items)
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO evaluation_datasets(dataset_id, name, items_json) VALUES (?, ?, ?)",
                (ds.dataset_id, ds.name, json.dumps(ds.items, ensure_ascii=False)),
            )
        return ds

    def list(self) -> List[dict]:
        with self._conn() as conn:
            rows = conn.execute("SELECT dataset_id, name, items_json FROM evaluation_datasets ORDER BY rowid DESC").fetchall()
        return [{"dataset_id": r[0], "name": r[1], "items": json.loads(r[2] or "[]")} for r in rows]


class PostgresEvalDatasetStore:
    def __init__(self, dsn: Optional[str] = None) -> None:
        self.dsn = dsn or os.getenv("RACHEL_POSTGRES_DSN", "postgresql://rachel:rachel@localhost:5432/rachel")
        self._initialized = False

    def _conn(self):
        import psycopg

        return psycopg.connect(self.dsn)

    def _ensure_table(self) -> None:
        if self._initialized:
            return
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS evaluation_datasets (
                        dataset_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        items_json TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
        self._initialized = True

    def create(self, name: str, items: list[dict], dataset_id: str | None = None) -> EvalDataset:
        self._ensure_table()
        ds = EvalDataset(dataset_id=dataset_id or str(uuid4()), name=name, items=items)
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO evaluation_datasets(dataset_id, name, items_json)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (dataset_id) DO UPDATE SET
                      name = EXCLUDED.name,
                      items_json = EXCLUDED.items_json
                    """,
                    (ds.dataset_id, ds.name, json.dumps(ds.items, ensure_ascii=False)),
                )
        return ds

    def list(self) -> List[dict]:
        self._ensure_table()
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT dataset_id, name, items_json FROM evaluation_datasets ORDER BY created_at DESC")
                rows = cur.fetchall()
        return [{"dataset_id": r[0], "name": r[1], "items": json.loads(r[2] or "[]")} for r in rows]
