# Wireframes v1.2 - Rachel Agent

Rachel Agent는 **사용자 입력으로 RAG+VectorDB를 자동 구축**하고, 품질을 실시간 확인하는 경험을 중심으로 UI를 구성한다.

## 필수 화면
1. 문서 업로드/처리현황
2. Chunking Playground
3. Embedding Playground
4. Search + RAG Answer
5. Evaluation(RAGAS 비교)
6. Live Quality Dashboard

## 화면별 핵심 UI
- 업로드: 문서 상태, 실패 사유, 재처리 버튼
- Chunking: strategy/size/overlap 설정, preview, 통계
- Embedding: 모델 선택, 비용/지연 비교, 검색 결과 비교
- Search/RAG: 답변 + 근거 패널(문서/버전/페이지/섹션)
- Evaluation: run 목록, metric chart, 비교표
- Live Quality: p95 latency, token cost, retrieval hit ratio 실시간 카드

## 공통 UX 규칙
- 모든 응답에 trace_id 및 citation 표시
- 실험 config snapshot 고정 표시
- 실패 시 사용자 액션 가능한 에러 메시지 제공
