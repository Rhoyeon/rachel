from uuid import uuid4
import logging

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile

from app.core.deps import get_chunk_repository, get_document_repository, get_eval_store, get_llm_client, get_vector_store
from app.schemas.common import ApiResponse
from app.schemas.documents import DocumentCreateRequest
from app.services.chunking import fixed_chunk
from app.services.embedding import embed_text
from app.services.evaluation import build_config_hash, compare_runs, compute_retrieval_metrics, run_ragas_evaluation, run_simple_evaluation, summarize_runs
from app.services.ingestion import build_chunks_for_document
from app.services.llm import LLMClient, StubLLMClient
from app.services.parsing import parse_document_bytes, parse_document_content
from app.services.preprocess import preprocess_text
from app.services.eval_store import EvalRunStore
from app.services.repository import ChunkRepository, DocumentRepository
from app.services.vector_store import InMemoryVectorStore, QdrantVectorStore, VectorPoint
from app.services.retrieval import bm25_score, simple_rerank

logger = logging.getLogger("rachel.api")
router = APIRouter(prefix="/api/v1")


def _tid(request: Request) -> str:
    return getattr(request.state, "trace_id", str(uuid4()))


@router.post("/documents", response_model=ApiResponse)
def post_document(req: DocumentCreateRequest, request: Request, repo: DocumentRepository = Depends(get_document_repository)) -> ApiResponse:
    parsed = parse_document_content(req.content, req.doc_type)
    normalized = preprocess_text(parsed.text)
    doc = repo.create(req.title, req.doc_type, normalized)
    logger.info("document created", extra={"trace_id": _tid(request)})
    return ApiResponse(data={"id": doc.id, "status": doc.status, "parser_used": parsed.parser_used}, trace_id=_tid(request))



@router.post("/documents/upload", response_model=ApiResponse)
async def upload_document(
    request: Request,
    title: str = Form(...),
    doc_type: str = Form(...),
    file: UploadFile = File(...),
    repo: DocumentRepository = Depends(get_document_repository),
) -> ApiResponse:
    raw = await file.read()
    parsed = parse_document_bytes(raw, doc_type)
    normalized = preprocess_text(parsed.text)
    doc = repo.create(title, doc_type, normalized)
    return ApiResponse(data={"id": doc.id, "status": doc.status, "parser_used": parsed.parser_used, "filename": file.filename}, trace_id=_tid(request))

@router.get("/documents", response_model=ApiResponse)
def get_documents(request: Request, doc_type: str | None = None, status: str | None = None, repo: DocumentRepository = Depends(get_document_repository)) -> ApiResponse:
    docs = []
    for d in repo.list():
        if doc_type and d.doc_type.lower() != doc_type.lower():
            continue
        if status and d.status.lower() != status.lower():
            continue
        docs.append({"id": d.id, "title": d.title, "doc_type": d.doc_type, "status": d.status})
    return ApiResponse(data={"items": docs}, trace_id=_tid(request))

@router.post("/playground/chunk/preview", response_model=ApiResponse)
def chunk_preview(payload: dict, request: Request) -> ApiResponse:
    chunks = fixed_chunk(payload.get("text", ""), size=int(payload.get("size", 200)), overlap=int(payload.get("overlap", 20)))
    return ApiResponse(data={"chunks": chunks, "count": len(chunks)}, trace_id=_tid(request))

@router.get("/documents/{document_id}", response_model=ApiResponse)
def get_document_detail(document_id: str, request: Request, repo: DocumentRepository = Depends(get_document_repository)) -> ApiResponse:
    doc = repo.get(document_id)
    if not doc:
        return ApiResponse(success=False, error="NOT_FOUND", data=None, trace_id=_tid(request))
    return ApiResponse(data={"id": doc.id, "title": doc.title, "doc_type": doc.doc_type, "status": doc.status, "content": doc.content}, trace_id=_tid(request))

@router.post("/documents/{document_id}/chunks", response_model=ApiResponse)
def build_document_chunks(document_id: str, payload: dict, request: Request, repo: DocumentRepository = Depends(get_document_repository), chunk_repo: ChunkRepository = Depends(get_chunk_repository), vector_store: InMemoryVectorStore | QdrantVectorStore = Depends(get_vector_store)) -> ApiResponse:
    doc = repo.get(document_id)
    if not doc:
        return ApiResponse(success=False, error="NOT_FOUND", data=None, trace_id=_tid(request))

    chunk_records = build_chunks_for_document(doc, size=int(payload.get("size", 200)), overlap=int(payload.get("overlap", 20)))
    saved = chunk_repo.save_for_document(document_id, [c.text for c in chunk_records])
    points = [VectorPoint(id=f"{document_id}-{c.chunk_index}", document_id=document_id, chunk_index=c.chunk_index, vector=embed_text(c.text), text=c.text) for c in chunk_records]
    vector_store.upsert_points(points)
    return ApiResponse(data={"document_id": doc.id, "chunk_count": saved, "chunks": [{"chunk_index": c.chunk_index, "text": c.text} for c in chunk_records]}, trace_id=_tid(request))

