from app.services.evaluation import summarize_runs


def test_summarize_runs_basic() -> None:
    runs = [
        {"query_count": 10, "metrics": {"strict_eval_requested": True, "strict_eval_passed": True, "_meta": {"run_tags": ["nightly"]}}},
        {"query_count": 4, "metrics": {"strict_eval_requested": False, "strict_eval_passed": False, "_meta": {"run_tags": ["exp", "nightly"]}}},
    ]
    s = summarize_runs(runs)
    assert s["run_count"] == 2
    assert s["strict_requested_rate"] == 0.5
    assert s["strict_pass_rate"] == 0.5
    assert s["avg_query_count"] == 7.0
    assert s["tag_counts"]["nightly"] == 2
