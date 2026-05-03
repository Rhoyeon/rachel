# Backend (FastAPI)

## Run
```bash
# from repository root
PYTHONPATH=backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Test
```bash
cd backend
pytest -q
```

## Notes
- If dependencies are not installed yet, run `pip install -r requirements.txt` first.
- In restricted network environments, dependency installation may fail; use a prebuilt dev image or internal package mirror.

## Next steps
- Implement additional `/api/v1` routes from `docs/api_spec_v1.md`
- Replace in-memory store with PostgreSQL + Qdrant integration
