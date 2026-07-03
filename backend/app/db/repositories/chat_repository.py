from __future__ import annotations
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.chat import Chat
from app.db.models.chat_member import ChatMember


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id: UUID) -> Optional[Chat]:
        r = await self.db.execute(select(Chat).where(Chat.id == id))
        return r.scalar_one_or_none()

    async def get_with_members(self, id: UUID) -> Optional[Chat]:
        r = await self.db.execute(
            select(Chat).options(
                selectinload(Chat.members).selectinload(ChatMember.user)
            ).where(Chat.id == id)
        )
        return r.scalar_one_or_none()

    async def get_member(self, chat_id: UUID, user_id: UUID) -> Optional[ChatMember]:
        r = await self.db.execute(
            select(ChatMember).where(
                and_(ChatMember.chat_id == chat_id, ChatMember.user_id == user_id)
            )
        )
        return r.scalar_one_or_none()

    async def find_direct(self, a: UUID, b: UUID) -> Optional[Chat]:
        sq_a = select(ChatMember.chat_id).where(ChatMember.user_id == a).scalar_subquery()
        sq_b = select(ChatMember.chat_id).where(ChatMember.user_id == b).scalar_subquery()
        r = await self.db.execute(
            select(Chat).where(
                and_(Chat.is_group == False, Chat.id.in_(sq_a), Chat.id.in_(sq_b))
            )
        )
        return r.scalar_one_or_none()

    async def list_for_user(self, user_id: UUID, limit: int = 50) -> list[Chat]:
        from app.db.models.message import Message
        from sqlalchemy import desc, func
        latest = (
            select(Message.chat_id, func.max(Message.created_at).label("lm"))
            .group_by(Message.chat_id).subquery()
        )
        r = await self.db.execute(
            select(Chat)
            .join(ChatMember, ChatMember.chat_id == Chat.id)
            .outerjoin(latest, latest.c.chat_id == Chat.id)
            .where(ChatMember.user_id == user_id)
            .options(
                selectinload(Chat.members).selectinload(ChatMember.user),
            )
            .order_by(desc(latest.c.lm))
            .limit(limit)
        )
        return list(r.scalars().unique().all())

    async def create(self, **kw) -> Chat:
        chat = Chat(**kw)
        self.db.add(chat)
        await self.db.flush()
        await self.db.refresh(chat)
        return chat

    async def add_member(self, chat_id: UUID, user_id: UUID, role: str = "member") -> ChatMember:
        m = ChatMember(chat_id=chat_id, user_id=user_id, role=role)
        self.db.add(m)
        await self.db.flush()
        return m

    async def remove_member(self, chat_id: UUID, user_id: UUID) -> None:
        m = await self.get_member(chat_id, user_id)
        if m:
            await self.db.delete(m)
            await self.db.flush()
