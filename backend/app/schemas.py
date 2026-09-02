from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# Auth
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Cards
class CardCreate(BaseModel):
    title: str
    description: Optional[str] = None

class CardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class CardMove(BaseModel):
    target_column_id: int
    new_order: int

class CardResponse(BaseModel):
    id: int
    column_id: int
    title: str
    description: Optional[str] = None
    order: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True

# Columns
class ColumnCreate(BaseModel):
    title: str

class ColumnResponse(BaseModel):
    id: int
    board_id: int
    title: str
    order: int
    cards: List[CardResponse] = []

    class Config:
        from_attributes = True

# Boards
class BoardCreate(BaseModel):
    title: str

class BoardMemberInvite(BaseModel):
    email: EmailStr

class BoardResponse(BaseModel):
    id: int
    title: str
    owner_id: int
    created_at: datetime
    columns: List[ColumnResponse] = []
    members: List[UserResponse] = []

    class Config:
        from_attributes = True