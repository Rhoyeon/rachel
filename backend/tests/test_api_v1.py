import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_documents_and_search_flow() -> None:
    r = client.post(
        '/api/v1/documents',
        json={'title': 'API Guide', 'doc_type': 'md', 'content': 'Rachel quality monitoring guide'},
    )
    assert r.status_code == 200
    assert r.json()['success'] is True
    assert r.json()["data"]["parser_used"] == "markdown"

    r = client.get('/api/v1/documents')
    assert r.status_code == 200
    assert len(r.json()['data']['items']) >= 1

    r = client.post('/api/v1/search', json={'query': 'quality', 'top_k': 3})
    assert r.status_code == 200
    assert len(r.json()['data']['items']) >= 1


def test_chunk_preview() -> None:
    r = client.post('/api/v1/playground/chunk/preview', json={'text': 'a' * 350, 'size': 100, 'overlap': 10})
    assert r.status_code == 200
    assert r.json()['data']['count'] >= 3


def test_documents_and_search_filters() -> None:
    client.post('/api/v1/documents', json={'title': 'Ops Manual', 'doc_type': 'pdf', 'content': 'ops incident guide'})
    client.post('/api/v1/documents', json={'title': 'Dev Guide', 'doc_type': 'md', 'content': 'dev coding standard'})

    r = client.get('/api/v1/documents', params={'doc_type': 'md'})
    assert r.status_code == 200
    items = r.json()['data']['items']
    assert all(it['doc_type'].lower() == 'md' for it in items)

    r = client.post('/api/v1/search', json={'query': 'guide', 'doc_type': 'pdf', 'top_k': 10})
    assert r.status_code == 200
    sitems = r.json()['data']['items']
    assert all(it['title'] == 'Ops Manual' for it in sitems)
