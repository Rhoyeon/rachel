import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_build_document_chunks_endpoint() -> None:
    created = client.post(
        '/api/v1/documents',
        json={'title': 'Chunk Doc', 'doc_type': 'md', 'content': 'chunk me ' * 80},
    ).json()
    doc_id = created['data']['id']

    r = client.post(f'/api/v1/documents/{doc_id}/chunks', json={'size': 120, 'overlap': 20})
    assert r.status_code == 200
    body = r.json()
    assert body['success'] is True
    assert body['data']['chunk_count'] >= 2
