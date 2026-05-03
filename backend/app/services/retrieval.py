from __future__ import annotations

from collections import Counter
from math import log
from typing import Iterable, List


def _tokenize(text: str) -> list[str]:
    return [t for t in (text or "").lower().split() if t]


def bm25_score(query: str, doc: str, corpus: Iterable[str], k1: float = 1.5, b: float = 0.75) -> float:
    q_terms = _tokenize(query)
    d_terms = _tokenize(doc)
    if not q_terms or not d_terms:
        return 0.0

    corpus_terms = [_tokenize(c) for c in corpus]
    n_docs = max(len(corpus_terms), 1)
    avgdl = sum(len(t) for t in corpus_terms) / n_docs
    freqs = Counter(d_terms)
    score = 0.0

    for term in q_terms:
        n_qi = sum(1 for terms in corpus_terms if term in terms)
        idf = log((n_docs - n_qi + 0.5) / (n_qi + 0.5) + 1)
        tf = freqs.get(term, 0)
        denom = tf + k1 * (1 - b + b * (len(d_terms) / max(avgdl, 1)))
        score += idf * ((tf * (k1 + 1)) / max(denom, 1e-9))
    return score


def simple_rerank(query: str, items: List[dict]) -> List[dict]:
    q = set(_tokenize(query))
    for it in items:
        s = set(_tokenize(it.get("snippet", "")))
        overlap = len(q.intersection(s))
        it["rerank_score"] = overlap
    return sorted(items, key=lambda x: (x.get("rerank_score", 0), x.get("score", 0)), reverse=True)
