from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.database.mongodb import get_users_collection
from app.models.schemas import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserMetadata,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(user_data: UserCreate):
    collection = get_users_collection()

    normalized_email = str(user_data.email).lower().strip()

    existing_user = await collection.find_one(
        {"email": normalized_email}
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    user_id = str(uuid4())
    now = datetime.now(timezone.utc)

    user_document = {
        "user_id": user_id,
        "name": user_data.name.strip(),
        "email": normalized_email,
        "password_hash": hash_password(user_data.password),
        "is_active": True,
        "created_at": now,
        "updated_at": None,
    }

    await collection.insert_one(user_document)

    access_token = create_access_token(
        {
            "sub": user_id,
            "email": normalized_email,
        }
    )

    user_response = UserMetadata(
        user_id=user_id,
        name=user_document["name"],
        email=normalized_email,
        created_at=now,
        updated_at=None,
        is_active=True,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(login_data: UserLogin):
    collection = get_users_collection()

    normalized_email = str(login_data.email).lower().strip()

    user = await collection.find_one(
        {"email": normalized_email}
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not verify_password(
        login_data.password,
        user["password_hash"],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive.",
        )

    access_token = create_access_token(
        {
            "sub": user["user_id"],
            "email": user["email"],
        }
    )

    user_response = UserMetadata(
        user_id=user["user_id"],
        name=user["name"],
        email=user["email"],
        created_at=user["created_at"],
        updated_at=user.get("updated_at"),
        is_active=user.get("is_active", True),
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response,
    )   