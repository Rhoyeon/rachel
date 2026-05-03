import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from app.core.deps import get_llm_client
from app.main import app


class _FailingLLM:
    def generate(self, query: str, contexts: list[str]):
        raise RuntimeError("llm down")


def test_rag_answer_falls_back_to_stub_when_llm_fails() -> None:
    app.dependency_overrides[get_llm_client] = lambda: _FailingLLM()
    client = TestClient(app)
    created = client.post("/api/v1/documents", json={"title": "doc", "doc_type": "md", "content": "retrieval sample"}).json()
    doc_id = created["data"]["id"]
    client.post(f"/api/v1/documents/{doc_id}/chunks", json={"size": 50, "overlap": 10})

    r = client.post("/api/v1/rag/answer", json={"query": "retrieval"})
    assert r.status_code == 200
    assert "[STUB]" in r.json()["data"]["answer"]

    app.dependency_overrides.clear()
