from fastapi import FastAPI
import asyncio
from sqlmodel import SQLModel
from app.models.db import engine
from app.models.user import User
from app.models.message import Message
from app.websockets.endpoint import router, manager
from app.core.redis_manager import RedisManager
from app.routes.message import router as message_router
from app.auth.routes import router as auth_router
app = FastAPI()

app.include_router(router)
app.include_router(message_router)
app.include_router(auth_router)

redis_manager = RedisManager()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def startup():
    print("🚀 STARTUP RUNNING")

    # Create tables
    SQLModel.metadata.create_all(engine)

    # Start Redis listener
    asyncio.create_task(
        redis_manager.subscribe(manager)
    )