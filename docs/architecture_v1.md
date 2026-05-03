# Architecture v1.2 - Rachel Agent

Rachel Agent는 **사용자 입력으로 RAG+VectorDB를 자동 구축**하고, 품질을 실시간으로 검증할 수 있도록 설계한다.

## 1. 컴포넌트
1. Web UI (Next.js)
2. API (FastAPI)
3. Worker (Celery + Redis)
4. PostgreSQL (메타데이터/실험/잡)
5. Qdrant (임베딩 벡터)
6. S3-compatible Storage (원본/산출물)
7. Evaluation Engine (RAGAS)

## 2. 처리 흐름
Upload -> Parse -> Normalize -> Chunk -> Embed -> Index -> Query/RAG -> Evaluate

## 3. 서비스 경계
- Ingestion: 파일 등록/버전/메타데이터
- Processing: 파싱/정규화/청킹
- Retrieval: 인덱스/검색/재랭킹
- Generation: RAG 응답/근거 생성
- Evaluation: 실험 실행/지표 저장/비교
- Observability: 실시간 품질/비용/지연 모니터링

## 4. 장애/복구 설계
- 단계별 job state: queued/running/success/failed
- 단계별 재시도 및 부분 재실행
- artifact immutable 저장으로 재현성 확보

## 5. 관측성
- request/job trace id 전파
- stage latency, failure rate, token cost 계측
- 실험 run별 config snapshot과 metric 연결
