from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_current_user, get_db
from app.db.models.message import Message as MsgModel
from app.db.models.user import User
from app.db.repositories.chat_repository import ChatRepository
from app.db.repositories.message_repository import MessageRepository
from app.services.websocket_manager import manager

router = APIRouter()


class SenderOut(BaseModel):
    id: UUID
    username: str
    display_name: str | None
    model_config = {"from_attributes": True}

class MessageOut(BaseModel):
    id: UUID
    chat_id: UUID
    sender: SenderOut | None
    content: str | None
    message_type: str
    deleted_for_everyone: bool
    created_at: datetime
    replied_to_id: UUID | None
    model_config = {"from_attributes": True}

class PaginatedOut(BaseModel):
    items: list[MessageOut]
    has_more: bool

class SendIn(BaseModel):
    content: str = Field(..., min_length=1, max_length=4096)
    replied_to_id: UUID | None = None

class EditIn(BaseModel):
    content: str = Field(..., min_length=1)


async def _require_member(db, chat_id, user_id):
    repo = ChatRepository(db)
    m = await repo.get_member(chat_id, user_id)
    if not m:
        raise HTTPException(403, "Not a member")
    return m


async def _load_msg(db, msg_id: UUID) -> MsgModel:
    result = await db.execute(
        select(MsgModel).options(selectinload(MsgModel.sender)).where(MsgModel.id == msg_id)
    )
    return result.scalar_one()


@router.get("/{chat_id}/messages", response_model=PaginatedOut)
async def list_messages(
    chat_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    before_id: UUID | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_member(db, chat_id, current_user.id)
    repo = MessageRepository(db)
    msgs = await repo.list_for_chat(chat_id, limit=limit + 1, before_id=before_id)
    has_more = len(msgs) > limit
    return PaginatedOut(items=msgs[:limit], has_more=has_more)  # type: ignore[arg-type]


@router.post("/{chat_id}/messages", response_model=MessageOut, status_code=201)
async def send_message(
    chat_id: UUID,
    body: SendIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_member(db, chat_id, current_user.id)
    repo = MessageRepository(db)
    msg = await repo.create(
        chat_id=chat_id, sender_id=current_user.id,
        content=body.content, message_type="text",
        replied_to_id=body.replied_to_id,
    )
    # Reload with sender
    msg = await _load_msg(db, msg.id)

    # Broadcast via WebSocket
    chat_repo = ChatRepository(db)
    chat = await chat_repo.get_with_members(chat_id)
    if chat:
        payload = {
            "id": str(msg.id), "chat_id": str(chat_id),
            "content": body.content, "message_type": "text",
            "deleted_for_everyone": False,
            "created_at": msg.created_at.isoformat(),
            "replied_to_id": str(body.replied_to_id) if body.replied_to_id else None,
            "sender": {
                "id": str(current_user.id),
                "username": current_user.username,
                "display_name": current_user.display_name,
            },
        }
        member_ids = [str(m.user_id) for m in chat.members]
        await manager.send_to_chat(member_ids, "new_message", payload, exclude_user_id=str(current_user.id))

    return msg


@router.patch("/{chat_id}/messages/{message_id}", response_model=MessageOut)
async def edit_message(
    chat_id: UUID, message_id: UUID, body: EditIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_member(db, chat_id, current_user.id)
    repo = MessageRepository(db)
    msg = await repo.get(message_id)
    if not msg or msg.chat_id != chat_id:
        raise HTTPException(404, "Message not found")
    if msg.sender_id != current_user.id:
        raise HTTPException(403, "Not your message")
    msg = await repo.update(msg, content=body.content)
    chat_repo = ChatRepository(db)
    chat = await chat_repo.get_with_members(chat_id)
    if chat:
        member_ids = [str(m.user_id) for m in chat.members]
        await manager.send_to_chat(member_ids, "message_edited",
            {"chat_id": str(chat_id), "message_id": str(message_id), "content": body.content})
    return msg


@router.delete("/{chat_id}/messages/{message_id}", status_code=204)
async def delete_message(
    chat_id: UUID, message_id: UUID,
    for_everyone: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_member(db, chat_id, current_user.id)
    repo = MessageRepository(db)
    msg = await repo.get(message_id)
    if not msg or msg.chat_id != chat_id:
        raise HTTPException(404, "Message not found")
    if for_everyone:
        if msg.sender_id != current_user.id:
            raise HTTPException(403, "Only sender can delete for everyone")
        await repo.delete_for_everyone(message_id)
        chat_repo = ChatRepository(db)
        chat = await chat_repo.get_with_members(chat_id)
        if chat:
            member_ids = [str(m.user_id) for m in chat.members]
            await manager.send_to_chat(member_ids, "message_deleted",
                {"chat_id": str(chat_id), "message_id": str(message_id)})
