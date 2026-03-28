import redis.asyncio as redis
import json

class RedisManager:
    def __init__(self):
        
        self.channel = "room_messages"
        import os
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
        self.redis = redis.from_url(redis_url, decode_responses=True)
    async def publish(self, room_id, message):
        event = {
            "room_id" : room_id,
            "message" : message
        }
        await self.redis.publish(self.channel, json.dumps(event))
    async def subscribe(self, connection_manager):
        print("SUBSCRIBE CALLED WITH:", connection_manager)
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(self.channel)

        async for message in pubsub.listen():

            if message["type"] != "message":
                continue

            data = json.loads(message["data"])

            room_id = data["room_id"]
            event = data["message"]

            await connection_manager.broadcast_to_room(room_id, event)
            