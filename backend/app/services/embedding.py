from __future__ import annotations

from hashlib import md5
from typing import List


EMBED_DIM = 8


def embed_text(text: str) -> List[float]:
    digest = md5(text.encode("utf-8")).digest()
    vals = [int(digest[i]) / 255.0 for i in range(EMBED_DIM)]
    return vals
