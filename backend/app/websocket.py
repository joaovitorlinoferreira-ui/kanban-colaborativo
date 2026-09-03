from fastapi import APIRouter, WebSocket, status, Query
from sqlalchemy.orm import Session
import jwt
from app.database import SessionLocal
from app.auth import SECRET_KEY, ALGORITHM
from app.models import Board, User

router = APIRouter()

@router.websocket("/ws/boards/{board_id}")
async def websocket_endpoint(websocket: WebSocket, board_id: int, token: str = Query(None)):
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Decodifica o token JWT
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    db: Session = SessionLocal()

    try:
        # Busca o usuário no banco
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Verifica se o usuário é membro do board
        board = db.query(Board).filter(Board.id == board_id).first()
        if not board or user not in board.members:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Aceita a conexão após as duas validações passarem
        await manager.connect(websocket, board_id)
        
        while True:
            await websocket.receive_text()

    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    finally:
        manager.disconnect(websocket, board_id)
        db.close()