from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List
import hashlib
import json
from uuid import uuid4


@dataclass
class EvalRun:
    run_id: str
    name: str
    query_count: int
    citation_rate: float
    avg_answer_length: float
    backend: str
    metrics: Dict[str, Any] = field(default_factory=dict)


RUNS: Dict[str, EvalRun] = {}


def compute_retrieval_metrics(samples: List[dict], k: int = 5) -> Dict[str, float]:
    """
    samples item format:
      {
        "relevant_ids": ["d1", ...],
        "retrieved_ids": ["d2", "d1", ...]
      }
    """
    if not samples:
        return {"recall_at_k": 0.0, "mrr": 0.0, "k": float(k)}

    recalls = []
    rr_values = []
    for s in samples:
        relevant = set(s.get("relevant_ids", []))
        retrieved = list(s.get("retrieved_ids", []))[:k]

        if relevant:
            hit_count = sum(1 for rid in retrieved if rid in relevant)
            recalls.append(hit_count / len(relevant))
        else:
            recalls.append(0.0)

        rr = 0.0
        for idx, rid in enumerate(retrieved, start=1):
            if rid in relevant:
                rr = 1.0 / idx
                break
        rr_values.append(rr)

    return {
        "recall_at_k": sum(recalls) / len(recalls),
        "mrr": sum(rr_values) / len(rr_values),
        "k": float(k),
    }


def run_simple_evaluation(name: str, samples: List[dict]) -> EvalRun:
    total = len(samples)
    if total == 0:
        result = EvalRun(
            run_id=str(uuid4()),
            name=name,
            query_count=0,
            citation_rate=0.0,
            avg_answer_length=0.0,
            backend="simple",
            metrics={},
        )
        RUNS[result.run_id] = result
        return result

    with_citation = sum(1 for s in samples if s.get("citations"))
    avg_len = sum(len(s.get("answer", "")) for s in samples) / total
    result = EvalRun(
        run_id=str(uuid4()),
        name=name,
        query_count=total,
        citation_rate=with_citation / total,
        avg_answer_length=avg_len,
        backend="simple",
        metrics={},
    )
    RUNS[result.run_id] = result
    return result


