from __future__ import annotations
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.message import Message


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id: UUID) -> Optional[Message]:
        r = await self.db.execute(select(Message).where(Message.id == id))
        return r.scalar_one_or_none()

    async def list_for_chat(self, chat_id: UUID, limit: int = 50, before_id: Optional[UUID] = None) -> list[Message]:
        stmt = (
            select(Message)
            .options(selectinload(Message.sender), selectinload(Message.replied_to))
            .where(and_(Message.chat_id == chat_id, Message.deleted_for_everyone == False))
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        if before_id:
            cur = await self.db.execute(select(Message.created_at).where(Message.id == before_id))
            ts = cur.scalar_one_or_none()
            if ts:
                stmt = stmt.where(Message.created_at < ts)
        r = await self.db.execute(stmt)
        rows = list(r.scalars().all())
        rows.reverse()
        return rows

    async def create(self, **kw) -> Message:
        msg = Message(**kw)
        self.db.add(msg)
        await self.db.flush()
        await self.db.refresh(msg)
        return msg

    async def update(self, msg: Message, **kw) -> Message:
        for k, v in kw.items():
            setattr(msg, k, v)
        await self.db.flush()
        await self.db.refresh(msg)
        return msg

    async def delete_for_everyone(self, id: UUID) -> None:
        await self.db.execute(
            update(Message).where(Message.id == id).values(deleted_for_everyone=True, content=None)
        )
