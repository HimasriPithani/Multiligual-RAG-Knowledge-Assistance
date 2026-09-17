"""Builds the grounded, context-only prompt sent to the LLM."""

from typing import List

from app.rag.retriever import RetrievedChunk

SYSTEM_INSTRUCTIONS = """You are a document-based knowledge assistant.

Answer the user's question using ONLY the provided context below.
If the answer cannot be found in the provided context, clearly state
that the information is not available in the uploaded documents —
do not invent facts or use outside knowledge.

Answer in the same language as the user's question.
Keep the answer concise and directly address the question.
Do not mention "context" or "document chunks" explicitly in your answer
— just answer naturally, as if you already knew the information."""


def build_context_block(chunks: List[RetrievedChunk]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        page_info = f", page {chunk.page}" if chunk.page else ""
        parts.append(f"[Source {i}: {chunk.filename}{page_info}]\n{chunk.text}")
    return "\n\n".join(parts)


def build_prompt(question: str, chunks: List[RetrievedChunk]) -> str:
    context_block = build_context_block(chunks)
    return (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"--- CONTEXT ---\n{context_block}\n--- END CONTEXT ---\n\n"
        f"User question: {question}\n\n"
        f"Answer:"
    )
