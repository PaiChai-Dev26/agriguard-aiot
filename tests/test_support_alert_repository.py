from datetime import datetime, timezone
from uuid import uuid4

import pytest

from backend.app.repositories.support_alerts import (
    InMemorySupportAlertRepository,
    SupportAlertNotFoundError,
)
from backend.app.schemas import SupportAlert


def alert(incident_id=None, target: str = "tractor-002", distance: float = 100) -> SupportAlert:
    return SupportAlert(
        id=uuid4(),
        incidentId=incident_id or uuid4(),
        targetDeviceId=target,
        distanceMeters=distance,
        createdAt=datetime.now(timezone.utc),
    )


def test_alert_repository_queries_by_incident_and_device() -> None:
    repository = InMemorySupportAlertRepository()
    incident_id = uuid4()
    far = repository.add(alert(incident_id, "far", 500))
    near = repository.add(alert(incident_id, "near", 100))
    assert repository.for_incident(incident_id) == [near, far]
    assert repository.for_device("near") == [near]


def test_duplicate_incident_target_is_rejected() -> None:
    repository = InMemorySupportAlertRepository()
    expected = alert()
    repository.add(expected)
    with pytest.raises(ValueError):
        repository.add(alert(expected.incident_id, expected.target_device_id))


def test_unknown_alert_is_rejected() -> None:
    with pytest.raises(SupportAlertNotFoundError):
        InMemorySupportAlertRepository().get(uuid4())

