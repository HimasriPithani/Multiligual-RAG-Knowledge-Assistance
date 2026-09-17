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
    """
    Embeds the question and searches ChromaDB for the closest chunks,
    filtering out anything below the configured similarity threshold.
    """
    k = top_k or settings.top_k
    query_vector = embed_query(question)

    raw_results = query_chunks(
        query_embedding=query_vector,
        top_k=k,
        document_ids=document_ids,
    )

    results: List[RetrievedChunk] = []
    for item in raw_results:
        if item["similarity"] < settings.similarity_threshold:
            continue
        results.append(
            RetrievedChunk(
                chunk_id=item["chunk_id"],
                text=item["text"],
                document_id=item["document_id"],
                filename=item["filename"],
                page=item.get("page"),
                similarity=item["similarity"],
            )
        )

    return results
