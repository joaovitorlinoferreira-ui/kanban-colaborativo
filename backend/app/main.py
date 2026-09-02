from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import auth, boards, cards
from app import websocket

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Kanban Colaborativo em Tempo Real",
    description="API do Kanban com FastAPI, WebSocket e Redis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(boards.router)
app.include_router(cards.router)
app.include_router(websocket.router)

@app.get("/")
def read_root():
    return {"status": "API Kanban operando com sucesso!"}