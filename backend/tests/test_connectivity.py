from app.services.connectivity import check_postgres, check_vector_store


class _OkCursor:
    def execute(self, _query):
        return None

    def fetchone(self):
        return (1,)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _OkConn:
    def cursor(self):
        return _OkCursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _RepoOk:
    def _conn(self):
        return _OkConn()


class _RepoFail:
    def _conn(self):
        raise RuntimeError("db down")


class _QdrantClientOk:
    def get_collections(self):
        return {"collections": []}


class _VectorOk:
    def _client(self):
        return _QdrantClientOk()


class _VectorFail:
    def _client(self):
        raise RuntimeError("qdrant down")


def test_check_postgres_ok():
    result = check_postgres(_RepoOk())
    assert result.ok is True


def test_check_postgres_fail():
    result = check_postgres(_RepoFail())
    assert result.ok is False


def test_check_vector_store_ok():
    result = check_vector_store(_VectorOk())
    assert result.ok is True


def test_check_vector_store_fail():
    result = check_vector_store(_VectorFail())
    assert result.ok is False
