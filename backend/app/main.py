from uuid import uuid4
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.routes import router as v1_router
from app.core.deps import get_document_repository, get_vector_store
from app.core.logging import configure_logging
from app.services.connectivity import check_postgres, check_vector_store

configure_logging()
logger = logging.getLogger("rachel")

app = FastAPI(title="Rachel Agent API", version="0.3.0")
app.include_router(v1_router)


@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = request.headers.get("x-trace-id", str(uuid4()))
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["x-trace-id"] = trace_id
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "trace_id", str(uuid4()))
    logger.exception("unhandled exception", extra={"trace_id": trace_id})
    return JSONResponse(status_code=500, content={"success": False, "data": None, "error": "INTERNAL_ERROR", "trace_id": trace_id})


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "rachel-agent-api"}


@app.get("/health/dependencies")
def health_dependencies() -> dict:
    repo = get_document_repository()
    vector_store = get_vector_store()
    pg = check_postgres(repo)
    vs = check_vector_store(vector_store)
    overall = "ok" if pg.ok and vs.ok else "degraded"
    return {
        "status": overall,
        "dependencies": {
            pg.name: {"ok": pg.ok, "detail": pg.detail},
            vs.name: {"ok": vs.ok, "detail": vs.detail},
        },
    }
