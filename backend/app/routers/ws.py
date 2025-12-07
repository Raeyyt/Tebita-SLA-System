from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional

from jose import jwt, JWTError

from ..config import settings
from ..websocket.manager import manager
from ..database import SessionLocal
from ..models import User

router = APIRouter()


async def _validate_token_get_user(token: str) -> Optional[User]:
    """Validate JWT token and return the DB User record or None."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        return user
    finally:
        db.close()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, token: str = Query(None)):
    """WebSocket endpoint that requires a JWT `token` query parameter for authentication.
    The token's `sub` claim must match a valid username in the database. The `user_id`
    parameter must match the authenticated user's id (as string) to prevent impersonation.
    Clients should connect to `/ws/{user_id}?token=...`.
    """
    if not token:
        await websocket.close(code=4401)  # custom close for unauthorized
        return

    user = await _validate_token_get_user(token)
    if not user:
        await websocket.close(code=4401)
        return

    # prevent connecting to another user's channel
    if str(user.id) != str(user_id):
        await websocket.close(code=4403)
        return

    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep the connection alive; ignore incoming messages
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, user_id)
