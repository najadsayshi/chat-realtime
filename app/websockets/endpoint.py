from fastapi import WebSocket, APIRouter, WebSocketDisconnect
from app.core.connection_manager import ConnectionManager
from app.auth.jwt_handler import verify_token

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    handlers = {
        "JOIN_ROOM": handle_join_room,
        "LEAVE_ROOM": handle_leave_room,
        "MESSAGE": handle_message
    }
    #verify token
    user_id = verify_token(token)

    if not user_id:
        await websocket.close()
        return
 
    await websocket.accept()

    await manager.connect(user_id,websocket)



    try: 
        while True:
            message = await websocket.receive_json()
            
            event_type = message.get("type")
            handler = handlers.get(event_type)



            if handler:
                await handler(user_id,websocket,message)
            else:
                await websocket.send_json({
                    "type": "ERROR",
                    "message": f"Unknown event type: {event_type}"
                })

    except WebSocketDisconnect:
        
        await manager.disconnect(user_id, websocket)




async def handle_join_room(user_id, websocket, message):
    room_id = message.get("room_id")
    if not room_id:
        await websocket.send_json({
            "type": "ERROR",
            "message" : "Room is required"
        })
        return
    await manager.join_room(user_id, room_id, websocket)

async def handle_leave_room(user_id, websocket, message):
    room_id = message.get("room_id")
    if not room_id:
        await websocket.send_json({
            "type" : "ERROR",
            "message" : "Room is required"
        })
        return
    await manager.leave_room(user_id, room_id, websocket)

async def handle_message(user_id, websocket, message):
    content = message.get("content")
    room_id = message.get("room_id")
    if not room_id:
        await websocket.send_json({
            "type" : "ERROR",
            "message" : "Room is required"
        })
        return 
    if not content:
        await websocket.send_json({
            "type" : "ERROR",
            "message" : "Content is required"
        })
        return
    await manager.broadcast_to_room(room_id, {
    "type": "MESSAGE",
    "user_id": user_id,
    "room_id": room_id,
    "content": content
})

    