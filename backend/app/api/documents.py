import logging
import uuid
from pathlib import Path

from fastapi import APIRouter,Depends, File, HTTPException, UploadFile

from app.config import settings
from app.database import chroma, metadata
from app.models.schemas import DocumentListResponse, DocumentUploadResponse,  DocumentDetailResponse, DocumentDeleteResponse
from app.multilingual.language_detection import detect_language
from app.rag.chunker import chunk_document
from app.rag.document_loader import (
    EmptyDocumentError,
    UnsupportedFileTypeError,
    extract_text,
)
from app.core.security import get_current_user_id
from app.rag.embeddings import embed_texts

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...),current_user_id: str = Depends(get_current_user_id),):
    # --- Validate file type up front ---
    ext = Path(file.filename).suffix.lower()
    if ext not in {".pdf", ".txt", ".docx"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload PDF, TXT, or DOCX.",
        )

    # --- Validate file size ---
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.max_file_size_mb:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds the {settings.max_file_size_mb}MB size limit.",
        )

    document_id = f"DOC_{uuid.uuid4().hex[:10].upper()}"
    saved_path = UPLOAD_DIR / f"{document_id}{ext}"
    saved_path.write_bytes(contents)

    await metadata.create_document(
        document_id=document_id,
        filename=file.filename,
        user_id=current_user_id,
        file_size=len(contents),
        file_type=ext.lstrip("."),
    )

    try:
        # 1. Extract text
        pages = extract_text(saved_path)

        # 2. Detect document language from a sample of its text
        sample_text = " ".join(p.text for p in pages)[:2000]
        language = detect_language(sample_text)

        # 3. Chunk
        chunks = chunk_document(
            document_id=document_id,
            pages=pages,
            chunk_size_words=settings.chunk_size_words,
            overlap_words=settings.chunk_overlap_words,
        )
        if not chunks:
            raise EmptyDocumentError("No readable text was found in this document.")

        # 4. Embed
        chunk_texts = [c.text for c in chunks]
        vectors = embed_texts(chunk_texts)

        # 5. Store in vector DB
        chunk_ids = [c.chunk_id for c in chunks]
        metadatas = [
            {
                "document_id": document_id,
                "filename": file.filename,
                "page": c.page_start,
            }
            for c in chunks
        ]
        chroma.add_chunks(
            chunk_ids=chunk_ids,
            texts=chunk_texts,
            embeddings=vectors,
            metadatas=metadatas,
        )

        # 6. Mark ready in metadata DB
        await metadata.mark_ready(document_id, language=language, chunk_count=len(chunks))

        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            status="ready",
            chunk_count=len(chunks),
        )

    except (UnsupportedFileTypeError, EmptyDocumentError) as exc:
        await metadata.mark_failed(document_id, str(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Document processing failed for %s", document_id)
        await metadata.mark_failed(document_id, "Unexpected processing error.")
        raise HTTPException(
            status_code=500, detail="Unable to process this document. Please try again."
        ) from exc


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    current_user_id: str = Depends(get_current_user_id),
):
    docs = await metadata.list_documents(
        user_id=current_user_id
    )

    return DocumentListResponse(
        documents=docs,
        total=len(docs),
    )

@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
)
async def get_document_details(
    document_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    document = await metadata.get_document(document_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    if document.user_id != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this document.",
        )

    return DocumentDetailResponse(document=document)

@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(
    document_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    doc = await metadata.get_document(document_id)

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    # Make sure users can delete only their own documents
    if doc.user_id != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete this document.",
        )

    # Delete chunks from ChromaDB
    chroma.delete_document_chunks(document_id)

    # Delete metadata record
    await metadata.delete_document(document_id)

    # Delete uploaded file
    for f in UPLOAD_DIR.glob(f"{document_id}.*"):
        f.unlink(missing_ok=True)

    return DocumentDeleteResponse(
        document_id=document_id,
        message="Document deleted successfully",
    )