import json
from typing import Any, Dict

from .. import config
from ..websocket.manager import manager

try:
    # optional Redis pub/sub bridge
    from ..websocket.redis_pubsub import publish_notification
except Exception:
    publish_notification = None


async def send_user_notification(user_id: str, payload: Dict[str, Any]):
    """Publish a notification for a single user. If Redis is configured, publish
    to the `notifications` channel with `user_id` set so other processes can
    route it. Falls back to in-process manager if Redis not available.
    """
    try:
        message = payload.copy()
        message["user_id"] = user_id
        # Prefer Redis-based pub/sub when available
        if publish_notification is not None and config.settings.redis_url:
            await publish_notification("notifications", message)
            return
    except Exception:
        pass

    # Fallback: deliver directly
    try:
        await manager.send_personal_message(json.dumps(payload), user_id)
    except Exception:
        # swallow errors to avoid breaking flows
        pass


async def broadcast_notification(payload: Dict[str, Any]):
    try:
        message = payload.copy()
        if publish_notification is not None and config.settings.redis_url:
            await publish_notification("notifications", message)
            return
    except Exception:
        pass

    try:
        await manager.broadcast(json.dumps(payload))
    except Exception:
        pass
