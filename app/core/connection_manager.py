from collections import defaultdict
from fastapi import Websocket
class ConnectionManager:

    def __init__(self):
        self.connections =defaultdict(set) # {user_id : set of webscocket}
        self.room_members = defaultdict(set) # {room_id : set of user_id}
        self.socket_rooms = defaultdict(set) # {websocket : set of room_id}

    async def connect(self, user_id, websocket):
        await websocket.accept()
        self.connections[user_id].add(websocket)
    async def disconnect(self, user_id, websocket):
        self.connections[user_id].remove(websocket)

        self.socket_rooms[websocket].clear() # Clear the rooms associated with the websocket


    async def join_room(self, user_id, room_id, websocket):
        self.room_members[room_id].add(user_id)
        self.socket_rooms[websocket].add(room_id)

    async def leave_room(self, user_id, room_id, websocket):
        self.room_members[room_id].remove(user_id)
        self.socket_rooms[websocket].remove(room_id)

        
    async def broadcast_to_room(self, room_id, message):
        for user_id in self.room_members[room_id]:
            for websocket in self.connections[user_id]:
                await websocket.send_json(message) 

