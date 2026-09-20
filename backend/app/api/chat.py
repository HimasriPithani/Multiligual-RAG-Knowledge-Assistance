"""
The core RAG endpoint.

Retrieves relevant document chunks, generates a grounded answer,
and streams the answer from Ollama to the frontend.
"""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.core.security import get_current_user_id
from app.database import chat_sessions
from app.models.schemas import (
    ChatRequest,
    ChatSessionListResponse,
    ChatSessionResponse,
    MessageResponse,
)
from app.multilingual.language_detection import detect_language
from app.rag.generator import (
    LLMServiceError,
    generate_answer_stream,
)
from app.rag.prompt import build_prompt
from app.rag.retriever import retrieve_relevant_chunks

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


NOT_FOUND_MESSAGE = {
    "en": "I could not find this information in the uploaded documents.",
    "hi": "मुझे यह जानकारी अपलोड किए गए दस्तावेज़ों में नहीं मिली।",
    "te": "ఈ సమాచారం అప్‌లోడ్ చేసిన పత్రాలలో నాకు కనుగొనబడలేదు.",
}


def make_event(event_type: str, **data) -> str:
    """
    Create one newline-delimited JSON event.
    """
    return json.dumps(
        {
            "type": event_type,
            **data,
        },
        ensure_ascii=False,
    ) + "\n"


@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id),
):
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    # Resolve or create chat session.
    if request.session_id:

        existing = await chat_sessions.get_session(
            session_id=request.session_id,
            user_id=current_user_id,
        )

        if existing is None:
            raise HTTPException(
                status_code=404,
                detail="Chat session not found.",
            )

        session_id = request.session_id

    else:

        session = await chat_sessions.create_session(
            user_id=current_user_id,
            title=request.question[:60],
        )

        session_id = session.session_id

    # Save user message.
    await chat_sessions.add_message(
        session_id=session_id,
        role="user",
        content=request.question,
    )

    language = detect_language(request.question)

    # Retrieve relevant document chunks.
    chunks = retrieve_relevant_chunks(
        question=request.question,
        top_k=request.top_k,
        document_ids=request.document_ids,
    )

    # ---------------------------------------------------------
    # No relevant document information found
    # ---------------------------------------------------------

    if not chunks:

        answer_text = NOT_FOUND_MESSAGE.get(
            language,
            NOT_FOUND_MESSAGE["en"],
        )

        await chat_sessions.add_message(
            session_id=session_id,
            role="assistant",
            content=answer_text,
        )

        async def not_found_stream():

            yield make_event(
                "meta",
                session_id=session_id,
                language=language,
                sources=[],
                grounded=False,
            )

            yield make_event(
                "token",
                content=answer_text,
            )

            yield make_event("done")

        return StreamingResponse(
            not_found_stream(),
            media_type="application/x-ndjson",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    # Build grounded prompt.
    prompt = build_prompt(
        request.question,
        chunks,
    )

    # Prepare source information.
    sources = [
        {
            "document": c.filename,
            "document_id": c.document_id,
            "page": c.page,
            "chunk_id": c.chunk_id,
            "similarity": round(c.similarity, 4),
        }
        for c in chunks
    ]

    async def answer_stream():

        full_answer = ""

        # Send metadata immediately.
        yield make_event(
            "meta",
            session_id=session_id,
            language=language,
            sources=sources,
            grounded=True,
        )

        try:

            async for token in generate_answer_stream(prompt):

                full_answer += token

                yield make_event(
                    "token",
                    content=token,
                )

            # Save the completed answer.
            if full_answer.strip():

                await chat_sessions.add_message(
                    session_id=session_id,
                    role="assistant",
                    content=full_answer.strip(),
                )

            yield make_event("done")

        except LLMServiceError as exc:

            logger.exception(
                "LLM streaming failed"
            )

            yield make_event(
                "error",
                message=str(exc),
            )

        except Exception as exc:

            logger.exception(
                "Unexpected streaming error"
            )

            yield make_event(
                "error",
                message="The local AI service is temporarily unavailable.",
            )

    return StreamingResponse(
        answer_stream(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/chat/sessions",
    response_model=ChatSessionListResponse,
)
async def get_sessions(
    current_user_id: str = Depends(get_current_user_id),
):
    """Returns every chat session belonging to the current user, newest first."""

    sessions = await chat_sessions.list_sessions(
        user_id=current_user_id
    )

    return ChatSessionListResponse(
        sessions=sessions,
        total=len(sessions),
    )


@router.get(
    "/chat/sessions/{session_id}",
    response_model=ChatSessionResponse,
)
async def get_session_detail(
    session_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    """Returns one session's metadata plus its full message history."""

    result = await chat_sessions.get_session(
        session_id=session_id,
        user_id=current_user_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found.",
        )

    session, messages = result

    return ChatSessionResponse(
        session=session,
        messages=messages,
    )


@router.delete(
    "/chat/sessions/{session_id}",
    response_model=MessageResponse,
)
async def delete_session_route(
    session_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    """Deletes a chat session belonging to the current user."""

    deleted = await chat_sessions.delete_session(
        session_id=session_id,
        user_id=current_user_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found.",
        )

    return MessageResponse(
        message="Chat session deleted successfully"
    )