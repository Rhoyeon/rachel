from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Protocol


@dataclass
class LLMResult:
    text: str
    model: str


class LLMClient(Protocol):
    def generate(self, query: str, contexts: List[str]) -> LLMResult: ...


class StubLLMClient:
    def generate(self, query: str, contexts: List[str]) -> LLMResult:
        if contexts:
            snippet = " | ".join(c[:60] for c in contexts[:2])
            return LLMResult(text=f"[STUB] 질문: {query}\n요약근거: {snippet}", model="stub-rag-v5")
        return LLMResult(text=f"[STUB] 질문 '{query}'에 대한 근거를 찾지 못했습니다.", model="stub-rag-v5")


class EchoLLMClient:
    """Local deterministic client to emulate non-stub model wiring without external APIs."""

    def generate(self, query: str, contexts: List[str]) -> LLMResult:
        merged = "\n".join(contexts[:2]) if contexts else "NO_CONTEXT"
        return LLMResult(text=f"[ECHO] {query}\n{merged}", model="echo-local-v1")


def get_llm_client() -> LLMClient:
    provider = os.getenv("RACHEL_LLM_PROVIDER", "stub").lower()
    if provider == "echo":
        return EchoLLMClient()
    return StubLLMClient()
