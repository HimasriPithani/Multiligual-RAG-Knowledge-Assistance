
"""
Thin wrapper around a local, persistent ChromaDB instance.

ChromaDB runs embedded in the backend process and writes to disk at
`CHROMA_PATH`.
"""

import logging
from functools import lru_cache
from typing import Dict, List, Optional

import chromadb

from app.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_chroma_client() -> chromadb.ClientAPI:
    return chromadb.PersistentClient(
        path=settings.chroma_path
    )


@lru_cache(maxsize=1)
def get_collection():
    client = get_chroma_client()

    collection = client.get_or_create_collection(
        name=settings.chroma_collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    logger.info(
        "CHROMA COLLECTION | name=%s | count=%d | metadata=%s",
        collection.name,
        collection.count(),
        collection.metadata,
    )

    return collection


def add_chunks(
    chunk_ids: List[str],
    texts: List[str],
    embeddings: List[List[float]],
    metadatas: List[Dict],
) -> None:
    """Store chunk embeddings, text, and metadata."""

    if not chunk_ids:
        return

    collection = get_collection()

    collection.add(
        ids=chunk_ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    logger.info(
        "CHROMA ADD | chunks_added=%d | collection_count=%d",
        len(chunk_ids),
        collection.count(),
    )


def query_chunks(
    query_embedding: List[float],
    top_k: int,
    document_ids: Optional[List[str]] = None,
) -> List[Dict]:
    """
    Return the top_k most similar chunks.

    Assumes the collection uses cosine distance:
        distance = 0 -> identical
        similarity = 1 - distance
    """

    collection = get_collection()

    # Build the filter only when specific document IDs are supplied.
    where_filter = None

    if document_ids:
        where_filter = {
            "document_id": {
                "$in": document_ids
            }
        }

    logger.info(
        "CHROMA QUERY | top_k=%d | document_ids=%s | where=%s",
        top_k,
        document_ids,
        where_filter,
    )

    query_kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
        "include": [
            "documents",
            "metadatas",
            "distances",
        ],
    }

    if where_filter is not None:
        query_kwargs["where"] = where_filter

    results = collection.query(**query_kwargs)

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    logger.info(
        "CHROMA RAW RESULT | ids=%d | documents=%d | metadatas=%d | distances=%d",
        len(ids),
        len(documents),
        len(metadatas),
        len(distances),
    )

    output: List[Dict] = []

    for i, chunk_id in enumerate(ids):
        metadata = metadatas[i] or {}

        distance = distances[i]

        # Cosine distance -> cosine similarity.
        similarity = 1.0 - distance

        result = {
            "chunk_id": chunk_id,
            "text": documents[i],
            "document_id": metadata.get("document_id"),
            "filename": metadata.get("filename"),
            "page": metadata.get("page"),
            "similarity": similarity,
        }

        logger.info(
            "CHROMA CHUNK | chunk_id=%s | document_id=%s | "
            "filename=%s | distance=%.4f | similarity=%.4f",
            result["chunk_id"],
            result["document_id"],
            result["filename"],
            distance,
            similarity,
        )

        output.append(result)

    logger.info(
        "CHROMA OUTPUT | chunks_returned=%d",
        len(output),
    )

    return output


def delete_document_chunks(document_id: str) -> None:
    """Remove every chunk belonging to a document."""

    collection = get_collection()

    collection.delete(
        where={
            "document_id": document_id
        }
    )

    logger.info(
        "CHROMA DELETE | document_id=%s | remaining_count=%d",
        document_id,
        collection.count(),
    )


def health_check() -> bool:
    try:
        get_collection().count()
        return True
    except Exception:
        logger.exception("ChromaDB health check failed.")
        return False