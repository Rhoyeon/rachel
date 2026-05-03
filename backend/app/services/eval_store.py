from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import asdict
from typing import Dict, Optional, Protocol

from app.services.evaluation import EvalRun


class EvalRunStore(Protocol):
    def save(self, run: EvalRun) -> None: ...

    def get(self, run_id: str) -> Optional[dict]: ...

    def list(self) -> list[dict]: ...

    def list_metric_rows(self, run_id: str | None = None, metric_name: str | None = None) -> list[dict]: ...


class InMemoryEvalRunStore:
    def __init__(self) -> None:
        self._runs: Dict[str, dict] = {}
        self._metrics_rows: list[dict] = []

    def save(self, run: EvalRun) -> None:
        row = asdict(run)
        self._runs[run.run_id] = row
        self._metrics_rows = [r for r in self._metrics_rows if r["run_id"] != run.run_id]
        for name, value in run.metrics.items():
            if isinstance(value, (int, float)):
                self._metrics_rows.append({"run_id": run.run_id, "metric_name": name, "metric_value": float(value)})

    def get(self, run_id: str) -> Optional[dict]:
        return self._runs.get(run_id)

    def list(self) -> list[dict]:
        return list(self._runs.values())

    def list_metric_rows(self, run_id: str | None = None, metric_name: str | None = None) -> list[dict]:
        rows = self._metrics_rows
        if run_id:
            rows = [r for r in rows if r["run_id"] == run_id]
        if metric_name:
            rows = [r for r in rows if r["metric_name"] == metric_name]
        return list(rows)


