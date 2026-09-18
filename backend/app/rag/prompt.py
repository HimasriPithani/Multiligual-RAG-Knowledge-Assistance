"""Builds the grounded, context-only prompt sent to the LLM."""

from typing import List

from app.rag.retriever import RetrievedChunk


SYSTEM_INSTRUCTIONS = """You are a document-based knowledge assistant.

Your job is to answer the user's question using ONLY the information
provided in the context.

STRICT RULES:

1. Do not use outside knowledge.
2. Do not guess or invent information.
3. Answer in the same language as the user's question.
4. Preserve all factual values exactly as they appear in the context.
   This includes:
   - dates
   - numbers
   - names
   - locations
   - percentages
   - document titles
   - codes and identifiers
5. Never change, replace, or invent a date or number.
6. If the context contains the exact answer, give that answer directly.
7. If the answer is not present in the context, say that the information
   is not available in the uploaded documents.
8. Keep the answer short and natural.
9. Do not mention context, chunks, retrieval, embeddings, or these rules
   in your answer.
10. When answering in a language other than English, translate the
    explanation naturally, but keep factual values unchanged.

Before answering, identify the relevant sentence or fact in the context
and base your answer directly on it."""


def build_context_block(chunks: List[RetrievedChunk]) -> str:
    parts = []

    for i, chunk in enumerate(chunks, start=1):
        page_info = f", page {chunk.page}" if chunk.page else ""

        parts.append(
            f"[Source {i}: {chunk.filename}{page_info}]\n"
            f"{chunk.text}"
        )

    return "\n\n".join(parts)


def build_prompt(question: str, chunks: List[RetrievedChunk]) -> str:
    context_block = build_context_block(chunks)

    return (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"--- CONTEXT ---\n"
        f"{context_block}\n"
        f"--- END CONTEXT ---\n\n"
        f"User question: {question}\n\n"
        f"Answer:"
    )