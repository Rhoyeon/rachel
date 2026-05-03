from pydantic import BaseModel
from typing import Any


class ApiResponse(BaseModel):
    success: bool = True
    data: Any = None
    error: str | None = None
    trace_id: str
