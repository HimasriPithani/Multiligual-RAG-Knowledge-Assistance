"""
Stores chat sessions and their messages in MongoDB, one document per
session with its messages embedded as a subarray. Mirrors metadata.py's
pattern for documents — same Mongo client, same async motor style.

Save this as app/database/chat_sessions.py.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import uuid4

from app.database.mongodb import get_database
from app.models.schemas import ChatMessage, ChatSessionMetadata


def get_collection():
    database = get_database()
    return database["chat_sessions"]


async def create_session(user_id: str, title: str) -> ChatSessionMetadata:
    now = datetime.now(timezone.utc)

    session = ChatSessionMetadata(
        session_id=f"SESSION_{uuid4().hex[:12].upper()}",
        user_id=user_id,
        title=title,
        created_at=now,
        updated_at=now,
    )

    collection = get_collection()
    await collection.insert_one({**session.model_dump(), "messages": []})

    return session


async def add_message(session_id: str, role: str, content: str) -> ChatMessage:
    message = ChatMessage(
        message_id=f"MSG_{uuid4().hex[:12].upper()}",
        role=role,
        content=content,
        created_at=datetime.now(timezone.utc),
    )

    collection = get_collection()
    await collection.update_one(
        {"session_id": session_id},
        {
            "$push": {"messages": message.model_dump()},
            "$set": {"updated_at": message.created_at},
        },
    )

    return message


async def get_session(
    session_id: str, user_id: str
) -> Optional[Tuple[ChatSessionMetadata, List[ChatMessage]]]:
    """Returns (session, messages) for a session owned by user_id, or None."""
    collection = get_collection()

    raw = await collection.find_one(
        {"session_id": session_id, "user_id": user_id},
        {"_id": 0},
    )

    if not raw:
        return None

    messages_raw = raw.pop("messages", [])
    session = ChatSessionMetadata(**raw)
    messages = [ChatMessage(**m) for m in messages_raw]

    return session, messages


async def list_sessions(user_id: str) -> List[ChatSessionMetadata]:
    """Returns every session for a user, most recently updated first."""
    collection = get_collection()

    cursor = collection.find(
        {"user_id": user_id},
        {"_id": 0, "messages": 0},
    ).sort("updated_at", -1)

    sessions = []
    async for raw in cursor:
        sessions.append(ChatSessionMetadata(**raw))

    return sessions


async def delete_session(session_id: str, user_id: str) -> bool:
    collection = get_collection()
    result = await collection.delete_one(
        {"session_id": session_id, "user_id": user_id}
    )
    return result.deleted_count > 0