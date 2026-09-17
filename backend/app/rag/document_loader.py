"""
Extracts clean text (with page numbers) from uploaded documents.

Supported formats: PDF (PyMuPDF), TXT (plain read), DOCX (python-docx).
Every extractor returns the same shape so the rest of the pipeline
(chunker, embeddings, retriever) never needs to know which format
the original file was.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

import fitz  # PyMuPDF
from docx import Document as DocxDocument


class UnsupportedFileTypeError(Exception):
    pass


class EmptyDocumentError(Exception):
    pass


@dataclass
class PageText:
    page_number: int
    text: str


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".docx"}


def _clean_text(text: str) -> str:
    """Remove extraction artifacts: excess whitespace, repeated blank lines."""
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_pdf(path: Path) -> List[PageText]:
    pages: List[PageText] = []
    with fitz.open(path) as doc:
        for i, page in enumerate(doc, start=1):
            raw = page.get_text("text")
            cleaned = _clean_text(raw)
            if cleaned:
                pages.append(PageText(page_number=i, text=cleaned))
    return pages


def _extract_txt(path: Path) -> List[PageText]:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    cleaned = _clean_text(raw)
    if not cleaned:
        return []
    # Plain text has no native pages; treat the whole file as page 1.
    return [PageText(page_number=1, text=cleaned)]


def _extract_docx(path: Path) -> List[PageText]:
    doc = DocxDocument(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    raw = "\n".join(paragraphs)
    cleaned = _clean_text(raw)
    if not cleaned:
        return []
    # python-docx has no reliable page concept either; treat as page 1.
    return [PageText(page_number=1, text=cleaned)]


def extract_text(path: Path) -> List[PageText]:
    """
    Dispatches to the correct extractor based on file extension.

    Raises:
        UnsupportedFileTypeError: extension isn't pdf/txt/docx
        EmptyDocumentError: extraction produced no readable text
    """
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{ext}'. Please upload PDF, TXT, or DOCX."
        )

    if ext == ".pdf":
        pages = _extract_pdf(path)
    elif ext == ".txt":
        pages = _extract_txt(path)
    else:  # .docx
        pages = _extract_docx(path)

    if not pages:
        raise EmptyDocumentError("No readable text was found in this document.")

    return pages
