"""
Endpoints for the "Settings" page: view and update the signed-in user's
own profile (name, password).

Reads/writes via app/database/user_store.py, the same Mongo users
collection your signup/login flow uses.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user_id, hash_password
from app.database import user_store
from app.models.schemas import MessageResponse, UserResponse, UserUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users/me", tags=["settings"])


@router.get("", response_model=UserResponse)
async def get_profile(current_user_id: str = Depends(get_current_user_id)):
    """Return the signed-in user's own profile."""
    user = await user_store.get_user(user_id=current_user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return UserResponse(user=user)


@router.put("", response_model=UserResponse)
async def update_profile(
    payload: UserUpdate,
    current_user_id: str = Depends(get_current_user_id),
):
    """Update the signed-in user's name and/or password. Both fields are optional."""
    if payload.name is None and payload.password is None:
        raise HTTPException(status_code=400, detail="Nothing to update.")

    hashed_password = hash_password(payload.password) if payload.password else None

    updated = await user_store.update_user(
        user_id=current_user_id,
        name=payload.name,
        hashed_password=hashed_password,
    )

    if updated is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return UserResponse(user=updated)


@router.delete("", response_model=MessageResponse)
async def delete_account(current_user_id: str = Depends(get_current_user_id)):
    """Permanently delete the signed-in user's account."""
    await user_store.delete_user(user_id=current_user_id)
    return MessageResponse(message="Account deleted.")