import asyncio
import json
import logging
import os
from typing import Dict, List
import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Depends
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.database import get_db
import app.models as models
import app.auth as auth

logger = logging.getLogger(__name__)

router = APIRouter()

# Identifica a model de membros do board se existir
BoardMemberModel = (
    getattr(models, "BoardMember", None) or
    getattr(models, "BoardUser", None) or
    getattr(models, "BoardMembership", None) or
    getattr(models, "Member", None) or
    getattr(models, "UserBoard", None)
)

# Identifica a função de autenticação no módulo auth
get_user_func = (
    getattr(auth, "get_current_user_ws", None) or
    getattr(auth, "get_current_user", None) or
    getattr(auth, "get_user_from_token", None)
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, board_id: int):
        await websocket.accept()
        if board_id not in self.active_connections:
            self.active_connections[board_id] = []
        self.active_connections[board_id].append(websocket)
        logger.info(f"WebSocket conectado ao board {board_id}")

    def disconnect(self, websocket: WebSocket, board_id: int):
        if board_id in self.active_connections:
            if websocket in self.active_connections[board_id]:
                self.active_connections[board_id].remove(websocket)
            if not self.active_connections[board_id]:
                del self.active_connections[board_id]
        logger.info(f"WebSocket desconectado do board {board_id}")

    async def broadcast(self, board_id: int, message: str):
        if board_id in self.active_connections:
            for connection in list(self.active_connections[board_id]):
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Erro ao enviar mensagem via WebSocket: {e}")
                    self.disconnect(connection, board_id)

manager = ConnectionManager()

async def redis_subscriber():
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    redis = aioredis.from_url(redis_url, decode_responses=True)
    pubsub = redis.pubsub()
    await pubsub.psubscribe("board:*")
    logger.info("Iniciado listener do Redis PubSub no canal 'board:*'")

    try:
        async for message in pubsub.listen():
            if message["type"] == "pmessage":
                channel = message["channel"]
                try:
                    board_id = int(channel.split(":")[1])
                    data = message["data"]
                    await manager.broadcast(board_id, data)
                except (IndexError, ValueError) as e:
                    logger.error(f"Erro ao parsear canal do Redis ({channel}): {e}")
    except asyncio.CancelledError:
        logger.info("Listener do Redis PubSub cancelado.")
    finally:
        await pubsub.unsubscribe("board:*")
        await redis.close()

async def get_ws_user(websocket: WebSocket, db: Session):
    """Autentica a conexão WebSocket capturando o token da query string ou headers."""
    if get_user_func:
        try:
            return await get_user_func(websocket, db) if asyncio.iscoroutinefunction(get_user_func) else get_user_func(websocket, db)
        except Exception:
            pass

    token = websocket.query_params.get("token")
    if not token:
        return None

    secret_key = os.getenv("SECRET_KEY", "secret")
    algorithm = os.getenv("ALGORITHM", "HS256")
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        email = payload.get("sub")
        if not email:
            return None
        return db.query(models.User).filter(models.User.email == email).first()
    except (JWTError, AttributeError):
        return None

@router.websocket("/ws/boards/{board_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    board_id: int,
    db: Session = Depends(get_db)
):
    user = await get_ws_user(websocket, db)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if BoardMemberModel:
        is_member = db.query(BoardMemberModel).filter(
            BoardMemberModel.board_id == board_id,
            BoardMemberModel.user_id == user.id
        ).first()

        if not is_member:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    await manager.connect(websocket, board_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, board_id)
    except Exception:
        manager.disconnect(websocket, board_id)