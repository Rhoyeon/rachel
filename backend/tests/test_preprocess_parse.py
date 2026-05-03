from app.services.parsing import parse_document_bytes, parse_document_content
from app.services.preprocess import preprocess_text
import base64


def test_parse_and_preprocess_pipeline():
    raw = "hello   world\r\n\r\n\r\nnext"
    parsed = parse_document_content(raw, "md")
    normalized = preprocess_text(parsed.text)
    assert normalized == "hello world\n\nnext"
    assert parsed.parser_used == "markdown"


def test_parse_document_bytes_plain_text() -> None:
    parsed = parse_document_bytes(b"line1\nline2", "txt")
    assert "line1" in parsed.text
    assert parsed.parser_used == "plain"


def test_parse_document_content_pdf_fallback_decodes_base64_text() -> None:
    payload = base64.b64encode("hello from fallback".encode("utf-8")).decode("utf-8")
    parsed = parse_document_content(payload, "pdf")
    assert "hello from fallback" in parsed.text
    assert parsed.parser_used == "pdf-fallback-plain"
