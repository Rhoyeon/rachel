from app.services.evaluation import compute_retrieval_metrics


def test_compute_recall_and_mrr() -> None:
    samples = [
        {"relevant_ids": ["d1"], "retrieved_ids": ["d2", "d1"]},  # rr=1/2 recall=1
        {"relevant_ids": ["d3", "d4"], "retrieved_ids": ["d4", "d9"]},  # rr=1 recall=1/2
    ]
    m = compute_retrieval_metrics(samples, k=2)
    assert round(m["recall_at_k"], 4) == 0.75
    assert round(m["mrr"], 4) == 0.75
    assert m["k"] == 2.0


def test_compute_recall_and_mrr_empty() -> None:
    m = compute_retrieval_metrics([], k=5)
    assert m["recall_at_k"] == 0.0
    assert m["mrr"] == 0.0
