import asyncio
import json
from typing import Any, Dict, Optional

import redis.asyncio as aioredis

from .manager import manager

_redis: Optional[aioredis.Redis] = None
_listener_task: Optional[asyncio.Task] = None
_stopping = False


async def init_redis(url: str):
    global _redis
    _redis = aioredis.from_url(url, decode_responses=True)


async def publish_notification(channel: str, payload: Dict[str, Any]):
    if _redis is None:
        raise RuntimeError("Redis not initialized")
    message = json.dumps(payload)
    await _redis.publish(channel, message)


async def _listener(channel: str = "notifications"):
    global _redis, _stopping
    if _redis is None:
        return
    pubsub = _redis.pubsub()
    await pubsub.subscribe(channel)
    try:
        while not _stopping:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message is None:
                await asyncio.sleep(0.1)
                continue
            # message is a dict: {'type': 'message', 'pattern': None, 'channel': 'notifications', 'data': '...'}
            data = message.get("data")
            if not data:
                continue
            try:
                payload = json.loads(data)
            except Exception:
                payload = {"message": data}

            # Deliver to specific user if provided, otherwise broadcast
            user_id = None
            if isinstance(payload, dict):
                user_id = payload.get("user_id")

            if user_id:
                # manager expects string user_id
                await manager.send_personal_message(json.dumps(payload), str(user_id))
            else:
                await manager.broadcast(json.dumps(payload))
    finally:
        try:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
        except Exception:
            pass


def start_listener(loop: Optional[asyncio.AbstractEventLoop] = None, channel: str = "notifications"):
    global _listener_task, _stopping
    if _listener_task is not None:
        return
    _stopping = False
    if loop is None:
        loop = asyncio.get_event_loop()
    _listener_task = loop.create_task(_listener(channel))


async def stop_listener():
    global _listener_task, _stopping
    _stopping = True
    if _listener_task:
        try:
            await _listener_task
        except asyncio.CancelledError:
            pass
        _listener_task = None
