import os

from app.core import deps
from app.services.eval_store import PostgresEvalRunStore
from app.services.postgres_store import PostgresDocumentRepository
from app.services.store import InMemoryDocumentRepository


def test_backend_selection_memory() -> None:
    os.environ['RACHEL_REPO_BACKEND'] = 'memory'
    deps._doc_repo_singleton = None
    repo = deps.get_document_repository()
    assert isinstance(repo, InMemoryDocumentRepository)


def test_backend_selection_postgres() -> None:
    os.environ['RACHEL_REPO_BACKEND'] = 'postgres'
    deps._doc_repo_singleton = None
    repo = deps.get_document_repository()
    assert isinstance(repo, PostgresDocumentRepository)


def test_eval_backend_selection_postgres() -> None:
    os.environ["RACHEL_EVAL_BACKEND"] = "postgres"
    deps._eval_store_singleton = None
    store = deps.get_eval_store()
    assert isinstance(store, PostgresEvalRunStore)
