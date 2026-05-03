import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload_document_endpoint() -> None:
    res = client.post(
        "/api/v1/documents/upload",
        data={"title": "Upload Guide", "doc_type": "txt"},
        files={"file": ("guide.txt", b"rachel upload test", "text/plain")},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["filename"] == "guide.txt"
