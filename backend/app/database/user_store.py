"""
Reads and updates user accounts in MongoDB via the same users collection
your signup/login flow writes to (see database/mongodb.py's
get_users_collection).

ASSUMPTION: this assumes your signup endpoint writes each user document
with the field names user_id, name, email, password_hash, is_active,
created_at, updated_at — the same names as UserMetadata / the SQLAlchemy
User model, just as a plain dict instead of a row. If your auth.py uses
different keys (e.g. Mongo's own _id instead of a separate user_id, or
"hashed_password" instead of "password_hash"), adjust the field names
below to match — everything else stays the same.

Save this as app/database/user_store.py.
"""

from datetime import datetime, timezone
from typing import Optional

from app.database.mongodb import get_users_collection
from app.models.schemas import UserMetadata


async def get_user(user_id: str) -> Optional[UserMetadata]:
    collection = get_users_collection()

    raw = await collection.find_one(
        {"user_id": user_id},
        {"_id": 0, "password_hash": 0},
    )

    return UserMetadata(**raw) if raw else None


async def update_user(
    user_id: str,
    name: Optional[str] = None,
    hashed_password: Optional[str] = None,
) -> Optional[UserMetadata]:
    updates = {"updated_at": datetime.now(timezone.utc)}

    if name is not None:
        updates["name"] = name

    if hashed_password is not None:
        updates["password_hash"] = hashed_password

    collection = get_users_collection()
    await collection.update_one({"user_id": user_id}, {"$set": updates})

    return await get_user(user_id)


async def delete_user(user_id: str) -> bool:
    collection = get_users_collection()
    result = await collection.delete_one({"user_id": user_id})
    return result.deleted_count > 0