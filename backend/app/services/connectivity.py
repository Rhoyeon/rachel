from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DependencyStatus:
    name: str
    ok: bool
    detail: str


def check_postgres(repo: Any) -> DependencyStatus:
    if not hasattr(repo, "_conn"):
        return DependencyStatus(name="postgres", ok=True, detail="skipped(non-postgres-backend)")
    try:
        with repo._conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return DependencyStatus(name="postgres", ok=True, detail="ok")
    except Exception as exc:  # pragma: no cover - defensive
        return DependencyStatus(name="postgres", ok=False, detail=str(exc))


def check_vector_store(store: Any) -> DependencyStatus:
    if not hasattr(store, "_client"):
        return DependencyStatus(name="qdrant", ok=True, detail="skipped(non-qdrant-backend)")
    try:
        client = store._client()
        client.get_collections()
        return DependencyStatus(name="qdrant", ok=True, detail="ok")
    except Exception as exc:  # pragma: no cover - defensive
        return DependencyStatus(name="qdrant", ok=False, detail=str(exc))
