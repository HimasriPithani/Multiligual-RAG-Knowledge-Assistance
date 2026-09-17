from pathlib import Path

import fitz
import pytest
from docx import Document as DocxDocument

from app.rag.document_loader import (
    EmptyDocumentError,
    UnsupportedFileTypeError,
    extract_text,
)


def test_extract_txt(tmp_path: Path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("Hello world.\nThis is a test document.", encoding="utf-8")

    pages = extract_text(file_path)

    assert len(pages) == 1
    assert "Hello world" in pages[0].text


def test_extract_docx(tmp_path: Path):
    file_path = tmp_path / "sample.docx"
    doc = DocxDocument()
    doc.add_paragraph("This is a docx test paragraph.")
    doc.save(file_path)

    pages = extract_text(file_path)

    assert len(pages) == 1
    assert "docx test paragraph" in pages[0].text


def test_extract_pdf(tmp_path: Path):
    file_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "This is a PDF test page.")
    doc.save(file_path)
    doc.close()

    pages = extract_text(file_path)

    assert len(pages) == 1
    assert pages[0].page_number == 1
    assert "PDF test page" in pages[0].text


def test_unsupported_file_type(tmp_path: Path):
    file_path = tmp_path / "sample.xyz"
    file_path.write_text("irrelevant")

    with pytest.raises(UnsupportedFileTypeError):
        extract_text(file_path)


def test_empty_document_raises(tmp_path: Path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("   \n\n   ")

    with pytest.raises(EmptyDocumentError):
        extract_text(file_path)
