import pytest

pytest.importorskip("fastapi")
pytestmark = pytest.mark.api

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_eval_run_detail_api() -> None:
    created = client.post(
        "/api/v1/evaluations/runs",
        json={"name": "detail", "samples": [{"answer": "ok", "citations": [1]}], "eval_backend": "simple"},
    )
    assert created.status_code == 200
    run_id = created.json()["data"]["run_id"]

    fetched = client.get(f"/api/v1/evaluations/runs/{run_id}")
    assert fetched.status_code == 200
    assert fetched.json()["data"]["run_id"] == run_id
