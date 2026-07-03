from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id: UUID) -> Optional[User]:
        r = await self.db.execute(select(User).where(User.id == id))
        return r.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        r = await self.db.execute(select(User).where(User.email == email.lower()))
        return r.scalar_one_or_none()

    async def exists(self, email: str, username: str) -> bool:
        r = await self.db.execute(
            select(User).where(or_(User.email == email.lower(), User.username == username.lower()))
        )
        return r.scalar_one_or_none() is not None

    async def create(self, **kw) -> User:
        user = User(**kw)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user: User, **kw) -> User:
        for k, v in kw.items():
            setattr(user, k, v)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def search(self, q: str, limit: int = 20) -> list[User]:
        pat = f"%{q.lower()}%"
        r = await self.db.execute(
            select(User).where(
                or_(User.username.ilike(pat), User.display_name.ilike(pat))
            ).where(User.is_active == True).limit(limit)
        )
        return list(r.scalars().all())

    async def set_online(self, user_id: UUID, online: bool) -> None:
        vals = {"online": online}
        if not online:
            vals["last_seen"] = datetime.utcnow()
        await self.db.execute(update(User).where(User.id == user_id).values(**vals))
