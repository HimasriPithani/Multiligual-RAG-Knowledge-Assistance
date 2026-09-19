from functools import lru_cache

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings


@lru_cache(maxsize=1)
def get_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(settings.mongodb_uri)


def get_database():
    client = get_client()
    return client[settings.mongodb_db_name]


def get_users_collection():
    database = get_database()
    return database["users"]


async def health_check() -> bool:
    try:
        client = get_client()
        await client.admin.command("ping")
        return True
    except Exception:
        return False