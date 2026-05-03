from pathlib import Path

from app.services.datasets import InMemoryEvalDatasetStore, SQLiteEvalDatasetStore


def test_dataset_store_create_and_list_in_memory() -> None:
    s = InMemoryEvalDatasetStore()
    ds = s.create(name="d1", items=[{"q": "q1", "a": "a1"}], dataset_id="ds-1")
    assert ds.dataset_id == "ds-1"
    items = s.list()
    assert len(items) == 1
    assert items[0]["name"] == "d1"


def test_dataset_store_create_and_list_sqlite(tmp_path: Path) -> None:
    db = tmp_path / "rachel.db"
    s = SQLiteEvalDatasetStore(path=str(db))
    s.create(name="ds", items=[{"q": "q", "a": "a"}], dataset_id="dsql-1")
    rows = s.list()
    assert rows[0]["dataset_id"] == "dsql-1"
    assert rows[0]["items"][0]["q"] == "q"
