from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ws.manager import control_room_manager
from simulator.scenarios import generate


def test_control_room_connects_and_responds_to_ping() -> None:
    client = TestClient(app)
    with client.websocket_connect("/ws/control-room") as websocket:
        connected = websocket.receive_json()
        assert connected["type"] == "control_room.connected"
        assert connected["connectionCount"] == 1

        websocket.send_json({"type": "ping"})
        assert websocket.receive_json() == {"type": "pong"}

    assert control_room_manager.connection_count == 0


def test_telemetry_and_incident_are_broadcast() -> None:
    client = TestClient(app)
    with client.websocket_connect("/ws/control-room") as websocket:
        websocket.receive_json()
        response = client.post("/api/v1/telemetry", json=next(generate("rollover", 1)))
        assert response.status_code == 200

        telemetry = websocket.receive_json()
        incident = websocket.receive_json()
        assert telemetry["type"] == "device.telemetry"
        assert incident["type"] == "incident.suspected"
        assert incident["incident"]["status"] == "pending_confirmation"