def run_ragas_evaluation(name: str, samples: List[dict], strict: bool = False) -> EvalRun:
    """
    Execute RAGAS evaluation when library is available; fallback to simple evaluation on any error.
    This function is intentionally defensive because deployment environments may not have ragas installed.
    """
    try:
        from datasets import Dataset  # type: ignore
        from ragas import evaluate  # type: ignore
        from ragas.metrics import answer_relevancy, context_precision, context_recall, faithfulness  # type: ignore

        total = len(samples)
        with_citation = sum(1 for s in samples if s.get("citations"))
        avg_len = (sum(len(s.get("answer", "")) for s in samples) / total) if total else 0.0
        dataset = Dataset.from_list(
            [
                {
                    "question": s.get("question", ""),
                    "answer": s.get("answer", ""),
                    "contexts": s.get("contexts", []),
                    "ground_truth": s.get("ground_truth", ""),
                }
                for s in samples
            ]
        ) if total else Dataset.from_list([])

        if total:
            result = evaluate(dataset=dataset, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
            metrics = {k: float(v) for k, v in result.items() if isinstance(v, (float, int))}
        else:
            metrics = {"faithfulness": 0.0, "answer_relevancy": 0.0, "context_precision": 0.0, "context_recall": 0.0}

        result = EvalRun(
            run_id=str(uuid4()),
            name=name,
            query_count=total,
            citation_rate=(with_citation / total) if total else 0.0,
            avg_answer_length=avg_len,
            backend="ragas",
            metrics=metrics,
        )
        RUNS[result.run_id] = result
        return result
    except Exception:
        if strict:
            raise
        return run_simple_evaluation(name=name, samples=samples)


def list_runs() -> List[dict]:
    return [asdict(v) for v in RUNS.values()]



def build_config_hash(config: Dict[str, Any] | None) -> str | None:
    if not config:
        return None
    blob = json.dumps(config, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def compare_runs(
    runs: List[dict],
    metric_keys: List[str] | None = None,
    sort_by: str | None = None,
    strict_only: bool = False,
    strict_mode: str = "requested",
    baseline_run_id: str | None = None,
    min_query_count: int = 0,
    run_tag: str | None = None,
    weights: Dict[str, float] | None = None,
) -> Dict[str, Any]:
    metric_keys = metric_keys or ["recall_at_k", "mrr", "faithfulness", "answer_relevancy", "context_precision", "context_recall"]
    rows = []
    leaders: Dict[str, dict] = {}

    for r in runs:
        metrics = r.get("metrics", {}) if isinstance(r, dict) else {}
        meta = metrics.get("_meta", {}) if isinstance(metrics.get("_meta", {}), dict) else {}
        if run_tag and run_tag not in meta.get("run_tags", []):
            continue
        if int(r.get("query_count", 0)) < min_query_count:
            continue
        if strict_only:
            if strict_mode == "passed" and not metrics.get("strict_eval_passed", False):
                continue
            if strict_mode != "passed" and not metrics.get("strict_eval_requested", False):
                continue

        row = {
            "run_id": r.get("run_id"),
            "name": r.get("name"),
            "backend": r.get("backend"),
            "query_count": r.get("query_count"),
            "metrics": {},
            "delta": {},
        }
        vals = []
        wsum = 0.0
        wtot = 0.0
        for m in metric_keys:
            v = metrics.get(m)
            if isinstance(v, (int, float)):
                fv = float(v)
                row["metrics"][m] = fv
                vals.append(fv)
                w = float((weights or {}).get(m, 1.0))
                wsum += w * fv
                wtot += w
                if m not in leaders or fv > leaders[m]["value"]:
                    leaders[m] = {"run_id": r.get("run_id"), "value": fv}
        row["weighted_score"] = (wsum / wtot) if wtot else ((sum(vals) / len(vals)) if vals else 0.0)
        rows.append(row)

    baseline = next((r for r in rows if r["run_id"] == baseline_run_id), None) if baseline_run_id else None
    if baseline:
        for row in rows:
            for m in metric_keys:
                v = row["metrics"].get(m)
                b = baseline["metrics"].get(m)
                if isinstance(v, float) and isinstance(b, float):
                    row["delta"][m] = v - b

    if sort_by:
        if sort_by == "weighted_score":
            rows.sort(key=lambda x: x.get("weighted_score", float("-inf")), reverse=True)
        else:
            rows.sort(key=lambda x: x["metrics"].get(sort_by, float("-inf")), reverse=True)

    summary = {
        "run_count": len(rows),
        "avg_weighted_score": (sum(r.get("weighted_score", 0.0) for r in rows) / len(rows)) if rows else 0.0,
    }
    return {
        "rows": rows,
        "leaders": leaders,
        "metric_keys": metric_keys,
        "sort_by": sort_by,
        "strict_only": strict_only,
        "strict_mode": strict_mode,
        "baseline_run_id": baseline_run_id,
        "min_query_count": min_query_count,
        "run_tag": run_tag,
        "weights": weights or {},
        "summary": summary,
    }



def summarize_runs(runs: List[dict]) -> Dict[str, Any]:
    total = len(runs)
    if total == 0:
        return {"run_count": 0, "strict_requested_rate": 0.0, "strict_pass_rate": 0.0, "avg_query_count": 0.0}

    strict_requested = 0
    strict_passed = 0
    query_sum = 0
    tags: Dict[str, int] = {}

    for r in runs:
        metrics = r.get("metrics", {})
        meta = metrics.get("_meta", {}) if isinstance(metrics.get("_meta", {}), dict) else {}
        if metrics.get("strict_eval_requested", False):
            strict_requested += 1
        if metrics.get("strict_eval_passed", False):
            strict_passed += 1
        query_sum += int(r.get("query_count", 0) or 0)
        for t in meta.get("run_tags", []):
            tags[t] = tags.get(t, 0) + 1

    return {
        "run_count": total,
        "strict_requested_rate": strict_requested / total,
        "strict_pass_rate": strict_passed / total,
        "avg_query_count": query_sum / total,
        "tag_counts": tags,
    }
