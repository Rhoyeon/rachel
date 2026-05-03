import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_trace_id_header_propagation() -> None:
    r = client.get('/health', headers={'x-trace-id': 'trace-123'})
    assert r.status_code == 200
    assert r.headers.get('x-trace-id') == 'trace-123'
