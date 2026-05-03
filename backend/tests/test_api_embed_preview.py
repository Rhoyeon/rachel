import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_embed_preview_endpoint():
    r = client.post("/api/v1/playground/embed/preview", json={"text": "preview test", "top_k": 2})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["data"]["dimension"] > 0
