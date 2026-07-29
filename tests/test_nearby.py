from datetime import datetime, timedelta, timezone

from backend.app.schemas import DeviceRead, Location
from backend.app.services.nearby import find_nearby_devices


NOW = datetime(2026, 8, 1, tzinfo=timezone.utc)
ORIGIN = Location(latitude=36.3012, longitude=127.5874)


def device(
    device_id: str,
    latitude: float,
    *,
    online: bool = True,
    age_seconds: int = 0,
    speed_kph: float = 0,
) -> DeviceRead:
    return DeviceRead(
        deviceId=device_id,
        displayName=device_id,
        deviceType="tractor",
        registeredAt=NOW,
        lastSeenAt=NOW - timedelta(seconds=age_seconds),
        online=online,
        location=Location(
            latitude=latitude,
            longitude=ORIGIN.longitude,
            speedKph=speed_kph,
        ),
    )


def test_selects_only_eligible_devices_within_one_kilometer() -> None:
    devices = [
        device("incident-device", 36.3012),
        device("near-1", 36.303),
        device("near-2", 36.307),
        device("outside", 36.32),
        device("offline", 36.302, online=False),
        device("stale", 36.302, age_seconds=121),
        device("moving-fast", 36.302, speed_kph=21),
    ]
    matches = find_nearby_devices(
        devices,
        source_device_id="incident-device",
        incident_location=ORIGIN,
        now=NOW,
    )
    assert [match.device.device_id for match in matches] == ["near-1", "near-2"]
    assert matches[0].distance_meters < matches[1].distance_meters

