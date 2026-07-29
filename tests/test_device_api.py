from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from backend.app.api.devices import repository
from backend.app.dependencies import support_alert_repository
from backend.app.main import app
from backend.app.schemas import SupportAlert
from simulator.scenarios import generate

client = TestClient(app)


def setup_function() -> None:
    repository.clear()
    support_alert_repository.clear()


def test_register_list_and_read_device() -> None:
    response = client.post(
        "/api/v1/devices/register",
        json={
            "deviceId": "tractor-001",
            "displayName": "1번 트랙터",
            "deviceType": "tractor",
        },
    )
    assert response.status_code == 201
    assert response.json()["online"] is False
    assert client.get("/api/v1/devices").json()[0]["deviceId"] == "tractor-001"
    assert client.get("/api/v1/devices/tractor-001").status_code == 200


def test_duplicate_registration_returns_conflict() -> None:
    payload = {
        "deviceId": "tractor-001",
        "displayName": "1번 트랙터",
        "deviceType": "tractor",
    }
    assert client.post("/api/v1/devices/register", json=payload).status_code == 201
    assert client.post("/api/v1/devices/register", json=payload).status_code == 409


def test_unknown_device_returns_not_found() -> None:
    assert client.get("/api/v1/devices/missing").status_code == 404


def test_get_recent_position_history() -> None:
    for payload in generate("normal", 3):
        client.post("/api/v1/telemetry", json=payload)
    response = client.get("/api/v1/devices/sim-tractor-001/positions?limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_position_history_limit_is_bounded() -> None:
    assert client.get("/api/v1/devices/tractor-001/positions?limit=0").status_code == 422


def test_device_reads_its_support_alerts() -> None:
    client.post(
        "/api/v1/devices/register",
        json={
            "deviceId": "tractor-002",
            "displayName": "2번 트랙터",
            "deviceType": "tractor",
        },
    )
    support_alert_repository.add(
        SupportAlert(
            id=uuid4(),
            incidentId=uuid4(),
            targetDeviceId="tractor-002",
            distanceMeters=250,
            createdAt=datetime.now(timezone.utc),
        )
    )
    response = client.get("/api/v1/devices/tractor-002/support-alerts")
    assert response.status_code == 200
    assert response.json()[0]["distanceMeters"] == 250
