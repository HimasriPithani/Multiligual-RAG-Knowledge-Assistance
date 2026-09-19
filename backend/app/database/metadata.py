"""
Stores document metadata (filename, language, upload date, chunk count,
status) in MongoDB. The vector embeddings themselves live in ChromaDB
(see chroma.py) — this file only ever handles metadata, never vectors.

Free MongoDB options for students:
  1. Run `docker compose up mongo` (see docker-compose.yml) — fully free,
     local, no signup.
  2. Create a free-forever M0 cluster at
     https://www.mongodb.com/cloud/atlas/register and put its connection
     string in MONGODB_URI.
"""

from datetime import datetime, timezone
from functools import lru_cache
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.models.schemas import DocumentMetadata


@lru_cache(maxsize=1)
def get_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(settings.mongodb_uri)


def get_collection():
    client = get_client()
    db = client[settings.mongodb_db_name]
    return db["documents"]


async def create_document(document_id: str, filename: str,user_id: str,) -> DocumentMetadata:
    doc = DocumentMetadata(
        document_id=document_id,
        user_id=user_id,
        filename=filename,
        uploaded_at=datetime.now(timezone.utc),
        status="processing",
        chunk_count=0,
    )
    collection = get_collection()
    await collection.insert_one(doc.model_dump())
    return doc


async def mark_ready(document_id: str, language: str, chunk_count: int) -> None:
    collection = get_collection()
    await collection.update_one(
        {"document_id": document_id},
        {"$set": {"status": "ready", "language": language, "chunk_count": chunk_count}},
    )


async def mark_failed(document_id: str, error_message: str) -> None:
    collection = get_collection()
    await collection.update_one(
        {"document_id": document_id},
        {"$set": {"status": "failed", "error_message": error_message}},
    )


async def get_document(
    document_id: str,
) -> Optional[DocumentMetadata]:
    collection = get_collection()

    raw = await collection.find_one(
        {"document_id": document_id},
        {"_id": 0},
    )

    return DocumentMetadata(**raw) if raw else None

async def list_documents(
    user_id: str,
) -> List[DocumentMetadata]:
    collection = get_collection()

    cursor = collection.find(
        {"user_id": user_id},
        {"_id": 0},
    ).sort(
        "uploaded_at",
        -1,
    )

    documents = []

    async for raw in cursor:
        raw.setdefault("user_id", user_id)
        raw.setdefault("language", None)
        raw.setdefault("chunk_count", 0)
        raw.setdefault("status", "processing")
        raw.setdefault("error_message", None)

        documents.append(
            DocumentMetadata(**raw)
        )

    return documents

async def delete_document(document_id: str) -> bool:
    collection = get_collection()
    result = await collection.delete_one({"document_id": document_id})
    return result.deleted_count > 0


async def health_check() -> bool:
    try:
        client = get_client()
        await client.admin.command("ping")
        return True
    except Exception:
        return False
