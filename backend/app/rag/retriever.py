"""
Retrieves the most relevant chunks for a user question.

This is the piece that enables hallucination control: chunks below
`similarity_threshold` are dropped before they ever reach the LLM, so
the model can't quietly latch onto a weak match and invent an answer.
"""

from dataclasses import dataclass
from typing import List, Optional

from app.config import settings
from app.database.chroma import query_chunks
from app.rag.embeddings import embed_query


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    document_id: str
    filename: str
    page: Optional[int]
    similarity: float


def retrieve_relevant_chunks(
    question: str,
    top_k: Optional[int] = None,
    document_ids: Optional[List[str]] = None,
) -> List[RetrievedChunk]:

    k = top_k or settings.top_k

    query_vector = embed_query(question)

    raw_results = query_chunks(
        query_embedding=query_vector,
        top_k=k,
        document_ids=document_ids,
    )

    if not raw_results:
        return []

    accepted_results = [
        item
        for item in raw_results
        if item["similarity"] >= settings.similarity_threshold
    ]

    # Fallback:
    # If the selected document has retrieved chunks but all are
    # below the threshold, retain the best matching chunk.
    if not accepted_results and document_ids:
        best_chunk = max(
            raw_results,
            key=lambda item: item["similarity"],
        )

        print(
            "RETRIEVAL FALLBACK: Keeping best matching chunk",
            {
                "chunk_id": best_chunk["chunk_id"],
                "similarity": best_chunk["similarity"],
                "document_id": best_chunk["document_id"],
            },
        )

        accepted_results = [best_chunk]

    return [
        RetrievedChunk(
            chunk_id=item["chunk_id"],
            text=item["text"],
            document_id=item["document_id"],
            filename=item["filename"],
            page=item.get("page"),
            similarity=item["similarity"],
        )
        for item in accepted_results
    ]
