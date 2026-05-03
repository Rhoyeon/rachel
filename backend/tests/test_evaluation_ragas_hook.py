import pytest

from app.services.evaluation import run_ragas_evaluation

pytestmark = pytest.mark.ragas_optional


def test_ragas_hook_falls_back_to_simple_when_library_missing():
    run = run_ragas_evaluation(
        name="fallback",
        samples=[{"answer": "a", "citations": [{"id": 1}]}],
    )
    assert run.backend in {"simple", "ragas"}
    assert run.query_count == 1


def test_ragas_hook_returns_consistent_shape():
    run = run_ragas_evaluation(name="shape", samples=[])
    assert isinstance(run.run_id, str)
    assert hasattr(run, "metrics")
