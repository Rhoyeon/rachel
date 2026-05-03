# PR Checklist - Rachel Agent

## 공통
- [ ] 변경 목적과 범위를 PR 설명에 명시
- [ ] 관련 문서(PRD/API/Architecture) 링크 명시
- [ ] 보안/운영 영향 여부 명시

## 코드
- [ ] 로컬에서 실행 가능한 최소 검증 수행
- [ ] 실패한 테스트가 있으면 원인과 환경 제약을 명시
- [ ] 불필요 산출물(`__pycache__`, 바이너리 등) 제외

## 테스트 리포팅
- [ ] 실행 명령 정확히 기재
- [ ] pass/fail/warn 구분 명확히 기재
- [ ] "실행하지 않았음" 또는 "환경 제약"은 명시적으로 작성
- [ ] Mandatory vs Optional 테스트 구분 기재 (`unit`/`api`/`ragas_optional`)
- [ ] API skip 시 표준 문구 사용:
  - `API tests were skipped due to missing FastAPI runtime dependency in the current environment.`
