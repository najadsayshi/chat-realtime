from fastapi import FastAPI
import asyncio

from app.core.redis_manager import RedisManager
from app.websockets.endpoint import router, manager

app = FastAPI()

app.include_router(router)

redis_manager = RedisManager()


@app.on_event("startup")
async def start_redis_listener():
    asyncio.create_task(
        redis_manager.subscribe(manager)
    )
