"""
Endpoints for the "Chat History" page: list a user's past conversations,
open one to replay its messages, or delete it.

Reads from the same app/database/chat_sessions.py store that chat.py
writes to.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user_id
from app.database import chat_sessions
from app.models.schemas import (
    ChatSessionListResponse,
    ChatSessionResponse,
    MessageResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat/sessions", tags=["chat-history"])


@router.get("", response_model=ChatSessionListResponse)
async def get_sessions(current_user_id: str = Depends(get_current_user_id)):
    """Return every chat session belonging to the signed-in user, newest first."""
    sessions = await chat_sessions.list_sessions(user_id=current_user_id)
    return ChatSessionListResponse(sessions=sessions, total=len(sessions))


@router.get("/{session_id}", response_model=ChatSessionResponse)
async def get_session_detail(
    session_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    """Return one session plus its full message history, oldest message first."""
    result = await chat_sessions.get_session(
        session_id=session_id, user_id=current_user_id
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    session, messages = result
    return ChatSessionResponse(session=session, messages=messages)


@router.delete("/{session_id}", response_model=MessageResponse)
async def remove_session(
    session_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    """Delete a chat session and its messages."""
    deleted = await chat_sessions.delete_session(
        session_id=session_id, user_id=current_user_id
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    return MessageResponse(message="Chat session deleted.")