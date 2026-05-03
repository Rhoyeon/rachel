from app.services.chunking import fixed_chunk


def test_fixed_chunk_basic() -> None:
    text = "a" * 500
    chunks = fixed_chunk(text, size=100, overlap=10)
    assert len(chunks) >= 5


def test_fixed_chunk_invalid() -> None:
    try:
        fixed_chunk("abc", size=10, overlap=10)
        assert False
    except ValueError:
        assert True
