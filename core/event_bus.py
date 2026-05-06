"""Event Bus - Cross-device real-time messaging."""

from typing import Any, Callable, Optional
from datetime import datetime, timezone
import json
import asyncio


EventHandler = Callable[[dict[str, Any]], Any]

USER_CHANNEL = "user:{user_id}:events"
DEVICE_CHANNEL = "user:{user_id}:device:{device_id}"


class LocalEventBus:
    """In-process event bus (no Redis dependency)."""

    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = {}

    def subscribe(self, channel: str, handler: EventHandler):
        if channel not in self._handlers:
            self._handlers[channel] = []
        self._handlers[channel].append(handler)

    def unsubscribe(self, channel: str, handler: EventHandler):
        if channel in self._handlers:
            self._handlers[channel].remove(handler)

    async def publish(self, channel: str, event: dict):
        event["_meta"] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "channel": channel,
        }
        for handler in self._handlers.get(channel, []):
            if asyncio.iscoroutinefunction(handler):
                asyncio.create_task(handler(event))
            else:
                handler(event)

    async def publish_user(self, user_id: str, event: dict):
        await self.publish(USER_CHANNEL.format(user_id=user_id), event)

    async def publish_device(self, user_id: str, device_id: str, event: dict):
        await self.publish(DEVICE_CHANNEL.format(user_id=user_id, device_id=device_id), event)


class RedisEventBus:
    """Redis-backed event bus for production use."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self._redis_url = redis_url
        self._pub = None
        self._sub = None
        self._handlers: dict[str, list[EventHandler]] = {}

    async def connect(self):
        import redis.asyncio as aioredis
        self._pub = await aioredis.from_url(self._redis_url)
        self._sub = self._pub.pubsub()

    async def subscribe(self, channel: str, handler: EventHandler):
        if channel not in self._handlers:
            self._handlers[channel] = []
            await self._sub.subscribe(channel)
        self._handlers[channel].append(handler)

    async def publish(self, channel: str, event: dict):
        if not self._pub:
            await self.connect()
        event["_meta"] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "channel": channel,
        }
        await self._pub.publish(channel, json.dumps(event))

    async def start_listening(self):
        async for message in self._sub.listen():
            if message["type"] == "message":
                channel = message["channel"].decode()
                data = json.loads(message["data"])
                for handler in self._handlers.get(channel, []):
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.create_task(handler(data))
                    else:
                        handler(data)


def get_event_bus(provider: str = "local"):
    if provider == "redis":
        return RedisEventBus()
    return LocalEventBus()
