import asyncio
from typing import List, Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import redis.asyncio as aioredis
from app.database import get_redis

router = APIRouter(tags=["WebSocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, board_id: int, websocket: WebSocket):
        await websocket.accept()
        if board_id not in self.active_connections:
            self.active_connections[board_id] = []
        self.active_connections[board_id].append(websocket)

    def disconnect(self, board_id: int, websocket: WebSocket):
        if board_id in self.active_connections:
            self.active_connections[board_id].remove(websocket)
            if not self.active_connections[board_id]:
                del self.active_connections[board_id]

    async def broadcast(self, board_id: int, message: str):
        if board_id in self.active_connections:
            for connection in self.active_connections[board_id]:
                await connection.send_text(message)

manager = ConnectionManager()

async def redis_subscriber(board_id: int, r: aioredis.Redis):
    pubsub = r.pubsub()
    await pubsub.subscribe(f"board:{board_id}")
    try:
        async for message in pubsub.listen():
            if message and message["type"] == "message":
                data = message["data"]
                await manager.broadcast(board_id, data)
    except asyncio.CancelledError:
        await pubsub.unsubscribe(f"board:{board_id}")

@router.websocket("/ws/boards/{board_id}")
async def websocket_endpoint(websocket: WebSocket, board_id: int, r: aioredis.Redis = Depends(get_redis)):
    await manager.connect(board_id, websocket)
    sub_task = asyncio.create_task(redis_subscriber(board_id, r))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(board_id, websocket)
        sub_task.cancel()