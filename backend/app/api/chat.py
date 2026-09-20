"""
The core RAG endpoint: takes a question in any supported language,
retrieves relevant document chunks, and generates a grounded,
source-cited answer in the same language as the question.

Each exchange is saved to a chat session so it shows up in the user's
chat history. Pass `session_id` in the request to continue an existing
session; omit it to start a new one.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user_id
from app.database import chat_sessions
from app.models.schemas import ChatRequest, ChatResponse, SourceReference
from app.multilingual.language_detection import detect_language
from app.rag.generator import LLMServiceError, generate_answer
from app.rag.prompt import build_prompt
from app.rag.retriever import retrieve_relevant_chunks

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])

NOT_FOUND_MESSAGE = {
    "en": "I could not find this information in the uploaded documents.",
    "hi": "मुझे यह जानकारी अपलोड किए गए दस्तावेज़ों में नहीं मिली।",
    "te": "ఈ సమాచారం అప్‌లోడ్ చేసిన పత్రాలలో నాకు కనుగొనబడలేదు.",
}


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user_id: str = Depends(get_current_user_id),
):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Resolve or create the session this exchange belongs to.
    if request.session_id:
        existing = await chat_sessions.get_session(
            session_id=request.session_id, user_id=current_user_id
        )
        if existing is None:
            raise HTTPException(status_code=404, detail="Chat session not found.")
        session_id = request.session_id
    else:
        session = await chat_sessions.create_session(
            user_id=current_user_id, title=request.question[:60]
        )
        session_id = session.session_id

    await chat_sessions.add_message(
        session_id=session_id, role="user", content=request.question
    )

    language = detect_language(request.question)

    chunks = retrieve_relevant_chunks(
        question=request.question,
        top_k=request.top_k,
        document_ids=request.document_ids,
    )

    # --- Hallucination control: no chunk cleared the similarity threshold ---
    if not chunks:
        answer_text = NOT_FOUND_MESSAGE.get(language, NOT_FOUND_MESSAGE["en"])
        await chat_sessions.add_message(
            session_id=session_id, role="assistant", content=answer_text
        )

        return ChatResponse(
            answer=answer_text,
            language=language,
            sources=[],
            grounded=False,
            session_id=session_id,
        )

    prompt = build_prompt(request.question, chunks)

    try:
        answer_text = generate_answer(prompt)
    except LLMServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    await chat_sessions.add_message(
        session_id=session_id, role="assistant", content=answer_text
    )

    sources = [
        SourceReference(
            document=c.filename,
            document_id=c.document_id,
            page=c.page,
            chunk_id=c.chunk_id,
            similarity=round(c.similarity, 4),
        )
        for c in chunks
    ]

    return ChatResponse(
        answer=answer_text,
        language=language,
        sources=sources,
        grounded=True,
        session_id=session_id,
    )   