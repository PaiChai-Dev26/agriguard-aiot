import asyncio

from backend.app.ws.manager import ConnectionManager


class FakeWebSocket:
    def __init__(self, failing: bool = False) -> None:
        self.accepted = False
        self.events: list[dict] = []
        self.failing = failing

    async def accept(self) -> None:
        self.accepted = True

    async def send_json(self, data: dict) -> None:
        if self.failing:
            raise ConnectionError
        self.events.append(data)


def test_connect_and_broadcast() -> None:
    manager = ConnectionManager()
    socket = FakeWebSocket()
    asyncio.run(manager.connect(socket))
    asyncio.run(manager.broadcast({"type": "device.connected"}))
    assert socket.accepted is True
    assert socket.events == [{"type": "device.connected"}]


def test_failed_connection_is_removed() -> None:
    manager = ConnectionManager()
    socket = FakeWebSocket(failing=True)
    asyncio.run(manager.connect(socket))
    asyncio.run(manager.broadcast({"type": "test"}))
    assert manager.connection_count == 0

