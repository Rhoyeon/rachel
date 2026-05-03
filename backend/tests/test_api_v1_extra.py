import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_document_detail() -> None:
    created = client.post(
        '/api/v1/documents',
        json={'title': 'Doc A', 'doc_type': 'md', 'content': 'detail test content'},
    ).json()
    doc_id = created['data']['id']

    r = client.get(f'/api/v1/documents/{doc_id}')
    assert r.status_code == 200
    assert r.json()['success'] is True
    assert r.json()['data']['id'] == doc_id


def test_document_detail_not_found() -> None:
    r = client.get('/api/v1/documents/not-exist')
    assert r.status_code == 200
    assert r.json()['success'] is False
    assert r.json()['error'] == 'NOT_FOUND'


def test_rag_answer_stub() -> None:
    r = client.post('/api/v1/rag/answer', json={'query': 'what is rachel'})
    assert r.status_code == 200
    assert r.json()['success'] is True
    assert '[STUB]' in r.json()['data']['answer']
