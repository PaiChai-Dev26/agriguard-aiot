from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from backend.app.api.incidents import repository
from backend.app.main import app
from backend.app.schemas import IncidentRead, RiskResult

client = TestClient(app)


def make_incident(status: str = "detected") -> IncidentRead:
    return IncidentRead(
        id=uuid4(),
        deviceId="tractor-001",
        occurredAt=datetime.now(timezone.utc),
        status=status,
        risk=RiskResult(
            classification="rollover",
            riskScore=0.95,
            evidence=["dangerous_tilt", "impact", "inactivity"],
            modelVersion="rules-v1",
        ),
    )


def setup_function() -> None:
    repository.clear()


def test_list_and_read_incidents() -> None:
    expected = repository.add(make_incident())
    assert client.get("/api/v1/incidents").json()[0]["id"] == str(expected.id)
    assert client.get(f"/api/v1/incidents/{expected.id}").status_code == 200


def test_acknowledge_detected_incident() -> None:
    incident = repository.add(make_incident())
    response = client.patch(
        f"/api/v1/incidents/{incident.id}/status",
        json={"status": "acknowledged"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "acknowledged"


def test_reject_invalid_status_transition() -> None:
    incident = repository.add(make_incident())
    response = client.patch(
        f"/api/v1/incidents/{incident.id}/status",
        json={"status": "dispatched"},
    )
    assert response.status_code == 409


def test_cancel_pending_incident() -> None:
    incident = repository.add(make_incident("pending_confirmation"))
    response = client.post(
        f"/api/v1/incidents/{incident.id}/cancel",
        json={"reason": "driver_is_safe"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

