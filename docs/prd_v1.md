# PRD v1.2 - Rachel Agent

Rachel Agent는 **사용자 입력으로 RAG+VectorDB를 자동 구축**하고, 전처리/청킹/임베딩/검색 품질을 실시간으로 확인·개선할 수 있는 차별화된 서비스다.

## 1. 배경
개발 표준문서/가이드/산출물이 다양한 포맷으로 흩어져 있어 검색 정확도와 최신성 보장이 어렵다. Rachel Agent는 업로드 즉시 자동 파이프라인을 구성하고 실험 기반으로 품질을 지속 개선한다.

## 2. 목표
- 문서 업로드 후 자동 처리(분석/전처리/청킹/임베딩/인덱싱)
- Playground 기반 청킹/임베딩 시뮬레이션
- 품질 실시간 확인(검색 결과/근거/비용/지연/지표)
- RAGAS 성능평가 및 run 비교
- 근거 기반 답변(문서/버전/페이지/섹션)

## 3. 사용자
- Admin: 시스템/권한/모델 운영
- Manager: 문서 품질/실험 관리
- User: 검색/RAG 질의

## 4. MVP 범위
### In
- 포맷: PDF/DOCX/MD/TXT/HTML
- 파이프라인: ingest -> parse -> preprocess -> chunk -> embed -> index
- 검색: hybrid retrieval + optional rerank
- 평가: ragas(faithfulness, answer_relevancy, context_precision, context_recall)

### Out
- 문서 협업 편집
- 복잡한 결재 워크플로우
- 실시간 공동 편집

## 5. KPI / SLO
- 파이프라인 성공률 >= 95%
- 답변 근거 표기율 = 100%
- Search p95 < 1.5s (10만 chunk 기준 목표)
- 평가 run 재현성 100%(동일 config 동일 데이터 기준)

## 6. 릴리즈
- R1(6주): MVP 전체
- R1.1: OCR/HWP, 권한 고도화, 평가 자동 리그레션
