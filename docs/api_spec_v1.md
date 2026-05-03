# API Spec v1.2 (MVP) - Rachel Agent

Rachel Agent는 **사용자 입력으로 RAG+VectorDB를 자동 구축**하며, API는 실시간 품질 확인 워크플로우를 지원한다.

Base: `/api/v1`

## 1) Documents
- `POST /documents` : 문서 업로드
- `GET /documents` : 목록/필터
- `GET /documents/{id}` : 상세
- `POST /documents/{id}/reprocess` : 재처리 요청

## 2) Playground
- `POST /playground/chunk/preview`
- `POST /playground/chunk/commit`
- `GET /embedding/profiles`
- `POST /playground/embed/preview`
- `POST /playground/embed/commit`

## 3) Search / RAG
- `POST /search`
- `POST /rag/answer`

## 4) Evaluation
- `POST /evaluations/datasets`
- `GET /evaluations/datasets`
- `POST /evaluations/runs`
- `GET /evaluations/runs/{id}`
- `GET /evaluations/runs/{id}/results`
- `GET /evaluations/compare`

## 5) Real-time Quality
- `GET /quality/live?run_id={id}` : 실시간 지연/비용/검색품질 요약

## 6) 표준 응답 포맷
```json
{ "success": true, "data": {}, "error": null, "trace_id": "..." }
```

## 7) 표준 에러 코드
- `INVALID_ARGUMENT`
- `UNAUTHORIZED`
- `FORBIDDEN`
- `NOT_FOUND`
- `CONFLICT`
- `RATE_LIMITED`
- `INTERNAL_ERROR`
