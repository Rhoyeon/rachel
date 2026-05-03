import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_evaluations_compare_api() -> None:
    a = client.post('/api/v1/evaluations/runs', json={'name': 'A', 'samples': [{'answer': 'x', 'citations': [1]}], 'retrieval_samples': [{'relevant_ids': ['d1'], 'retrieved_ids': ['d1']}]}).json()['data']['run_id']
    b = client.post('/api/v1/evaluations/runs', json={'name': 'B', 'samples': [{'answer': 'x', 'citations': []}], 'retrieval_samples': [{'relevant_ids': ['d1'], 'retrieved_ids': ['d9']}]}).json()['data']['run_id']

    r = client.get('/api/v1/evaluations/compare', params={'run_ids': f'{a},{b}', 'metric_keys': 'recall_at_k,mrr', 'sort_by': 'mrr', 'strict_only': 'false', 'strict_mode': 'requested', 'baseline_run_id': a, 'min_query_count': 0})
    assert r.status_code == 200
    body = r.json()['data']
    assert 'leaders' in body
    assert 'rows' in body
    assert len(body['rows']) == 2
    assert body['metric_keys'] == ['recall_at_k', 'mrr']


def test_evaluations_metric_rows_api() -> None:
    run_id = client.post(
        '/api/v1/evaluations/runs',
        json={'name': 'M', 'samples': [{'answer': 'x', 'citations': [1]}], 'retrieval_samples': [{'relevant_ids': ['d1'], 'retrieved_ids': ['d1']}]},
    ).json()['data']['run_id']

    r = client.get('/api/v1/evaluations/metrics', params={'run_id': run_id, 'metric_name': 'mrr', 'page': 1, 'page_size': 5, 'sort_by': 'metric_value', 'sort_order': 'desc'})
    assert r.status_code == 200
    body = r.json()['data']
    assert body['count'] >= 1
    assert body['page'] == 1
    assert body['page_size'] == 5
