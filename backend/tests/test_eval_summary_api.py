import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_eval_summary_api() -> None:
    client.post('/api/v1/evaluations/runs', json={'name': 's1', 'samples': [{'answer': 'a', 'citations': [1]}], 'run_tags': ['nightly']})
    r = client.get('/api/v1/evaluations/summary')
    assert r.status_code == 200
    data = r.json()['data']
    assert data['run_count'] >= 1
    assert 'strict_requested_rate' in data
