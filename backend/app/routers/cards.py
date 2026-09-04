import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import redis.asyncio as aioredis
from app.database import get_db, get_redis
from app.models import Card, KanbanColumn, Board, User
from app.schemas import CardCreate, CardResponse, CardMove
from app.auth import get_current_user

router = APIRouter(prefix="/cards", tags=["Cards"])

async def notify_board_change(board_id: int, event_type: str, payload: dict, r):
    message = json.dumps({"event": event_type, "data": payload})
    r.publish(f"board:{board_id}", message)

@router.post("/column/{column_id}", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
async def create_card(
    column_id: int,
    card_in: CardCreate,
    db: Session = Depends(get_db),
    r: aioredis.Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    column = db.query(KanbanColumn).filter(KanbanColumn.id == column_id).first()
    if not column:
        raise HTTPException(status_code=404, detail="Coluna não encontrada.")

    board = db.query(Board).filter(Board.id == column.board_id, Board.members.any(id=current_user.id)).first()
    if not board:
        raise HTTPException(status_code=403, detail="Acesso negado ao quadro.")

    card = Card(
        column_id=column_id,
        title=card_in.title,
        description=card_in.description,
        order=len(column.cards),
        created_by=current_user.id
    )
    db.add(card)
    db.commit()
    db.refresh(card)

    card_data = CardResponse.model_validate(card).model_dump(mode="json")
    await notify_board_change(column.board_id, "CARD_CREATED", card_data, r)

    return card

@router.put("/{card_id}/move", response_model=CardResponse)
async def move_card(
    card_id: int,
    move_in: CardMove,
    db: Session = Depends(get_db),
    r: aioredis.Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card não encontrado.")

    current_column = db.query(KanbanColumn).filter(KanbanColumn.id == card.column_id).first()
    target_column = db.query(KanbanColumn).filter(KanbanColumn.id == move_in.target_column_id).first()
    
    if not current_column or not target_column or current_column.board_id != target_column.board_id:
        raise HTTPException(status_code=400, detail="Movimentação inválida entre quadros diferentes.")

    board = db.query(Board).filter(Board.id == current_column.board_id, Board.members.any(id=current_user.id)).first()
    if not board:
        raise HTTPException(status_code=403, detail="Acesso negado.")

    card.column_id = move_in.target_column_id
    card.order = move_in.new_order
    db.commit()
    db.refresh(card)

    payload = {
        "card_id": card.id,
        "from_column_id": current_column.id,
        "to_column_id": move_in.target_column_id,
        "new_order": move_in.new_order,
        "card": CardResponse.model_validate(card).model_dump(mode="json")
    }
    await notify_board_change(current_column.board_id, "CARD_MOVED", payload, r)

    return card

@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    card_id: int,
    db: Session = Depends(get_db),
    r: aioredis.Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user)
):
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card não encontrado.")

    column = db.query(KanbanColumn).filter(KanbanColumn.id == card.column_id).first()
    board = db.query(Board).filter(Board.id == column.board_id, Board.members.any(id=current_user.id)).first()
    if not board:
        raise HTTPException(status_code=403, detail="Acesso negado.")

    board_id = column.board_id
    db.delete(card)
    db.commit()

    await notify_board_change(board_id, "CARD_DELETED", {"card_id": card_id, "column_id": column.id}, r)
    return None