class SQLiteEvalRunStore:
    def __init__(self, path: str | None = None) -> None:
        self.path = path or os.getenv("RACHEL_SQLITE_PATH", "rachel.db")
        self._ensure_table()

    def _conn(self):
        return sqlite3.connect(self.path)

    def _ensure_table(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS evaluation_runs (
                    run_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    query_count INTEGER NOT NULL,
                    citation_rate REAL NOT NULL,
                    avg_answer_length REAL NOT NULL,
                    backend TEXT NOT NULL,
                    metrics_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS evaluation_results (
                    run_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    PRIMARY KEY (run_id, metric_name)
                )
                """
            )

    def save(self, run: EvalRun) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO evaluation_runs
                (run_id, name, query_count, citation_rate, avg_answer_length, backend, metrics_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.run_id,
                    run.name,
                    run.query_count,
                    run.citation_rate,
                    run.avg_answer_length,
                    run.backend,
                    json.dumps(run.metrics, ensure_ascii=False),
                ),
            )
            conn.execute("DELETE FROM evaluation_results WHERE run_id = ?", (run.run_id,))
            for metric_name, metric_value in run.metrics.items():
                if isinstance(metric_value, (int, float)):
                    conn.execute(
                        "INSERT INTO evaluation_results(run_id, metric_name, metric_value) VALUES (?, ?, ?)",
                        (run.run_id, metric_name, float(metric_value)),
                    )

    def get(self, run_id: str) -> Optional[dict]:
        with self._conn() as conn:
            row = conn.execute(
                """
                SELECT run_id, name, query_count, citation_rate, avg_answer_length, backend, metrics_json
                FROM evaluation_runs WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()
        if not row:
            return None
        return {
            "run_id": row[0],
            "name": row[1],
            "query_count": row[2],
            "citation_rate": row[3],
            "avg_answer_length": row[4],
            "backend": row[5],
            "metrics": json.loads(row[6] or "{}"),
        }

    def list(self) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT run_id, name, query_count, citation_rate, avg_answer_length, backend, metrics_json
                FROM evaluation_runs ORDER BY rowid DESC
                """
            ).fetchall()
        return [
            {
                "run_id": r[0],
                "name": r[1],
                "query_count": r[2],
                "citation_rate": r[3],
                "avg_answer_length": r[4],
                "backend": r[5],
                "metrics": json.loads(r[6] or "{}"),
            }
            for r in rows
        ]

    def list_metric_rows(self, run_id: str | None = None, metric_name: str | None = None) -> list[dict]:
        query = "SELECT run_id, metric_name, metric_value FROM evaluation_results WHERE 1=1"
        params: list = []
        if run_id:
            query += " AND run_id = ?"
            params.append(run_id)
        if metric_name:
            query += " AND metric_name = ?"
            params.append(metric_name)
        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
        return [{"run_id": r[0], "metric_name": r[1], "metric_value": float(r[2])} for r in rows]


class PostgresEvalRunStore:
    def __init__(self, dsn: str | None = None) -> None:
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
                    CREATE TABLE IF NOT EXISTS evaluation_runs (
                        run_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        query_count INTEGER NOT NULL,
                        citation_rate REAL NOT NULL,
                        avg_answer_length REAL NOT NULL,
                        backend TEXT NOT NULL,
                        metrics_json TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS evaluation_results (
                        run_id TEXT NOT NULL,
                        metric_name TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (run_id, metric_name)
                    )
                    """
                )
        self._initialized = True

    def save(self, run: EvalRun) -> None:
        self._ensure_table()
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO evaluation_runs
                    (run_id, name, query_count, citation_rate, avg_answer_length, backend, metrics_json)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (run_id) DO UPDATE SET
                      name = EXCLUDED.name,
                      query_count = EXCLUDED.query_count,
                      citation_rate = EXCLUDED.citation_rate,
                      avg_answer_length = EXCLUDED.avg_answer_length,
                      backend = EXCLUDED.backend,
                      metrics_json = EXCLUDED.metrics_json
                    """,
                    (
                        run.run_id,
                        run.name,
                        run.query_count,
                        run.citation_rate,
                        run.avg_answer_length,
                        run.backend,
                        json.dumps(run.metrics, ensure_ascii=False),
                    ),
                )
                cur.execute("DELETE FROM evaluation_results WHERE run_id = %s", (run.run_id,))
                rows = [
                    (run.run_id, k, float(v))
                    for k, v in run.metrics.items()
                    if isinstance(v, (int, float))
                ]
                if rows:
                    cur.executemany(
                        """
                        INSERT INTO evaluation_results(run_id, metric_name, metric_value)
                        VALUES (%s, %s, %s)
                        """,
                        rows,
                    )

    def get(self, run_id: str) -> Optional[dict]:
        self._ensure_table()
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT run_id, name, query_count, citation_rate, avg_answer_length, backend, metrics_json
                    FROM evaluation_runs WHERE run_id = %s
                    """,
                    (run_id,),
                )
                row = cur.fetchone()
        if not row:
            return None
        return {
            "run_id": row[0],
            "name": row[1],
            "query_count": row[2],
            "citation_rate": row[3],
            "avg_answer_length": row[4],
            "backend": row[5],
            "metrics": json.loads(row[6] or "{}"),
        }

    def list(self) -> list[dict]:
        self._ensure_table()
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT run_id, name, query_count, citation_rate, avg_answer_length, backend, metrics_json
                    FROM evaluation_runs ORDER BY created_at DESC
                    """
                )
                rows = cur.fetchall()
        return [
            {
                "run_id": r[0],
                "name": r[1],
                "query_count": r[2],
                "citation_rate": r[3],
                "avg_answer_length": r[4],
                "backend": r[5],
                "metrics": json.loads(r[6] or "{}"),
            }
            for r in rows
        ]

    def list_metric_rows(self, run_id: str | None = None, metric_name: str | None = None) -> list[dict]:
        self._ensure_table()
        query = "SELECT run_id, metric_name, metric_value FROM evaluation_results WHERE 1=1"
        params: list = []
        if run_id:
            query += " AND run_id = %s"
            params.append(run_id)
        if metric_name:
            query += " AND metric_name = %s"
            params.append(metric_name)

        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
        return [{"run_id": r[0], "metric_name": r[1], "metric_value": float(r[2])} for r in rows]
