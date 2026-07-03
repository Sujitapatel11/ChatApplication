from typing import AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException, WebSocket, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.base import async_session
from app.db.models.user import User
from app.db.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    exc = HTTPException(status_code=401, detail="Invalid credentials",
                        headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = decode_token(token)
    except ValueError:
        raise exc
    if payload.get("type") != "access":
        raise exc
    try:
        user_id = UUID(payload["sub"])
    except (KeyError, ValueError):
        raise exc
    repo = UserRepository(db)
    user = await repo.get(user_id)
    if not user or not user.is_active:
        raise exc
    return user


async def ws_get_current_user(websocket: WebSocket, db: AsyncSession) -> User:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        payload = decode_token(token)
        user_id = UUID(payload["sub"])
    except Exception:
        await websocket.close(code=4001)
        raise HTTPException(status_code=401, detail="Invalid token")
    repo = UserRepository(db)
    user = await repo.get(user_id)
    if not user or not user.is_active:
        await websocket.close(code=4001)
        raise HTTPException(status_code=401, detail="User not found")
    return user
