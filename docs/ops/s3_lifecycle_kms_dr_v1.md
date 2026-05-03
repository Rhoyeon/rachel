# S3/Lifecycle/KMS/DR 운영안 v1.2 - Rachel Agent

Rachel Agent는 **사용자 입력으로 RAG+VectorDB를 자동 구축**하는 서비스이며, 운영안은 자동화 산출물과 실시간 품질 데이터 보호를 전제로 한다.

## S3 키 컨벤션
s3://{bucket}/{env}/{org_id}/{project_id}/{document_id}/{revision}/
- original/{filename}
- parsed/{parser_version}/document.json
- normalized/{preprocess_version}/normalized.json
- chunks/{chunk_profile_id}/chunks.jsonl
- embeddings/{embedding_profile_id}/manifest.json
- eval/{experiment_run_id}/ragas_result.json
- quality/live/{experiment_run_id}/{timestamp}.json

## Lifecycle
- original: 0-30일 Standard, 31-180일 Standard-IA, 이후 Glacier IR
- artifacts(parsed/normalized/chunks/embeddings): 0-30 Standard, 31-90 IA, 이후 Glacier IR
- quality/live: 0-14일 Standard, 15일 이후 IA, 90일 이후 삭제(집계본은 별도 보관)
- tmp/failed: 14~30일 후 삭제
- playground cache: 30일 후 삭제

## 암호화(KMS)
- SSE-KMS 강제
- 환경별 CMK 분리(dev/stg/prod)
- TLS 강제 및 Public Access Block 활성화

## 백업/복구
- S3: Versioning + Cross-Region Replication
- PostgreSQL: 일일 Full + PITR(WAL)
- Qdrant: 일일 snapshot(또는 manifest 기반 재색인)
- 목표: RPO(DB 15분), RTO(핵심 2~4시간)
