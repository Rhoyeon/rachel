from typing import List


def fixed_chunk(text: str, size: int = 200, overlap: int = 20) -> List[str]:
    if size <= 0:
        raise ValueError("size must be > 0")
    if overlap < 0 or overlap >= size:
        raise ValueError("overlap must be >= 0 and < size")

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        part = text[start:end].strip()
        if part:
            chunks.append(part)
        if end == len(text):
            break
        start = end - overlap
    return chunks
