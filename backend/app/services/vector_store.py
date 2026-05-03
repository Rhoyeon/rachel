from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class VectorPoint:
    id: str
    document_id: str
    chunk_index: int
    vector: List[float]
    text: str


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._points: Dict[str, VectorPoint] = {}

    def upsert_points(self, points: List[VectorPoint]) -> None:
        for p in points:
            self._points[p.id] = p

    def search(self, query_vector: List[float], top_k: int = 5) -> List[VectorPoint]:
        def score(p: VectorPoint) -> float:
            return sum(a * b for a, b in zip(query_vector, p.vector))

        ranked = sorted(self._points.values(), key=score, reverse=True)
        return ranked[:top_k]


class QdrantVectorStore:
    def __init__(self, host: str | None = None, port: int | None = None, collection: str | None = None) -> None:
        self.host = host or os.getenv("RACHEL_QDRANT_HOST", "localhost")
        self.port = port or int(os.getenv("RACHEL_QDRANT_PORT", "6333"))
        self.collection = collection or os.getenv("RACHEL_QDRANT_COLLECTION", "rachel_chunks")

    def _client(self):
        from qdrant_client import QdrantClient

        return QdrantClient(host=self.host, port=self.port)

    def _ensure_collection(self, dim: int) -> None:
        from qdrant_client.models import Distance, VectorParams

        client = self._client()
        cols = [c.name for c in client.get_collections().collections]
        if self.collection not in cols:
            client.create_collection(self.collection, vectors_config=VectorParams(size=dim, distance=Distance.COSINE))

    def upsert_points(self, points: List[VectorPoint]) -> None:
        if not points:
            return
        self._ensure_collection(len(points[0].vector))
        from qdrant_client.models import PointStruct

        client = self._client()
        client.upsert(
            collection_name=self.collection,
            points=[
                PointStruct(
                    id=p.id,
                    vector=p.vector,
                    payload={"document_id": p.document_id, "chunk_index": p.chunk_index, "text": p.text},
                )
                for p in points
            ],
        )

    def search(self, query_vector: List[float], top_k: int = 5) -> List[VectorPoint]:
        client = self._client()
        hits = client.search(collection_name=self.collection, query_vector=query_vector, limit=top_k)
        return [
            VectorPoint(
                id=str(h.id),
                document_id=h.payload.get("document_id", ""),
                chunk_index=h.payload.get("chunk_index", 0),
                vector=query_vector,
                text=h.payload.get("text", ""),
            )
            for h in hits
        ]
