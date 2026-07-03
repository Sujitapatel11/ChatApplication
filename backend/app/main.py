"""FirstChat MVP — register, login, chat"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import auth, chats, messages, users
from app.core.config import settings
from app.services.websocket_manager import manager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    from app.core.events import create_tables
    await create_tables()
    yield


app = FastAPI(
    title="FirstChat MVP",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVP — allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

V1 = "/api/v1"
app.include_router(auth.router, prefix=f"{V1}/auth", tags=["Auth"])
app.include_router(users.router, prefix=f"{V1}/users", tags=["Users"])
app.include_router(chats.router, prefix=f"{V1}/chats", tags=["Chats"])
app.include_router(messages.router, prefix=f"{V1}/chats", tags=["Messages"])


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    from app.core.dependencies import ws_get_current_user
    from app.db.base import async_session

    try:
        async with async_session() as db:
            user = await ws_get_current_user(websocket, db)
    except Exception:
        return

    user_id = str(user.id)
    await manager.connect(user_id, websocket)

    # Mark online
    async with async_session() as db:
        from app.db.repositories.user_repository import UserRepository
        repo = UserRepository(db)
        await repo.set_online(user.id, True)
        await db.commit()

    await manager.broadcast_presence(user_id, online=True)

    try:
        while True:
            data = await websocket.receive_json()
            event = data.get("event")
            payload = data.get("payload", {})

            if event == "typing":
                chat_id = str(payload.get("chat_id", ""))
                async with async_session() as db:
                    from app.db.repositories.chat_repository import ChatRepository
                    from uuid import UUID
                    repo = ChatRepository(db)
                    try:
                        chat = await repo.get_with_members(UUID(chat_id))
                        if chat:
                            member_ids = [str(m.user_id) for m in chat.members]
                            await manager.send_to_chat(
                                chat_member_ids=member_ids,
                                event="typing",
                                payload={
                                    "chat_id": chat_id,
                                    "user_id": user_id,
                                    "is_typing": payload.get("is_typing", True),
                                },
                                exclude_user_id=user_id,
                            )
                    except Exception:
                        pass

    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(user_id)
        async with async_session() as db:
            from app.db.repositories.user_repository import UserRepository
            repo = UserRepository(db)
            await repo.set_online(user.id, False)
            await db.commit()
        await manager.broadcast_presence(user_id, online=False)
