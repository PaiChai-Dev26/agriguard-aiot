from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from backend.app.api.devices import repository as device_repository
from backend.app.api.incidents import repository, support_alert_repository
from backend.app.main import app
from backend.app.schemas import DeviceRead, IncidentRead, Location, RiskResult

client = TestClient(app)


def make_incident(status: str = "detected") -> IncidentRead:
    return IncidentRead(
        id=uuid4(),
        deviceId="tractor-001",
        occurredAt=datetime.now(timezone.utc),
        status=status,
        location=Location(latitude=36.3012, longitude=127.5874),
        risk=RiskResult(
            classification="rollover",
            riskScore=0.95,
            evidence=["dangerous_tilt", "impact", "inactivity"],
            modelVersion="rules-v1",
        ),
    )


def setup_function() -> None:
    repository.clear()
    device_repository.clear()
    support_alert_repository.clear()


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


def test_get_sos_handoff_for_detected_incident() -> None:
    incident = repository.add(make_incident())
    response = client.get(f"/api/v1/incidents/{incident.id}/sos")
    assert response.status_code == 200
    assert response.json()["incidentId"] == str(incident.id)
    assert response.json()["emergencyCallUri"] == "tel:119"


def test_sos_handoff_rejects_pending_incident() -> None:
    incident = repository.add(make_incident("pending_confirmation"))
    response = client.get(f"/api/v1/incidents/{incident.id}/sos")
    assert response.status_code == 409


def test_get_nearby_devices_for_incident() -> None:
    now = datetime.now(timezone.utc)
    incident = repository.add(make_incident())
    for device_id, latitude in [("near", 36.302), ("far", 36.32)]:
        device_repository.add(
            DeviceRead(
                deviceId=device_id,
                displayName=device_id,
                deviceType="tractor",
                registeredAt=now,
                lastSeenAt=now,
                online=True,
                location=Location(latitude=latitude, longitude=127.5874),
            )
        )
    response = client.get(f"/api/v1/incidents/{incident.id}/nearby-devices")
    assert response.status_code == 200
    assert [item["device"]["deviceId"] for item in response.json()] == ["near"]


def test_send_and_answer_nearby_support_alert() -> None:
    now = datetime.now(timezone.utc)
    incident = repository.add(make_incident())
    device_repository.add(
        DeviceRead(
            deviceId="near",
            displayName="인근 트랙터",
            deviceType="tractor",
            registeredAt=now,
            lastSeenAt=now,
            online=True,
            location=Location(latitude=36.302, longitude=127.5874),
        )
    )
    sent = client.post(f"/api/v1/incidents/{incident.id}/nearby-alert")
    assert sent.status_code == 201
    alert = sent.json()[0]

    response = client.post(
        f"/api/v1/incidents/{incident.id}/support-response",
        params={"alert_id": alert["id"]},
        json={"status": "available"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "available"
    listed = client.get(f"/api/v1/incidents/{incident.id}/support-alerts").json()
    assert listed[0]["status"] == "available"
