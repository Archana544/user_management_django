# tests/test_text_processing.py

from utils.vector_store import clean_text, chunk_text


def test_clean_text_removes_extra_spaces():
    text = "Hello   world\n\nThis is   test"
    cleaned = clean_text(text)

    assert cleaned == "Hello world This is test"


def test_clean_text_fixes_ocr_issue():
    text = "DearPlease find attached"
    cleaned = clean_text(text)

    assert "Dear Please" in cleaned


def test_chunk_text_basic():
    text = "word " * 300
    chunks = chunk_text(text, chunk_size=100, overlap=20)

    assert len(chunks) > 1
    assert all(isinstance(c, str) for c in chunks)