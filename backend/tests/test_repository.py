from app.services.store import InMemoryDocumentRepository


def test_inmemory_repository_crud() -> None:
    repo = InMemoryDocumentRepository()
    doc = repo.create("Doc", "md", "content")
    assert repo.get(doc.id) is not None
    assert len(repo.list()) == 1
