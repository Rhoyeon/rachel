from pathlib import Path
import sqlite3

from app.services.eval_store import InMemoryEvalRunStore, SQLiteEvalRunStore
from app.services.evaluation import EvalRun


def test_eval_store_save_and_get():
    store = InMemoryEvalRunStore()
    run = EvalRun(
        run_id="run-1",
        name="exp",
        query_count=3,
        citation_rate=0.66,
        avg_answer_length=23.0,
        backend="simple",
        metrics={"faithfulness": 0.8},
    )
    store.save(run)
    row = store.get("run-1")
    assert row is not None
    assert row["name"] == "exp"
    assert row["metrics"]["faithfulness"] == 0.8


def test_eval_store_list():
    store = InMemoryEvalRunStore()
    run = EvalRun(
        run_id="run-2",
        name="exp2",
        query_count=1,
        citation_rate=1.0,
        avg_answer_length=10.0,
        backend="simple",
        metrics={},
    )
    store.save(run)
    items = store.list()
    assert len(items) == 1
    assert items[0]["run_id"] == "run-2"


def test_sqlite_eval_store_normalized_metric_rows(tmp_path: Path) -> None:
    db_path = tmp_path / "eval.db"
    store = SQLiteEvalRunStore(path=str(db_path))
    run = EvalRun(
        run_id="run-3",
        name="exp3",
        query_count=2,
        citation_rate=0.5,
        avg_answer_length=7.0,
        backend="ragas",
        metrics={"recall_at_k": 0.8, "mrr": 0.6, "strict_eval_requested": 1.0},
    )
    store.save(run)

    with sqlite3.connect(str(db_path)) as conn:
        rows = conn.execute(
            "SELECT metric_name, metric_value FROM evaluation_results WHERE run_id = ? ORDER BY metric_name",
            ("run-3",),
        ).fetchall()

    assert ("mrr", 0.6) in rows
    assert ("recall_at_k", 0.8) in rows


def test_sqlite_eval_store_metric_row_filter(tmp_path: Path) -> None:
    db_path = tmp_path / "eval_filter.db"
    store = SQLiteEvalRunStore(path=str(db_path))
    run = EvalRun(
        run_id="run-4",
        name="exp4",
        query_count=1,
        citation_rate=1.0,
        avg_answer_length=3.0,
        backend="simple",
        metrics={"mrr": 0.9, "recall_at_k": 1.0},
    )
    store.save(run)
    rows = store.list_metric_rows(run_id="run-4", metric_name="mrr")
    assert len(rows) == 1
    assert rows[0]["metric_name"] == "mrr"
