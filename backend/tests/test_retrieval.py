from app.services.retrieval import bm25_score, simple_rerank


def test_bm25_prefers_matching_document() -> None:
    corpus = ["api auth guide", "database migration manual"]
    s1 = bm25_score("api auth", corpus[0], corpus)
    s2 = bm25_score("api auth", corpus[1], corpus)
    assert s1 > s2


def test_simple_rerank_uses_overlap() -> None:
    items = [
        {"snippet": "auth token refresh", "score": 0.2},
        {"snippet": "unrelated text", "score": 0.9},
    ]
    ranked = simple_rerank("auth token", items)
    assert ranked[0]["snippet"] == "auth token refresh"
