import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_rag_answer_with_citation() -> None:
    created = client.post('/api/v1/documents', json={'title': 'RAG Doc', 'doc_type': 'md', 'content': 'Rachel retrieval quality'}).json()
    doc_id = created['data']['id']
    client.post(f'/api/v1/documents/{doc_id}/chunks', json={'size': 50, 'overlap': 10})

    r = client.post('/api/v1/rag/answer', json={'query': 'retrieval'})
    assert r.status_code == 200
    assert r.json()['success'] is True
    assert len(r.json()['data']['citations']) >= 1
    assert "[STUB]" in r.json()["data"]["answer"]
