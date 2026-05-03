# Rachel Agent

Rachel Agent는 사용자 입력으로 RAG+VectorDB를 자동 구축하고, 품질을 실시간으로 확인/개선하는 서비스입니다.

## Repository Layout
- `docs/`: PRD, architecture, API, DB schema, ops, testing strategy, wireframes
- `backend/`: FastAPI service scaffold
- `frontend/`: UI scaffold placeholder
- `infra/`: infra scaffold

## Quick Start (local)
```bash
docker compose up -d
cd backend
pip install -r requirements.txt
pytest -q
cd ..
PYTHONPATH=backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:
```bash
curl http://localhost:8000/health
```
