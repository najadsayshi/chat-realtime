from fastapi import WebSocket, APIRouter, WebSocketDisconnect
from sqlalchemy import event
from sqlmodel import Session
from app.core.connection_manager import ConnectionManager
from app.core.redis_manager import RedisManager
from app.models.db import engine
from app.models.message import Message
from app.auth.jwt_handler import verify_token

router = APIRouter()
manager = ConnectionManager()
redis_manager = RedisManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")

    user_id = verify_token(token)

    if not user_id:
        await websocket.close()
        return

    await manager.connect(user_id, websocket)

    handlers = {
        "JOIN_ROOM": handle_join_room,
        "LEAVE_ROOM": handle_leave_room,
        "MESSAGE": handle_message
    }

    try:
        while True:
            message = await websocket.receive_json()

            event_type = message.get("type")
            handler = handlers.get(event_type)

            if handler:
                await handler(user_id, websocket, message)
            else:
                await websocket.send_json({
                    "type": "ERROR",
                    "message": f"Unknown event type: {event_type}"
                })

    except WebSocketDisconnect:
        await manager.disconnect(user_id, websocket)


# 🔹 Handlers

async def handle_join_room(user_id, websocket, message):
    room_id = message.get("room_id")

    if not room_id:
        await websocket.send_json({"type": "ERROR", "message": "Room is required"})
        return

    await manager.join_room(user_id, room_id, websocket)


async def handle_leave_room(user_id, websocket, message):
    room_id = message.get("room_id")

    if not room_id:
        await websocket.send_json({"type": "ERROR", "message": "Room is required"})
        return

    await manager.leave_room(user_id, room_id, websocket)


async def handle_message(user_id, websocket, message):
    content = message.get("content")
    room_id = message.get("room_id")

    if not room_id:
        await websocket.send_json({"type": "ERROR", "message": "Room is required"})
        return

    if not content:
        await websocket.send_json({"type": "ERROR", "message": "Content is required"})
        return

    session = Session(engine)

    try:
        # 🧱 Save to DB
        msg = Message(
            room_id=room_id,
            user_id=user_id,
            content=content
        )
        session.add(msg)
        session.commit()
        session.refresh(msg)
        from app.models.user import User

        user = session.get(User, user_id)
        # 🔥 Event
        
        event = {
            "type": "MESSAGE",
            "id": msg.id,
            "name"  : user.name,
            "user_id": msg.user_id,
            "room_id": msg.room_id,
            "content": msg.content,
            "timestamp": str(msg.timestamp)
        }
        # 🚀 Publish to Redis
        await redis_manager.publish(room_id, event)

    finally:
        session.close()