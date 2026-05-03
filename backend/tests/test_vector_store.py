from app.services.vector_store import InMemoryVectorStore, VectorPoint


def test_inmemory_vector_search() -> None:
    store = InMemoryVectorStore()
    store.upsert_points([
        VectorPoint(id='1', document_id='d1', chunk_index=0, vector=[1, 0, 0], text='a'),
        VectorPoint(id='2', document_id='d2', chunk_index=0, vector=[0, 1, 0], text='b'),
    ])
    hits = store.search([1, 0, 0], top_k=1)
    assert len(hits) == 1
    assert hits[0].document_id == 'd1'
