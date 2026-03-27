from collections import defaultdict
from fastapi import WebSocket
class ConnectionManager:

    def __init__(self):
        self.connections =defaultdict(set) # {user_id : set of webscocket}
        self.room_members = defaultdict(set) # {room_id : set of user_id}
        self.socket_rooms = defaultdict(set) # {websocket : set of room_id}

    async def connect(self, user_id, websocket):
        await websocket.accept() # accept connection in webscocket endpoint
        self.connections[user_id].add(websocket)
    async def disconnect(self, user_id, websocket):
        # remove this socket from user's connections
        self.connections[user_id].remove(websocket)

        # iterate through rooms this socket joined
        for room_id in self.socket_rooms.get(websocket, []):
            
            # check if the user still has another socket in this room
            still_in_room = False
            for other_socket in self.connections.get(user_id, []):
                if room_id in self.socket_rooms.get(other_socket, []):
                    still_in_room = True
                    break

            # if no other socket is in the room → remove user
            if not still_in_room:
                if user_id in self.room_members.get(room_id, set()):
                    self.room_members[room_id].remove(user_id)

        # delete socket entry
        if websocket in self.socket_rooms:
            del self.socket_rooms[websocket]

    async def join_room(self, user_id, room_id, websocket):
        self.room_members[room_id].add(user_id)
        self.socket_rooms[websocket].add(room_id)

    async def leave_room(self, user_id, room_id, websocket):
        self.room_members[room_id].remove(user_id)
        self.socket_rooms[websocket].remove(room_id)

            
    async def broadcast_to_room(self, room_id, message):
        for user_id in self.room_members[room_id]:
            for websocket in list(self.connections[user_id]):
                try:
                    await websocket.send_json(message)
                except:
                    self.connections[user_id].remove(websocket)