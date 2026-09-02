from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Board, User, KanbanColumn
from app.schemas import BoardCreate, BoardResponse, BoardMemberInvite, ColumnCreate, ColumnResponse
from app.auth import get_current_user

router = APIRouter(prefix="/boards", tags=["Boards"])

@router.post("/", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
def create_board(board_in: BoardCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    board = Board(title=board_in.title, owner_id=current_user.id)
    board.members.append(current_user)
    
    default_columns = ["A Fazer", "Em Progresso", "Concluído"]
    for idx, col_title in enumerate(default_columns):
        board.columns.append(KanbanColumn(title=col_title, order=idx))

    db.add(board)
    db.commit()
    db.refresh(board)
    return board

@router.get("/", response_model=List[BoardResponse])
def list_my_boards(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Board).filter(Board.members.any(id=current_user.id)).all()

@router.get("/{board_id}", response_model=BoardResponse)
def get_board_details(board_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    board = db.query(Board).filter(Board.id == board_id, Board.members.any(id=current_user.id)).first()
    if not board:
        raise HTTPException(status_code=404, detail="Quadro não encontrado ou acesso negado.")
    return board

@router.post("/{board_id}/members", status_code=status.HTTP_200_OK)
def invite_member(board_id: int, invite: BoardMemberInvite, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    board = db.query(Board).filter(Board.id == board_id, Board.owner_id == current_user.id).first()
    if not board:
        raise HTTPException(status_code=403, detail="Apenas o criador pode convidar usuários.")

    user_to_add = db.query(User).filter(User.email == invite.email).first()
    if not user_to_add:
        raise HTTPException(status_code=404, detail="Usuário com esse e-mail não foi encontrado.")

    if user_to_add not in board.members:
        board.members.append(user_to_add)
        db.commit()
    
    return {"message": f"Usuário {invite.email} adicionado ao quadro."}

@router.post("/{board_id}/columns", response_model=ColumnResponse, status_code=status.HTTP_201_CREATED)
def add_column(board_id: int, col_in: ColumnCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    board = db.query(Board).filter(Board.id == board_id, Board.members.any(id=current_user.id)).first()
    if not board:
        raise HTTPException(status_code=404, detail="Quadro não encontrado.")
    
    last_order = len(board.columns)
    column = KanbanColumn(board_id=board_id, title=col_in.title, order=last_order)
    db.add(column)
    db.commit()
    db.refresh(column)
    return column