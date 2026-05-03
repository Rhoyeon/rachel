from __future__ import annotations

import re


def preprocess_text(text: str, remove_extra_blank_lines: bool = True, collapse_spaces: bool = True) -> str:
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    if collapse_spaces:
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
    if remove_extra_blank_lines:
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()
