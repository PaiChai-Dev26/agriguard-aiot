from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from backend.app.main import app, events, latest_by_device, state_machine


client = TestClient(app)


def rollover_payload(occurred_at: datetime) -> dict:
    return {
        "device_id": "api-test-001",
        "occurred_at": occurred_at.isoformat(),
        "ax": 1.8,
        "ay": 0.4,
        "az": 0.2,
        "gx": 220,
        "gy": 40,
        "gz": 15,
        "roll": 72,
        "pitch": 15,
        "speed_kmh": 0,
        "motion_rms": 0.05,
        "location": {"latitude": 36.3012, "longitude": 127.5874},
    }


def setup_function() -> None:
    latest_by_device.clear()
    events.clear()
    state_machine.reset("api-test-001")


def test_health() -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_rollover_reaches_detected_after_confirmation_window() -> None:
    start = datetime.now(timezone.utc)
    first = client.post("/api/v1/telemetry", json=rollover_payload(start))
    assert first.status_code == 200
    assert first.json()["incident_state"] == "pending_confirmation"

    confirmed = client.post(
        "/api/v1/telemetry",
        json=rollover_payload(start + timedelta(seconds=11)),
    )
    assert confirmed.json()["incident_state"] == "detected"
    assert client.get("/api/v1/incidents").json()[-1]["type"] == "incident.detected"


def test_operator_can_cancel_pending_incident() -> None:
    client.post(
        "/api/v1/telemetry",
        json=rollover_payload(datetime.now(timezone.utc)),
    )
    cancelled = client.post("/api/v1/devices/api-test-001/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"

