from fastapi import FastAPI
import asyncio

from app.core.redis_manager import RedisManager
from app.websockets.endpoint import router, manager
from app.auth.routes import router as auth_router
app = FastAPI()

app.include_router(router)
app.include_router(auth_router)
redis_manager = RedisManager()


@app.on_event("startup")
async def start_redis_listener():
    asyncio.create_task(
        redis_manager.subscribe(manager)
    )
