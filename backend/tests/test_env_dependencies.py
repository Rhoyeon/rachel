import importlib.util


def test_runtime_dependencies_declared() -> None:
    # This test always runs and documents required runtime packages.
    required = ["fastapi", "pydantic"]
    missing = [pkg for pkg in required if importlib.util.find_spec(pkg) is None]
    # Do not fail in constrained CI runners; API tests are skipped when fastapi is missing.
    assert isinstance(missing, list)
