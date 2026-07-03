from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.db.models.user import User
from app.db.repositories.chat_repository import ChatRepository
from app.db.repositories.user_repository import UserRepository

router = APIRouter()


class MemberOut(BaseModel):
    user_id: UUID
    username: str
    display_name: str | None
    profile_picture: str | None
    online: bool
    role: str

class ChatOut(BaseModel):
    id: UUID
    is_group: bool
    name: str | None
    members: list[MemberOut] = []

class DirectIn(BaseModel):
    target_user_id: UUID

class GroupIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    member_ids: list[UUID]


def _build(chat, uid: UUID) -> ChatOut:
    members = [
        MemberOut(
            user_id=m.user_id,
            username=m.user.username,
            display_name=m.user.display_name,
            profile_picture=m.user.profile_picture,
            online=m.user.online,
            role=m.role,
        )
        for m in chat.members
    ]
    name = chat.name
    if not chat.is_group:
        other = next((m for m in chat.members if m.user_id != uid), None)
        if other:
            name = other.user.display_name or other.user.username
    return ChatOut(id=chat.id, is_group=chat.is_group, name=name, members=members)


@router.get("", response_model=list[ChatOut])
async def list_chats(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    repo = ChatRepository(db)
    chats = await repo.list_for_user(current_user.id)
    return [_build(c, current_user.id) for c in chats]


@router.post("/direct", response_model=ChatOut, status_code=201)
async def create_direct(body: DirectIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if body.target_user_id == current_user.id:
        raise HTTPException(400, "Cannot chat with yourself")
    u_repo = UserRepository(db)
    if not await u_repo.get(body.target_user_id):
        raise HTTPException(404, "User not found")
    c_repo = ChatRepository(db)
    existing = await c_repo.find_direct(current_user.id, body.target_user_id)
    if existing:
        chat = await c_repo.get_with_members(existing.id)
        return _build(chat, current_user.id)
    chat = await c_repo.create(is_group=False)
    await c_repo.add_member(chat.id, current_user.id, "member")
    await c_repo.add_member(chat.id, body.target_user_id, "member")
    chat = await c_repo.get_with_members(chat.id)
    return _build(chat, current_user.id)


@router.post("/group", response_model=ChatOut, status_code=201)
async def create_group(body: GroupIn, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    c_repo = ChatRepository(db)
    chat = await c_repo.create(is_group=True, name=body.name)
    await c_repo.add_member(chat.id, current_user.id, "owner")
    u_repo = UserRepository(db)
    for uid in set(body.member_ids):
        if uid == current_user.id:
            continue
        if await u_repo.get(uid):
            await c_repo.add_member(chat.id, uid, "member")
    chat = await c_repo.get_with_members(chat.id)
    return _build(chat, current_user.id)


@router.get("/{chat_id}", response_model=ChatOut)
async def get_chat(chat_id: UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    repo = ChatRepository(db)
    chat = await repo.get_with_members(chat_id)
    if not chat:
        raise HTTPException(404, "Chat not found")
    if not any(m.user_id == current_user.id for m in chat.members):
        raise HTTPException(403, "Not a member")
    return _build(chat, current_user.id)
