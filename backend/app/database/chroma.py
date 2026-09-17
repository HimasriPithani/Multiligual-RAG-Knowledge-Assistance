"""
Thin wrapper around a local, persistent ChromaDB instance.

ChromaDB runs embedded in the backend process and writes to disk at
`CHROMA_PATH` — no server, account, or cost involved.
"""

from functools import lru_cache
from typing import Dict, List, Optional

import chromadb

from app.config import settings


@lru_cache(maxsize=1)
def get_chroma_client() -> chromadb.ClientAPI:
    return chromadb.PersistentClient(path=settings.chroma_path)


@lru_cache(maxsize=1)
def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=settings.chroma_collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(
    chunk_ids: List[str],
    texts: List[str],
    embeddings: List[List[float]],
    metadatas: List[Dict],
) -> None:
    """Stores chunk embeddings + text + metadata in the vector store."""
    if not chunk_ids:
        return
    collection = get_collection()
    collection.add(
        ids=chunk_ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )


def query_chunks(
    query_embedding: List[float],
    top_k: int,
    document_ids: Optional[List[str]] = None,
) -> List[Dict]:
    """
    Returns the top_k most similar chunks to the query embedding.

    Each result dict contains: chunk_id, text, document_id, filename,
    page, similarity (1.0 = identical, 0.0 = unrelated).
    """
    collection = get_collection()

    where_filter = None
    if document_ids:
        where_filter = {"document_id": {"$in": document_ids}}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,
    )

    output: List[Dict] = []
    if not results["ids"] or not results["ids"][0]:
        return output

    for i in range(len(results["ids"][0])):
        distance = results["distances"][0][i]  # cosine distance: 0 = identical
        similarity = 1 - distance
        metadata = results["metadatas"][0][i]
        output.append(
            {
                "chunk_id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "document_id": metadata.get("document_id"),
                "filename": metadata.get("filename"),
                "page": metadata.get("page"),
                "similarity": similarity,
            }
        )

    return output


def delete_document_chunks(document_id: str) -> None:
    """Removes every chunk belonging to a document (used on document delete)."""
    collection = get_collection()
    collection.delete(where={"document_id": document_id})


def health_check() -> bool:
    try:
        get_collection().count()
        return True
    except Exception:
        return False
