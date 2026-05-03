import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_eval_runs_api() -> None:
    r = client.post('/api/v1/evaluations/runs', json={'name': 'smoke', 'samples': [{'answer': 'a', 'citations': [1]}, {'answer': 'bb', 'citations': []}], 'retrieval_samples': [{'relevant_ids': ['d1'], 'retrieved_ids': ['d2', 'd1']}], 'top_k': 2, 'run_tags': ['nightly'], 'config': {'retriever': 'hybrid', 'top_k': 2}})
    assert r.status_code == 200
    assert r.json()['success'] is True
    metrics = r.json()['data']['metrics']
    assert 'recall_at_k' in metrics
    assert 'mrr' in metrics
    assert '_meta' in metrics
    assert metrics['_meta']['config_hash'] is not None

    r = client.get('/api/v1/evaluations/runs')
    assert r.status_code == 200
    assert len(r.json()['data']['items']) >= 1