@router.post("/rag/answer", response_model=ApiResponse)
def rag_answer(payload: dict, request: Request, repo: DocumentRepository = Depends(get_document_repository), vector_store: InMemoryVectorStore | QdrantVectorStore = Depends(get_vector_store), llm: LLMClient = Depends(get_llm_client)) -> ApiResponse:
    query = payload.get("query", "").strip().lower()
    query_vector = embed_text(query)
    hits = vector_store.search(query_vector, top_k=3)

    citations = []
    contexts = []
    for h in hits:
        doc = repo.get(h.document_id)
        title = doc.title if doc else h.document_id
        contexts.append(h.text)
        citations.append({"document_id": h.document_id, "title": title, "snippet": h.text[:120]})

    try:
        llm_result = llm.generate(query=query, contexts=contexts)
    except Exception:
        llm_result = StubLLMClient().generate(query=query, contexts=contexts)

    return ApiResponse(data={"answer": llm_result.text, "citations": citations, "model": llm_result.model}, trace_id=_tid(request))

@router.post("/evaluations/runs", response_model=ApiResponse)
def run_evaluation(payload: dict, request: Request, eval_store: EvalRunStore = Depends(get_eval_store)) -> ApiResponse:
    name = payload.get("name", "default")
    samples = payload.get("samples", [])
    eval_backend = payload.get("eval_backend", "simple")
    strict = eval_backend == "ragas_strict"
    run = run_ragas_evaluation(name=name, samples=samples, strict=strict) if eval_backend in {"ragas", "ragas_strict"} else run_simple_evaluation(name=name, samples=samples)

    retrieval_samples = payload.get("retrieval_samples", [])
    if retrieval_samples:
        k = int(payload.get("top_k", 5))
        run.metrics.update(compute_retrieval_metrics(retrieval_samples, k=k))

    run.metrics["strict_eval_requested"] = bool(strict)
    run.metrics["strict_eval_passed"] = bool(strict and run.backend == "ragas")

    config = payload.get("config", {})
    run_tags = payload.get("run_tags", [])
    run.metrics["_meta"] = {
        "config_hash": build_config_hash(config),
        "run_tags": run_tags if isinstance(run_tags, list) else [],
    }

    eval_store.save(run)
    return ApiResponse(data=run.__dict__, trace_id=_tid(request))


@router.get("/evaluations/runs/{run_id}", response_model=ApiResponse)
def get_evaluation_run(run_id: str, request: Request, eval_store: EvalRunStore = Depends(get_eval_store)) -> ApiResponse:
    row = eval_store.get(run_id)
    if not row:
        return ApiResponse(success=False, error="NOT_FOUND", data=None, trace_id=_tid(request))
    return ApiResponse(data=row, trace_id=_tid(request))



@router.get("/evaluations/compare", response_model=ApiResponse)
def compare_evaluations(
    request: Request,
    run_ids: str | None = Query(default=None, description="Comma separated run ids"),
    metric_keys: str | None = Query(default=None, description="Comma separated metric keys"),
    sort_by: str | None = Query(default=None, description="Sort rows by a metric key"),
    strict_only: bool = Query(default=False, description="Filter strict-eval runs only"),
    strict_mode: str = Query(default="requested", description="requested|passed"),
    baseline_run_id: str | None = Query(default=None, description="Baseline run for delta calculation"),
    min_query_count: int = Query(default=0, description="Minimum query_count filter"),
    run_tag: str | None = Query(default=None, description="Filter by run tag"),
    weights: str | None = Query(default=None, description="JSON object for metric weights"),
    eval_store: EvalRunStore = Depends(get_eval_store),
) -> ApiResponse:
    runs = eval_store.list()
    if run_ids:
        allow = {x.strip() for x in run_ids.split(",") if x.strip()}
        runs = [r for r in runs if r.get("run_id") in allow]

    metric_list = [m.strip() for m in metric_keys.split(",") if m.strip()] if metric_keys else None
    weight_obj = None
    if weights:
        import json
        try:
            parsed = json.loads(weights)
            weight_obj = parsed if isinstance(parsed, dict) else None
        except Exception:
            weight_obj = None
    data = compare_runs(runs, metric_keys=metric_list, sort_by=sort_by, strict_only=strict_only, strict_mode=strict_mode, baseline_run_id=baseline_run_id, min_query_count=min_query_count, run_tag=run_tag, weights=weight_obj)
    return ApiResponse(data=data, trace_id=_tid(request))



