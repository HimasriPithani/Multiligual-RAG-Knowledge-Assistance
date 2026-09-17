"""
The core RAG endpoint: takes a question in any supported language,
retrieves relevant document chunks, and generates a grounded,
source-cited answer in the same language as the question.
"""

import logging

from fastapi import APIRouter, HTTPException

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
async def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    language = detect_language(request.question)

    chunks = retrieve_relevant_chunks(
        question=request.question,
        top_k=request.top_k,
        document_ids=request.document_ids,
    )

    # --- Hallucination control: no chunk cleared the similarity threshold ---
    if not chunks:
        return ChatResponse(
            answer=NOT_FOUND_MESSAGE.get(language, NOT_FOUND_MESSAGE["en"]),
            language=language,
            sources=[],
            grounded=False,
        )

    prompt = build_prompt(request.question, chunks)

    try:
        answer_text = generate_answer(prompt)
    except LLMServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

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
    )
