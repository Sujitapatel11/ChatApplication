from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.db.models.user import User
from app.db.repositories.user_repository import UserRepository

router = APIRouter()


class UserPublic(BaseModel):
    id: UUID
    username: str
    display_name: str | None
    profile_picture: str | None
    online: bool
    model_config = {"from_attributes": True}


@router.get("/search", response_model=list[UserPublic])
async def search_users(
    q: str = Query(..., min_length=2),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    results = await repo.search(q)
    return [u for u in results if u.id != current_user.id]


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(
    user_id: UUID,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepository(db)
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user
