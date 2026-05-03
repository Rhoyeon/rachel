from app.services.store import InMemoryChunkRepository


def test_inmemory_chunk_repository_save_and_list() -> None:
    repo = InMemoryChunkRepository()
    saved = repo.save_for_document('d1', ['a', 'b'])
    assert saved == 2
    rows = repo.list_for_document('d1')
    assert len(rows) == 2
    assert rows[0].chunk_index == 0
