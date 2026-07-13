from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Call websocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Call websocket disconnection"""
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Send broadcast message to all connected websockets"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

socket_manager = ConnectionManager()
