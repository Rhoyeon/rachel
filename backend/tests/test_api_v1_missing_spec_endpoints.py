import pytest


fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from app.main import app


def test_missing_spec_endpoints_present() -> None:
    client = TestClient(app)

    created = client.post("/api/v1/documents", json={"title": "t", "doc_type": "txt", "content": "hello"}).json()["data"]
    doc_id = created["id"]

    assert client.post(f"/api/v1/documents/{doc_id}/reprocess").status_code == 200
    assert client.post("/api/v1/playground/chunk/commit", json={"text": "hello world"}).status_code == 200
    assert client.get("/api/v1/embedding/profiles").status_code == 200
    assert client.post("/api/v1/playground/embed/commit", json={"text": "hello", "profile": "default"}).status_code == 200

    d = client.post("/api/v1/evaluations/datasets", json={"name": "d1", "items": [{"q": "q", "a": "a"}]}).json()["data"]
    assert d["name"] == "d1"
    assert client.get("/api/v1/evaluations/datasets").status_code == 200

    run = client.post("/api/v1/evaluations/runs", json={"name": "r1", "samples": [{"question": "q", "answer": "a", "reference": "a", "citations": ["c"]}]}).json()["data"]
    run_id = run["run_id"]
    assert client.get(f"/api/v1/evaluations/runs/{run_id}/results").status_code == 200
    assert client.get(f"/api/v1/quality/live?run_id={run_id}").status_code == 200

