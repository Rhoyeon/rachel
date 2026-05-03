# Testing Strategy v1.0 - Rachel Agent

Rachel Agent는 **사용자 입력으로 RAG+VectorDB를 자동 구축**하고, 품질을 실시간으로 확인·개선해야 하므로 테스트를 기능/품질/운영 3계층으로 수행한다.

## 1. 테스트 원칙
- Shift-left: PR 단계에서 자동 검증 우선
- Reproducible: 동일 데이터/동일 config 재실행 가능
- Evidence-first: 모든 결과는 trace_id/run_id로 추적
- Quality gate: 기준 미달 시 배포 차단

## 2. 테스트 계층

### 2.1 Unit Test
대상:
- 파서 어댑터, 전처리 규칙, 청킹 알고리즘
- 임베딩 프로파일 유효성 검증
- API 요청/응답 스키마, 에러코드 매핑

합격 기준:
- 핵심 모듈 라인 커버리지 80% 이상
- 치명 버그 0

### 2.2 Integration Test
대상:
- 업로드 -> 파싱 -> 전처리 -> 청킹 -> 임베딩 -> 인덱싱 E2E
- 실패/재시도/부분 재실행
- 메타데이터/스토리지/벡터DB 정합성

합격 기준:
- 표준 샘플 문서셋 처리 성공률 95% 이상
- 파이프라인 실패 시 재시도 복구율 95% 이상

### 2.3 Retrieval/RAG Quality Test
대상:
- 검색 품질: Recall@k, MRR, nDCG
- 생성 품질: RAGAS(faithfulness, answer_relevancy, context_precision, context_recall)
- 근거 표시 품질: citation completeness

합격 기준(초기값):
- faithfulness >= 0.80
- answer_relevancy >= 0.78
- context_precision >= 0.75
- citation completeness = 100%

### 2.4 Performance/Cost Test
대상:
- p95 latency(검색/응답)
- 처리량(TPS/QPS)
- 토큰 비용/문서당 처리비

합격 기준(초기값):
- Search p95 < 1.5s
- RAG Answer p95 < 4.0s
- 비용 초과 알림 임계치 설정

### 2.5 Security/DR Test
대상:
- 권한(RBAC), 접근통제, 민감문서 필터
- 백업/복구 리허설(PITR, snapshot 복원)

합격 기준:
- 권한 우회 0건
- DR 리허설에서 RPO/RTO 목표 충족

## 3. 테스트 데이터 전략
- Golden QA Set: 도메인별 최소 100문항
- 문서셋: 표준문서/가이드/산출물 혼합
- Drift Set: 신규/개정 문서 반영용
- Adversarial Set: 모호한 질의, 충돌 규칙, 오래된 버전 참조

## 4. CI/CD 품질 게이트

### 4.1 PR 게이트
- **필수(Mandatory)**
  - unit (`pytest -m "not api and not ragas_optional"`)
  - API smoke (FastAPI runtime available 시)
- **선택(Optional)**
  - ragas smoke (`pytest -m "ragas_optional"`)
  - optional 경로는 non-blocking으로 운영하되 결과 기록은 필수

### 4.1.1 환경 제약 표준 문구
환경 제약으로 API 테스트를 실행하지 못한 경우 PR/릴리즈 노트에 아래 문구를 그대로 사용한다:

> API tests were skipped due to missing FastAPI runtime dependency in the current environment.

### 4.2 Main 게이트
- full integration
- full quality eval(RAGAS + retrieval)
- 성능 회귀 체크

### 4.3 Release 게이트
- KPI/SLO 충족 여부
- 보안 점검 통과
- DR 점검 결과 첨부

## 5. 실시간 운영 모니터링
- live dashboard: p95 latency, token cost, retrieval hit ratio
- 알람: 지표 임계치 이탈 시 Slack/PagerDuty
- 주간 리포트: run 추세, 비용 추세, 실패 원인 Top N

## 6. 역할과 책임
- Platform: 파이프라인 안정성, 인프라, DR
- ML/AI: 청킹/임베딩/리트리버/평가 지표 튜닝
- Product: KPI 승인/변경, 품질 기준 결정
- QA: 게이트 준수 확인, 회귀 시나리오 운영

## 7. 테스트 운영 캘린더
- 매 PR: unit + integration smoke + ragas smoke
- 매일: 배치 full eval
- 매주: 회귀 리뷰/임계치 조정
- 분기: DR 리허설, 보안 감사
