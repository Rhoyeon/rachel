import os

from app.services.db_store import SQLiteChunkRepository, SQLiteDocumentRepository
from app.services.postgres_store import PostgresChunkRepository, PostgresDocumentRepository
from app.services.repository import ChunkRepository, DocumentRepository
from app.services.llm import LLMClient, get_llm_client as _build_llm_client
from app.services.eval_store import EvalRunStore, InMemoryEvalRunStore, PostgresEvalRunStore, SQLiteEvalRunStore
from app.services.store import InMemoryChunkRepository, InMemoryDocumentRepository
from app.services.vector_store import InMemoryVectorStore, QdrantVectorStore

_doc_repo_singleton: DocumentRepository | None = None
_chunk_repo_singleton: ChunkRepository | None = None
_vector_store_singleton: InMemoryVectorStore | QdrantVectorStore | None = None
_llm_client_singleton: LLMClient | None = None
_eval_store_singleton: EvalRunStore | None = None


def get_document_repository() -> DocumentRepository:
    global _doc_repo_singleton
    if _doc_repo_singleton is None:
        backend = os.getenv("RACHEL_REPO_BACKEND", "memory")
        if backend == "postgres":
            _doc_repo_singleton = PostgresDocumentRepository()
        elif backend == "sqlite":
            _doc_repo_singleton = SQLiteDocumentRepository()
        else:
            _doc_repo_singleton = InMemoryDocumentRepository()
    return _doc_repo_singleton


def get_chunk_repository() -> ChunkRepository:
    global _chunk_repo_singleton
    if _chunk_repo_singleton is None:
        backend = os.getenv("RACHEL_REPO_BACKEND", "memory")
        if backend == "postgres":
            _chunk_repo_singleton = PostgresChunkRepository()
        elif backend == "sqlite":
            _chunk_repo_singleton = SQLiteChunkRepository()
        else:
            _chunk_repo_singleton = InMemoryChunkRepository()
    return _chunk_repo_singleton


def get_vector_store() -> InMemoryVectorStore | QdrantVectorStore:
    global _vector_store_singleton
    if _vector_store_singleton is None:
        backend = os.getenv("RACHEL_VECTOR_BACKEND", "memory")
        _vector_store_singleton = QdrantVectorStore() if backend == "qdrant" else InMemoryVectorStore()
    return _vector_store_singleton


def get_llm_client() -> LLMClient:
    global _llm_client_singleton
    if _llm_client_singleton is None:
        _llm_client_singleton = _build_llm_client()
    return _llm_client_singleton


def get_eval_store() -> EvalRunStore:
    global _eval_store_singleton
    if _eval_store_singleton is None:
        backend = os.getenv("RACHEL_EVAL_BACKEND", "memory")
        if backend == "postgres":
            _eval_store_singleton = PostgresEvalRunStore()
        elif backend == "sqlite":
            _eval_store_singleton = SQLiteEvalRunStore()
        else:
            _eval_store_singleton = InMemoryEvalRunStore()
    return _eval_store_singleton
