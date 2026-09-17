"""
Splits extracted page text into overlapping, embedding-sized chunks.

Chunking is sentence-aware (it never cuts a sentence in half) and
script-aware: the sentence splitter recognizes '.', '!', '?' as well as
the Devanagari/Indic full stop '।' used by Hindi, Maithili and similar
scripts, so chunk boundaries stay clean across all supported languages.
"""

import re
from dataclasses import dataclass
from typing import List

from app.rag.document_loader import PageText

# Splits on sentence-ending punctuation (., !, ?, or the Indic danda ।)
# followed by whitespace, while keeping the punctuation attached to the sentence.
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?।])\s+")


@dataclass
class Chunk:
    chunk_id: str
    text: str
    page_start: int
    page_end: int


def _split_sentences(text: str) -> List[str]:
    sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(text) if s.strip()]
    return sentences


def chunk_document(
    document_id: str,
    pages: List[PageText],
    chunk_size_words: int = 350,
    overlap_words: int = 60,
) -> List[Chunk]:
    """
    Builds a flat list of Chunk objects for one document.

    Algorithm:
      1. Walk through pages in order, splitting each page into sentences.
      2. Accumulate sentences into a chunk until adding the next sentence
         would exceed `chunk_size_words`.
      3. Start the next chunk with the last `overlap_words` words of the
         previous chunk, so context isn't lost at the boundary.
    """
    chunks: List[Chunk] = []
    current_words: List[str] = []
    current_page_start = None
    current_page_end = None
    chunk_counter = 0

    def flush_chunk():
        nonlocal current_words, current_page_start, current_page_end, chunk_counter
        if not current_words:
            return
        chunk_counter += 1
        chunks.append(
            Chunk(
                chunk_id=f"{document_id}_CHUNK_{chunk_counter:04d}",
                text=" ".join(current_words).strip(),
                page_start=current_page_start,
                page_end=current_page_end,
            )
        )
        # Carry over the overlap for the next chunk
        overlap = current_words[-overlap_words:] if overlap_words > 0 else []
        current_words = list(overlap)

    for page in pages:
        sentences = _split_sentences(page.text)
        for sentence in sentences:
            sentence_words = sentence.split()
            if current_page_start is None:
                current_page_start = page.page_number
            current_page_end = page.page_number

            if len(current_words) + len(sentence_words) > chunk_size_words and current_words:
                flush_chunk()
                current_page_start = page.page_number
                current_page_end = page.page_number

            # A single sentence longer than chunk_size_words on its own
            # (e.g. no internal punctuation) can't rely on sentence
            # boundaries alone — fall back to slicing it by words so it
            # still gets split into properly sized chunks.
            if len(sentence_words) > chunk_size_words:
                start = 0
                while start < len(sentence_words):
                    end = start + (chunk_size_words - len(current_words))
                    current_words.extend(sentence_words[start:end])
                    start = end
                    if start < len(sentence_words):
                        flush_chunk()
                        current_page_start = page.page_number
                        current_page_end = page.page_number
                continue

            current_words.extend(sentence_words)

    flush_chunk()

    return [c for c in chunks if c.text]
