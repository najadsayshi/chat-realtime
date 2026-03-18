from fastapi import FastAPI
import asyncio
from sqlmodel import SQLModel
from app.models.db import engine
from app.models.user import User
from app.models.message import Message
from app.websockets.endpoint import router, manager
from app.core.redis_manager import RedisManager
from app.routes.message import router as message_router


app = FastAPI()

app.include_router(router)
app.include_router(message_router)

redis_manager = RedisManager()


@app.on_event("startup")
async def startup():
    print("🚀 STARTUP RUNNING")

    # Create tables
    SQLModel.metadata.create_all(engine)

    # Start Redis listener
    asyncio.create_task(
        redis_manager.subscribe(manager)
    )