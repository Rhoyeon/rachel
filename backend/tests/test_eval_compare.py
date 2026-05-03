from app.services.evaluation import compare_runs


def test_compare_runs_leaders() -> None:
    runs = [
        {"run_id": "r1", "name": "A", "backend": "simple", "query_count": 10, "metrics": {"recall_at_k": 0.4, "mrr": 0.3}},
        {"run_id": "r2", "name": "B", "backend": "ragas", "query_count": 10, "metrics": {"recall_at_k": 0.7, "mrr": 0.2}},
    ]
    out = compare_runs(runs)
    assert out["leaders"]["recall_at_k"]["run_id"] == "r2"
    assert out["leaders"]["mrr"]["run_id"] == "r1"
    assert len(out["rows"]) == 2


def test_compare_runs_sort_and_strict_filter() -> None:
    runs = [
        {"run_id": "r1", "name": "A", "backend": "simple", "query_count": 10, "metrics": {"mrr": 0.8, "strict_eval_requested": False}},
        {"run_id": "r2", "name": "B", "backend": "ragas", "query_count": 10, "metrics": {"mrr": 0.5, "strict_eval_requested": True}},
    ]
    out = compare_runs(runs, sort_by="weighted_score", strict_only=True)
    assert len(out["rows"]) == 1
    assert out["rows"][0]["run_id"] == "r2"
    assert "summary" in out


def test_compare_runs_strict_mode_passed() -> None:
    runs = [
        {"run_id": "r1", "name": "A", "backend": "ragas", "query_count": 10, "metrics": {"mrr": 0.4, "strict_eval_requested": True, "strict_eval_passed": False}},
        {"run_id": "r2", "name": "B", "backend": "ragas", "query_count": 10, "metrics": {"mrr": 0.6, "strict_eval_requested": True, "strict_eval_passed": True}},
    ]
    out = compare_runs(runs, strict_only=True, strict_mode="passed")
    assert len(out["rows"]) == 1
    assert out["rows"][0]["run_id"] == "r2"


def test_compare_runs_baseline_and_min_query_count() -> None:
    runs = [
        {"run_id": "base", "name": "Base", "backend": "ragas", "query_count": 5, "metrics": {"mrr": 0.4}},
        {"run_id": "cand", "name": "Cand", "backend": "ragas", "query_count": 12, "metrics": {"mrr": 0.7}},
    ]
    out = compare_runs(runs, baseline_run_id="base", min_query_count=5)
    cand = next(r for r in out["rows"] if r["run_id"] == "cand")
    assert round(cand["delta"]["mrr"], 4) == 0.3


def test_compare_runs_tag_and_weights() -> None:
    runs = [
        {"run_id": "r1", "name": "A", "backend": "ragas", "query_count": 10, "metrics": {"mrr": 0.2, "recall_at_k": 0.9, "_meta": {"run_tags": ["exp-a"]}}},
        {"run_id": "r2", "name": "B", "backend": "ragas", "query_count": 10, "metrics": {"mrr": 0.8, "recall_at_k": 0.4, "_meta": {"run_tags": ["exp-b"]}}},
    ]
    out = compare_runs(runs, run_tag="exp-b", weights={"mrr": 2.0, "recall_at_k": 1.0})
    assert len(out["rows"]) == 1
    assert out["rows"][0]["run_id"] == "r2"