@router.get("/evaluations/metrics", response_model=ApiResponse)
def get_evaluation_metric_rows(
    request: Request,
    run_id: str | None = Query(default=None),
    metric_name: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    sort_by: str = Query(default="metric_value"),
    sort_order: str = Query(default="desc"),
    eval_store: EvalRunStore = Depends(get_eval_store),
) -> ApiResponse:
    rows = eval_store.list_metric_rows(run_id=run_id, metric_name=metric_name)

    reverse = sort_order.lower() == "desc"
    if sort_by in {"metric_value", "metric_name", "run_id"}:
        rows = sorted(rows, key=lambda r: r.get(sort_by), reverse=reverse)

    total = len(rows)
    start = (page - 1) * page_size
    end = start + page_size
    page_rows = rows[start:end]
    return ApiResponse(data={"items": page_rows, "count": len(page_rows), "total": total, "page": page, "page_size": page_size}, trace_id=_tid(request))



@router.get("/evaluations/summary", response_model=ApiResponse)
def get_evaluations_summary(request: Request, eval_store: EvalRunStore = Depends(get_eval_store)) -> ApiResponse:
    runs = eval_store.list()
    return ApiResponse(data=summarize_runs(runs), trace_id=_tid(request))

@router.get("/evaluations/runs", response_model=ApiResponse)
def get_evaluations(request: Request, eval_store: EvalRunStore = Depends(get_eval_store)) -> ApiResponse:
    return ApiResponse(data={"items": eval_store.list()}, trace_id=_tid(request))

@router.post("/search", response_model=ApiResponse)
def search(payload: dict, request: Request, repo: DocumentRepository = Depends(get_document_repository), vector_store: InMemoryVectorStore | QdrantVectorStore = Depends(get_vector_store)) -> ApiResponse:
    query = payload.get("query", "").strip().lower()
    top_k = int(payload.get("top_k", 5))
    query_vector = embed_text(query)
    lex_w = float(payload.get("lexical_weight", 0.5))
    dense_w = float(payload.get("dense_weight", 0.5))
    title_filter = (payload.get("title_contains") or "").lower()
    doc_type_filter = (payload.get("doc_type") or "").lower()
    status_filter = (payload.get("status") or "").lower()
    vector_hits = vector_store.search(query_vector, top_k=top_k * 4)
    vector_score = {h.document_id: max(0.0, sum(a * b for a, b in zip(query_vector, h.vector))) for h in vector_hits}
    corpus = [d.content for d in repo.list()]
    items = []
    for d in repo.list():
        if title_filter and title_filter not in d.title.lower():
            continue
        if doc_type_filter and d.doc_type.lower() != doc_type_filter:
            continue
        if status_filter and d.status.lower() != status_filter:
            continue
        bm25 = bm25_score(query=query, doc=d.content, corpus=corpus)
        dense = vector_score.get(d.id, 0.0)
        score = lex_w * bm25 + dense_w * dense
        if score > 0:
            items.append({"document_id": d.id, "title": d.title, "snippet": d.content[:200], "score": round(score, 4), "bm25": round(bm25, 4)})
    if payload.get("rerank", False):
        items = simple_rerank(query, items)
    else:
        items.sort(key=lambda x: x["score"], reverse=True)
    return ApiResponse(data={"items": items[:top_k], "retrieval": "hybrid-bm25-dense"}, trace_id=_tid(request))


@router.post("/playground/embed/preview", response_model=ApiResponse)
def embed_preview(payload: dict, request: Request, vector_store: InMemoryVectorStore | QdrantVectorStore = Depends(get_vector_store)) -> ApiResponse:
    text = payload.get("text", "")
    top_k = int(payload.get("top_k", 3))
    vector = embed_text(text)
    neighbors = vector_store.search(vector, top_k=top_k)
    return ApiResponse(
        data={
            "dimension": len(vector),
            "vector": vector,
            "neighbors": [{"document_id": n.document_id, "chunk_index": n.chunk_index, "snippet": n.text[:120]} for n in neighbors],
        },
        trace_id=_tid(request),
    )
