# Next PR Plan v1 - Rachel Agent

## 목표
다음 PR은 초기 스캐폴드 이후 핵심 개발을 위한 기반 강화를 목표로 한다.

## 범위 (Proposed)
1. DB 마이그레이션 v0
   - documents, document_revisions, chunks, pipeline_jobs, queries 테이블
2. API 확장
   - `GET /api/v1/documents/{id}`
   - `POST /api/v1/rag/answer` (stub)
3. 서비스 계층 정리
   - in-memory store 추상화 인터페이스 도입
   - PostgreSQL/Qdrant 연동 지점 분리
4. 테스트 확장
   - API 상세 조회 테스트
   - RAG answer stub 테스트
   - chunk preview edge case 추가

## 완료 기준 (DoD)
- 신규 API 2개 이상 구현 및 테스트 포함
- migration 파일 추가
- README에 실행/검증 절차 반영
- 테스트 결과는 실행 환경 한계 포함하여 정확히 기재

## 리스크
- 네트워크 제한으로 `pip install` 실패 가능
- 외부 의존성 부재 시 통합테스트 제한

## 대응
- 단위/스모크 테스트 우선
- CI 환경에서 full test 수행
