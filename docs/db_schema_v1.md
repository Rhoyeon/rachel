# DB Schema v1.2 - Rachel Agent

Rachel Agent는 **사용자 입력으로 RAG+VectorDB를 자동 구축**하고, 실시간 품질 확인을 위해 실험/평가/관측 데이터를 함께 저장한다.

## 1. 핵심 엔터티
- organizations, users
- documents, document_revisions, artifacts
- chunks, embedding_profiles, chunk_embeddings
- indexes, index_members
- queries, query_results, rag_answers
- experiments, experiment_runs
- evaluation_datasets, evaluation_results
- pipeline_jobs, audit_logs
- quality_live_snapshots

## 2. 관계 요약
- documents 1:N document_revisions
- document_revisions 1:N artifacts/chunks/pipeline_jobs
- chunks 1:N chunk_embeddings
- experiments 1:N experiment_runs 1:N evaluation_results
- experiment_runs 1:N quality_live_snapshots
- queries 1:N query_results + 1:1 rag_answers(선택)

## 3. 저장 원칙
- 대용량 본문/산출물은 S3 URI만 DB에 저장
- 벡터 본문은 Qdrant, DB에는 vector_id 참조
- 모든 run은 config jsonb와 함께 저장해 재현성 보장

## 4. 권장 인덱스
- documents(org_id, status, uploaded_at desc)
- chunks(document_revision_id, chunk_index)
- pipeline_jobs(document_revision_id, stage, status)
- evaluation_results(experiment_run_id, metric_name)
- quality_live_snapshots(experiment_run_id, captured_at desc)
