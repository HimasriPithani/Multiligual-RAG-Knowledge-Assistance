"""Pydantic models describing every API request/response body."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    language: Optional[str] = None
    uploaded_at: datetime
    chunk_count: int = 0
    status: str = "processing"  # processing | ready | failed
    error_message: Optional[str] = None


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    chunk_count: int


class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    document_ids: Optional[List[str]] = None  # optional: restrict search to specific docs
    top_k: Optional[int] = None


class SourceReference(BaseModel):
    document: str
    document_id: str
    page: Optional[int] = None
    chunk_id: str
    similarity: float


class ChatResponse(BaseModel):
    answer: str
    language: str
    sources: List[SourceReference]
    grounded: bool  # False if the answer had to fall back to "not found in documents"


class HealthResponse(BaseModel):
    status: str
    embedding_model_loaded: bool
    vector_db_connected: bool
    metadata_db_connected: bool
