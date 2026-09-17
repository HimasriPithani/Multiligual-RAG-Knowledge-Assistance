from app.rag.chunker import chunk_document
from app.rag.document_loader import PageText


def test_chunk_document_creates_chunks_within_size_limit():
    long_text = " ".join([f"This is sentence number {i}." for i in range(200)])
    pages = [PageText(page_number=1, text=long_text)]

    chunks = chunk_document("DOC_TEST", pages, chunk_size_words=50, overlap_words=10)

    assert len(chunks) > 1
    for chunk in chunks:
        word_count = len(chunk.text.split())
        # Allow some slack since we never cut a sentence mid-way
        assert word_count <= 70


def test_chunk_document_preserves_overlap():
    text = " ".join([f"Word{i}" for i in range(100)]) + "."
    pages = [PageText(page_number=1, text=text)]

    chunks = chunk_document("DOC_TEST", pages, chunk_size_words=30, overlap_words=5)

    assert len(chunks) >= 2
    # Last words of chunk 1 should reappear at the start of chunk 2
    first_chunk_tail = chunks[0].text.split()[-5:]
    second_chunk_head = chunks[1].text.split()[:5]
    assert first_chunk_tail == second_chunk_head


def test_chunk_document_assigns_chunk_ids_sequentially():
    pages = [PageText(page_number=1, text="Sentence one. Sentence two. Sentence three.")]
    chunks = chunk_document("DOC_XYZ", pages, chunk_size_words=2, overlap_words=0)

    assert chunks[0].chunk_id == "DOC_XYZ_CHUNK_0001"
    if len(chunks) > 1:
        assert chunks[1].chunk_id == "DOC_XYZ_CHUNK_0002"


def test_chunk_document_handles_devanagari_sentence_boundary():
    text = "यह पहला वाक्य है। यह दूसरा वाक्य है। यह तीसरा वाक्य है।"
    pages = [PageText(page_number=1, text=text)]

    chunks = chunk_document("DOC_HI", pages, chunk_size_words=3, overlap_words=0)

    assert len(chunks) >= 1
    assert all(chunk.text for chunk in chunks)
