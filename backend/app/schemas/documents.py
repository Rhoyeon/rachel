from pydantic import BaseModel


class DocumentCreateRequest(BaseModel):
    title: str
    doc_type: str
    content: str


class DocumentItem(BaseModel):
    id: str
    title: str
    doc_type: str
    status: str
