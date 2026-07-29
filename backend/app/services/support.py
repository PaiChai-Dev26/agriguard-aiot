from datetime import datetime, timezone
from uuid import UUID, uuid4

from backend.app.repositories.support_alerts import InMemorySupportAlertRepository
from backend.app.schemas import NearbyDevice, SupportAlert, SupportStatus


def create_support_alerts(
    repository: InMemorySupportAlertRepository,
    incident_id: UUID,
    nearby_devices: list[NearbyDevice],
    now: datetime | None = None,
) -> list[SupportAlert]:
    now = now or datetime.now(timezone.utc)
    return [
        repository.add(
            SupportAlert(
                id=uuid4(),
                incidentId=incident_id,
                targetDeviceId=nearby.device.device_id,
                distanceMeters=nearby.distance_meters,
                createdAt=now,
            )
        )
        for nearby in nearby_devices
    ]


def respond_to_alert(
    repository: InMemorySupportAlertRepository,
    alert_id: UUID,
    response: SupportStatus,
    now: datetime | None = None,
) -> SupportAlert:
    alert = repository.get(alert_id)
    allowed = {
        "pending": {"checking", "available", "unavailable"},
        "checking": {"available", "unavailable"},
    }
    if response not in allowed.get(alert.status, set()):
        raise ValueError(f"cannot change support response from {alert.status} to {response}")
    updated = alert.model_copy(
        update={
            "status": response,
            "responded_at": now or datetime.now(timezone.utc),
        }
    )
    return repository.replace(updated)

