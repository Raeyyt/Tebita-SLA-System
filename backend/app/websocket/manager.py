from typing import Dict, List
from starlette.websockets import WebSocket


class ConnectionManager:
    def __init__(self):
        # Map user_id -> list of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.setdefault(user_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        conns = self.active_connections.get(user_id)
        if not conns:
            return
        try:
            conns.remove(websocket)
        except ValueError:
            pass
        if not conns:
            self.active_connections.pop(user_id, None)

    async def send_personal_message(self, message: str, user_id: str):
        conns = self.active_connections.get(user_id, [])
        for ws in list(conns):
            try:
                await ws.send_text(message)
            except Exception:
                # ignore send errors; client may have disconnected
                try:
                    conns.remove(ws)
                except ValueError:
                    pass

    async def broadcast(self, message: str):
        # Send to all connected clients
        for user_id, conns in list(self.active_connections.items()):
            for ws in list(conns):
                try:
                    await ws.send_text(message)
                except Exception:
                    try:
                        conns.remove(ws)
                    except ValueError:
                        pass


# single shared manager instance used by the app
manager = ConnectionManager()
