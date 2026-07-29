from datetime import datetime, timezone
from uuid import uuid4

import pytest

from backend.app.repositories.support_alerts import InMemorySupportAlertRepository
from backend.app.schemas import DeviceRead, NearbyDevice
from backend.app.services.support import create_support_alerts, respond_to_alert


def nearby(device_id: str, distance: float) -> NearbyDevice:
    now = datetime.now(timezone.utc)
    return NearbyDevice(
        device=DeviceRead(
            deviceId=device_id,
            displayName=device_id,
            deviceType="tractor",
            registeredAt=now,
            lastSeenAt=now,
            online=True,
        ),
        distanceMeters=distance,
    )


def test_create_one_alert_per_nearby_device() -> None:
    repository = InMemorySupportAlertRepository()
    incident_id = uuid4()
    alerts = create_support_alerts(
        repository,
        incident_id,
        [nearby("tractor-002", 100), nearby("tractor-003", 300)],
    )
    assert len(alerts) == 2
    assert all(alert.incident_id == incident_id for alert in alerts)


def test_support_response_progression() -> None:
    repository = InMemorySupportAlertRepository()
    alert = create_support_alerts(repository, uuid4(), [nearby("tractor-002", 100)])[0]
    checking = respond_to_alert(repository, alert.id, "checking")
    available = respond_to_alert(repository, alert.id, "available")
    assert checking.status == "checking"
    assert available.status == "available"
    assert available.responded_at is not None


def test_final_support_response_cannot_change() -> None:
    repository = InMemorySupportAlertRepository()
    alert = create_support_alerts(repository, uuid4(), [nearby("tractor-002", 100)])[0]
    respond_to_alert(repository, alert.id, "unavailable")
    with pytest.raises(ValueError):
        respond_to_alert(repository, alert.id, "available")

