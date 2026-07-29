from fastapi.testclient import TestClient

from backend.app.api.devices import repository as device_repository
from backend.app.api.incidents import repository
from backend.app.dependencies import replay_repository
from backend.app.main import app
from simulator.scenarios import generate

client = TestClient(app)


def setup_function() -> None:
    repository.clear()
    device_repository.clear()
    replay_repository.clear()


def test_health_endpoint() -> None:
    with TestClient(app) as lifespan_client:
        response = lifespan_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "confirmationMonitor": "running",
        }


def test_telemetry_endpoint_returns_explainable_risk() -> None:
    response = client.post("/api/v1/telemetry", json=next(generate("rollover", 1)))
    assert response.status_code == 200
    body = response.json()
    assert body["classification"] == "rollover"
    assert body["riskScore"] >= 0.9
    assert body["evidence"] == ["dangerous_tilt", "impact", "inactivity"]
    incidents = client.get("/api/v1/incidents").json()
    assert len(incidents) == 1
    assert incidents[0]["status"] == "pending_confirmation"
    assert incidents[0]["deviceId"] == "sim-tractor-001"
    assert replay_repository.get(UUID(incidents[0]["id"])).samples
    replay = client.get(f"/api/v1/incidents/{incidents[0]['id']}/replay")
    assert replay.status_code == 200
    assert replay.json()["deviceId"] == "sim-tractor-001"


def test_invalid_coordinates_are_rejected() -> None:
    payload = next(generate("normal", 1))
    payload["location"]["latitude"] = 100
    response = client.post("/api/v1/telemetry", json=payload)
    assert response.status_code == 422


def test_non_rollover_telemetry_does_not_create_incident() -> None:
    response = client.post("/api/v1/telemetry", json=next(generate("slope", 1)))
    assert response.status_code == 200
    assert client.get("/api/v1/incidents").json() == []


def test_telemetry_updates_device_registry() -> None:
    payload = next(generate("normal", 1))
    client.post("/api/v1/telemetry", json=payload)
    device = client.get(f"/api/v1/devices/{payload['deviceId']}").json()
    assert device["online"] is True
    assert device["location"]["valid"] is True
    assert device["batteryPercent"] == payload["batteryPercent"]
from uuid import UUID
