import pytest

from app.services.evaluation import run_ragas_evaluation


def test_ragas_strict_raises_when_backend_unavailable():
    with pytest.raises(Exception):
        run_ragas_evaluation(name="strict", samples=[{"question": "q", "answer": "a", "contexts": [], "ground_truth": "g"}], strict=True)
