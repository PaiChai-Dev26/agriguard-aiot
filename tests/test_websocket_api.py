from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ws.manager import control_room_manager


def test_control_room_connects_and_responds_to_ping() -> None:
    client = TestClient(app)
    with client.websocket_connect("/ws/control-room") as websocket:
        connected = websocket.receive_json()
        assert connected["type"] == "control_room.connected"
        assert connected["connectionCount"] == 1

        websocket.send_json({"type": "ping"})
        assert websocket.receive_json() == {"type": "pong"}

    assert control_room_manager.connection_count == 0

