"""Pydantic models describing every API request/response body."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ============================================================
# Common
# ============================================================

class MessageResponse(BaseModel):
    message: str


# ============================================================
# User Schemas
# ============================================================

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    password: Optional[str] = Field(
        default=None,
        min_length=8,
        max_length=128,
    )


class UserMetadata(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True


class UserResponse(BaseModel):
    user: UserMetadata


class UserListResponse(BaseModel):
    users: List[UserMetadata]


# ============================================================
# Authentication Schemas
# ============================================================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserMetadata


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutResponse(BaseModel):
    message: str = "Logged out successfully"


# ============================================================
# Document Schemas
# ============================================================

class DocumentMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    user_id: str

    filename: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None

    language: Optional[str] = None
    uploaded_at: datetime

    chunk_count: int = 0

    status: str = "processing"
    # processing | ready | failed

    error_message: Optional[str] = None


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    chunk_count: int = 0


class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]
    total: int


class DocumentDetailResponse(BaseModel):
    document: DocumentMetadata


class DocumentDeleteResponse(BaseModel):
    document_id: str
    message: str = "Document deleted successfully"


# ============================================================
# Chat Schemas
# ============================================================

class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    document_ids: Optional[List[str]] = None

    top_k: Optional[int] = Field(
        default=None,
        ge=1,
        le=50,
    )

    language: Optional[str] = None

    session_id: Optional[str] = None
    # Pass the session_id from a previous ChatResponse to continue that
    # conversation. Omit it to start a new chat session.


class SourceReference(BaseModel):
    document: str
    document_id: str

    page: Optional[int] = None
    chunk_id: str

    similarity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
    )

    text: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    language: str

    sources: List[SourceReference]

    grounded: bool

    session_id: str
    # The chat session (new or continued) this exchange was saved under.


# ============================================================
# Chat History Schemas
# ============================================================

class ChatMessage(BaseModel):
    message_id: str
    role: str
    # user | assistant | system

    content: str
    created_at: datetime


class ChatSessionMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: str
    user_id: str

    title: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ChatSessionResponse(BaseModel):
    session: ChatSessionMetadata
    messages: List[ChatMessage]


class ChatSessionListResponse(BaseModel):
    sessions: List[ChatSessionMetadata]
    total: int


# ============================================================
# Health Schemas
# ============================================================

class HealthResponse(BaseModel):
    status: str

    embedding_model_loaded: bool
    vector_db_connected: bool
    metadata_db_connected: bool

    ollama_connected: bool
    ollama_model_available: bool


# ============================================================
# Error Schemas
# ============================================================

class ErrorResponse(BaseModel):
    detail: str


# ============================================================
# Pagination
# ============================================================

class PaginationParams(BaseModel):
    page: int = Field(
        default=1,
        ge=1,
    )

    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
    )