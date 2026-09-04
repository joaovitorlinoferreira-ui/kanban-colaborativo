import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.websocket import router as websocket_router, redis_subscriber
from app.routers import auth, boards, cards

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: Inicia a escuta do Redis Pub/Sub
    subscriber_task = asyncio.create_task(redis_subscriber())
    yield
    # SHUTDOWN: Cancela a tarefa ao desligar
    subscriber_task.cancel()

app = FastAPI(
    title="Kanban Colaborativo",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(boards.router, prefix="/boards", tags=["Boards"])
app.include_router(cards.router, tags=["Cards"])
app.include_router(websocket_router)