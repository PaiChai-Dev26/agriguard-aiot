from typing import Any, Protocol


class WebSocketLike(Protocol):
    async def accept(self) -> None: ...
    async def send_json(self, data: Any) -> None: ...


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: list[WebSocketLike] = []

    @property
    def connection_count(self) -> int:
        return len(self._connections)

    async def connect(self, websocket: WebSocketLike) -> None:
        await websocket.accept()
        self._connections.append(websocket)

    def disconnect(self, websocket: WebSocketLike) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)

    async def broadcast(self, event: dict[str, Any]) -> None:
        disconnected: list[WebSocketLike] = []
        for connection in tuple(self._connections):
            try:
                await connection.send_json(event)
            except Exception:
                disconnected.append(connection)
        for connection in disconnected:
            self.disconnect(connection)


control_room_manager = ConnectionManager()

