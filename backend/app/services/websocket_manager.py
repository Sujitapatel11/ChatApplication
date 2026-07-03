import asyncio
from typing import Any
from fastapi import WebSocket
from starlette.websockets import WebSocketState


class ConnectionManager:
    def __init__(self):
        self._conns: dict[str, WebSocket] = {}
        self._lock = asyncio.Lock()

    async def connect(self, user_id: str, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            old = self._conns.get(user_id)
            if old and old.client_state == WebSocketState.CONNECTED:
                try: await old.close()
                except: pass
            self._conns[user_id] = ws

    async def disconnect(self, user_id: str):
        async with self._lock:
            self._conns.pop(user_id, None)

    async def send_to_user(self, user_id: str, event: str, payload: Any) -> bool:
        ws = self._conns.get(user_id)
        if ws and ws.client_state == WebSocketState.CONNECTED:
            try:
                await ws.send_json({"event": event, "payload": payload})
                return True
            except:
                await self.disconnect(user_id)
        return False

    async def send_to_chat(self, chat_member_ids: list[str], event: str,
                            payload: Any, exclude_user_id: str | None = None):
        tasks = [
            self.send_to_user(uid, event, payload)
            for uid in chat_member_ids
            if uid != exclude_user_id
        ]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def broadcast_presence(self, user_id: str, online: bool):
        payload = {"user_id": user_id, "online": online}
        tasks = [
            ws.send_json({"event": "presence", "payload": payload})
            for uid, ws in self._conns.items()
            if uid != user_id and ws.client_state == WebSocketState.CONNECTED
        ]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def is_online(self, user_id: str) -> bool:
        ws = self._conns.get(user_id)
        return ws is not None and ws.client_state == WebSocketState.CONNECTED

    @property
    def online_count(self) -> int:
        return len(self._conns)


manager = ConnectionManager()
